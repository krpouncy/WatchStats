import os
import uuid
from concurrent.futures import ThreadPoolExecutor

import cv2
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models
from torchvision import transforms

import pytesseract
from tqdm import tqdm

from app.core.db_manager import (
    save_game_data,
    save_snapshot_data,
    save_team_data
)

from app.core.image_utils import generate_sub_images

SECTION_BOUNDS = [
    (275, 339),
    (339, 394),
    (394, 455),
    (455, 569),
    (569, 655),
    (655, None)  # None implies it goes to the end of the array
]

TESSERACT_NUMERIC_CONFIG = "--psm 6 -c tessedit_char_whitelist=0123456789"

class ImageParser:
    def __init__(self, model_path=None, class_names=None, batch_size=32):
        """
        :param model_path: Path to a pre-trained PyTorch model (.pth file).
        :param class_names: Optional list of strings for model output classification.
        :param batch_size: Number of images to process in a single batch during inference.
        """
        # Default hero labels if none are provided
        if class_names is None:
            self.class_names = [
                'label_Ana', 'label_Ashe', 'label_Baptiste', 'label_Bastion', 'label_Brigitte', 'label_Cassidy',
                'label_DVa', 'label_Doomfist', 'label_Echo', 'label_Genji', 'label_Hanzo', 'label_Hazard', 'label_Hidden',
                'label_Illari', 'label_Junker_Queen', 'label_Junkrat', 'label_Juno', 'label_Kiriko',
                'label_Lifeweaver', 'label_Lucio', 'label_Mauga', 'label_Mei', 'label_Mercy', 'label_Moira',
                'label_Orisa', 'label_Pharah', 'label_Ramattra', 'label_Reaper', 'label_Reinhardt', 'label_Roadhog',
                'label_Sigma', 'label_Sojourn', 'label_Soldier_76', 'label_Sombra', 'label_Symmetra', 'label_Torbjorn',
                'label_Tracer', 'label_Venture', 'label_Widowmaker', 'label_Winston', 'label_Wrecking_Ball',
                'label_Zarya', 'label_Zenyatta'
            ]
        else:
            self.class_names = class_names

        self.device = None
        self.model = None
        self.batch_size = batch_size

        # Load the model if a path is specified
        if model_path is not None:
            # Device configuration
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            print(f'Using device: {self.device}')

            # Initialize the model architecture (ResNet50)
            self.model = models.resnet50(weights=None)

            # Modify the final layer to match the number of classes
            self.model.fc = nn.Sequential(
                nn.Linear(self.model.fc.in_features, 256),
                nn.ReLU(),
                nn.Dropout(0.5),
                nn.Linear(256, len(self.class_names))
            )

            # Load the saved model weights
            try:
                self.model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
                self.model = self.model.to(self.device)
                self.model.eval()  # Set to evaluation mode
                print("Model loaded and set to evaluation mode.")
            except Exception as e:
                print(f"Error loading the model: {e}")
                self.model = None
        else:
            self.model = None

        # Define the preprocessing transforms (must match training transforms)
        self.preprocess = transforms.Compose([
            transforms.Resize((224, 224)),  # Resize to match model input
            transforms.ToTensor()  # Convert PIL Image to tensor
            # transforms.Normalize(mean=[0.485, 0.456, 0.406],  # ImageNet mean
            #                      std=[0.229, 0.224, 0.225])   # ImageNet std
        ])

    def classify_images(self, images, skip_enemy=False):
        """
        Given a list of images (NumPy arrays), run inference using the loaded model and return two lists
        (my_team, enemy_team) each with classification labels.

        :param images: List of NumPy arrays representing the profile images.
        :param skip_enemy: If True, only return the first 5 labels (my_team).
        :return: A list with two sub-lists of predicted labels [team1, team2].
        """
        if not self.model:
            tqdm.write("No model loaded; skipping classification.")
            return [[], []]

        # Convert list of images to PIL Images
        pil_images = [self._convert_cv2_to_pil(img) for img in images]

        # Apply preprocessing transforms
        input_tensors = [self.preprocess(img) for img in pil_images]

        # Create a batch tensor
        input_batch = torch.stack(input_tensors).to(self.device)

        # Perform inference
        with torch.no_grad():
            outputs = self.model(input_batch)  # Shape: [batch_size, num_classes]
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            predicted_class_idxs = torch.argmax(probabilities, dim=1).cpu().numpy()
            confidences = torch.max(probabilities, dim=1).values.cpu().numpy()

        # Convert class indices to class names
        # predicted_classes = [self.class_names[idx] for idx in predicted_class_idxs]

        predicted_classes = [
            self.class_names[idx] if confidence >= 0.9 else 'label_Hidden'
            for idx, confidence in zip(predicted_class_idxs, confidences)
        ]

        # # Debugging: Print the probabilities and predicted class names
        # for idx, (prob, predicted_class, confidence) in enumerate(
        #         zip(probabilities.cpu().numpy(), predicted_classes, confidences)):
        #     print(f"Image {idx + 1}:")
        #     print(f"  Predicted class: {predicted_class}")
        #     print(f"  Confidence: {confidence * 100:.2f}%")
        #     print(f"  Probabilities: {prob}")
        #     print("-" * 50)

        # Split into two teams (5 players each)
        team_1 = predicted_classes[:5]

        if skip_enemy:
            return [team_1, None]
        else:
            team_2 = predicted_classes[5:]
            return [team_1, team_2]

    @staticmethod
    def _convert_cv2_to_pil(cv2_image):
        """
        Convert a CV2 image (BGR) to PIL Image (RGB).

        :param cv2_image: NumPy array representing the image in BGR format.
        :return: PIL Image in RGB format.
        """
        rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        return pil_image

    @staticmethod
    def convert_to_gray(image):
        """
        Convert an image (NumPy array) to grayscale. If it's already single-channel,
        just return it.

        :param image: NumPy array representing the image.
        :return: Grayscale image as NumPy array.
        """
        if len(image.shape) == 2 or image.shape[-1] == 1:
            return image
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def ocr_extract_numeric_text(gray_image):
        """
        Extract numeric text from a grayscale image via Tesseract OCR.
        Strips out whitespace and newlines.

        :param gray_image: Grayscale image as NumPy array.
        :return: Extracted numeric text as string.
        """
        text = pytesseract.image_to_string(
            gray_image, config=TESSERACT_NUMERIC_CONFIG
        )
        return text.replace(' ', '').replace('\n', '')

    def extract_text_from_stats(self, stat_images, return_empty=True):
        """
        Extract text from a list of stat_images. Each stat_image is sliced according
        to SECTION_BOUNDS, and extracted in parallel.

        :param stat_images: List of images (NumPy arrays) to be processed.
        :param return_empty: If False, skip images where all sections are empty.
        :return: A list of lists. Each sub-list corresponds to one stat_image.
        """
        extracted_texts = []

        with ThreadPoolExecutor() as executor:
            for image in stat_images:
                # Slice into sections
                sections = [
                    image[:, start:end] if end else image[:, start:]
                    for (start, end) in SECTION_BOUNDS
                ]

                # Schedule tasks to convert to grayscale + OCR
                futures = [
                    executor.submit(
                        self.ocr_extract_numeric_text,
                        self.convert_to_gray(section)
                    )
                    for section in sections
                ]

                # Gather results
                section_texts = [f.result() for f in futures]

                # Optionally skip if all sections are empty
                if not return_empty and all(text == '' for text in section_texts):
                    continue

                extracted_texts.append(section_texts)

        return extracted_texts

    @staticmethod
    def get_header_info(image_path):
        """
        Extract text from the top region of the image (e.g., scoreboard header).

        :param image_path: Path to the image file.
        :return: Extracted header text as string or None if extraction fails.
        """
        image = cv2.imread(image_path)
        if image is None:
            tqdm.write(f"Error reading image: {image_path}")
            return None
        header_image = image[:100, 120:750]
        try:
            header_text = pytesseract.image_to_string(header_image)
            return header_text.strip()
        except pytesseract.TesseractError as e:
            tqdm.write(f"Error processing header image in {image_path}: {e}")
            return None

    @staticmethod
    def any_row_missing(teams, stats):
        """
        Check if there's a row with 'label_Hidden' and excessive missing data.

        :param teams: List of team labels (e.g., ['label_Ana', 'label_Hidden', ...]).
        :param stats: List of stats corresponding to each player.
        :return: True if any 'label_Hidden' has 4 or more missing stats, else False.
        """
        for player, stat in zip(teams, stats):
            if player == "label_Hidden" and stat.count('') >= 4:
                return True
        return False

    @staticmethod
    def save_image(img, _dir="hidden"):
        """
        Save an image for future reference or training data if the label is 'Hidden'.

        :param img: Image as NumPy array.
        :param _dir: Directory to save the image.
        """
        os.makedirs(_dir, exist_ok=True)
        hidden_image_path = os.path.join(_dir, f"{uuid.uuid4().hex[:8]}.png")
        cv2.imwrite(hidden_image_path, img)

    def process_directory(self, directories, current_directory):
        """
        Process a single directory that contains multiple Overwatch images.
        Steps:
          1) Load the first image, parse out game outcome, possibly skip if outcome is 'left'.
          2) For each image, parse the scoreboard.
          3) Save the data to the DB (game, snapshot, team).

        :param directories: Root directory containing game subdirectories.
        :param current_directory: Name of the current subdirectory to process.
        """
        path_to_dir = os.path.join(directories, current_directory)
        image_files = [
            file for file in os.listdir(path_to_dir)
            if os.path.isfile(os.path.join(path_to_dir, file))
        ]

        if not image_files:
            tqdm.write(f"No image files found in directory: {current_directory}")
            return

        # Skip if there are fewer than 3 images
        if len(image_files) < 3:
            tqdm.write(f"Skipping directory {current_directory} due to insufficient images.")
            return

        # Derive game outcome from directory name
        # e.g., "someprefix_win_somesuffix" => outcome = "win"
        #       "someprefix_left_somesuffix" => outcome = "left"
        parts = current_directory.split("_")
        if len(parts) < 2:
            tqdm.write(f"Unable to determine game outcome from directory name: {current_directory}")
            return
        game_outcome = parts[1]
        # If the user left the game, skip it entirely
        if game_outcome == 'left':
            return

        # Read the first image to get the game header
        first_image_path = os.path.join(path_to_dir, image_files[0])
        header_text = self.get_header_info(first_image_path)
        game_id = save_game_data(header_text, game_outcome)

        first_snapshot = True

        # Loop through all images in this directory
        for image_name in tqdm(image_files, desc=f"Processing Images in {current_directory}", unit="image"):
            image_path = os.path.join(path_to_dir, image_name)

            # If we've already used a header_text, try to extract it again
            # to ensure each snapshot has the right info (or None)
            if not first_snapshot:
                header_text = self.get_header_info(image_path)
                if header_text is None:
                    continue

            # Generate sub-images (one row per player)
            sub_images = generate_sub_images(image_path)

            # Separate profile from stats columns
            profile_images = [sub_image[:, :91] for sub_image in sub_images]
            stat_images = [sub_image[:, 91:] for sub_image in sub_images]

            # Classify heroes
            my_team, enemy_team = self.classify_images(profile_images)

            # Extract stats
            stats = self.extract_text_from_stats(stat_images)

            # If row missing too much data and is "Hidden"
            if self.any_row_missing([*my_team, *enemy_team], stats):
                if first_snapshot:
                    stats = [['0', '0', '0', '0', '0', '0'] for _ in range(10)]
                else:
                    tqdm.write(f"Warning: Image missing data in directory {current_directory}. Skipping.")
                    continue

            snapshot_id = save_snapshot_data(game_id, header_text)

            # Save to DB (per team)
            for i, team in enumerate([my_team, enemy_team]):
                team_stats = stats[5 * i: 5 * (i + 1)]
                if len(team_stats) != 5:
                    tqdm.write(f"Warning: Unexpected number of stats for team {i} in directory {current_directory}. Skipping this team.")
                    continue

                # Zip the profile images, player labels, and stats for each row
                for img, player, stat in zip(profile_images, team, team_stats):
                    if player == "label_Hidden":
                        self.save_image(img)
                    save_team_data(snapshot_id, player, ', '.join(stat), i)

            first_snapshot = False

    def process_game_images(self, directories):
        """
        Orchestrate processing across multiple subdirectories in the given 'directories' path.
        Uses a ThreadPoolExecutor to parallelize across subdirectories.

        :param directories: Root directory containing game subdirectories.
        """
        with ThreadPoolExecutor(max_workers=12) as executor:
            # Loop over subdirectories
            for entry in tqdm(os.scandir(directories), desc="Reading Directories", unit=" dir(s)"):
                if entry.is_dir():
                    executor.submit(self.process_directory, directories, entry.name)