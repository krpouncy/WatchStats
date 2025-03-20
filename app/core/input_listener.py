import ctypes  # TODO consider using another library like (inputs or pynput) instead of 'keyboard' (DOESN"T WORK)
import time
import traceback

import eventlet

from .game_manager import game_manager
from .state import app_state


# XInput structures and constants
class XinputGamepad(ctypes.Structure):
    _fields_ = [
        ("wButtons", ctypes.c_ushort),
        ("bLeftTrigger", ctypes.c_ubyte),
        ("bRightTrigger", ctypes.c_ubyte),
        ("sThumbLX", ctypes.c_short),
        ("sThumbLY", ctypes.c_short),
        ("sThumbRX", ctypes.c_short),
        ("sThumbRY", ctypes.c_short),
    ]


class XinputState(ctypes.Structure):
    _fields_ = [
        ("dwPacketNumber", ctypes.c_ulong),
        ("Gamepad", XinputGamepad)
    ]


XINPUT_GAMEPAD_BACK = 0x0020
VK_TAB = 0x09


def get_controller_state(controller_id=0):
    """Get the state of a controller"""
    state = XinputState()
    try:
        result = ctypes.windll.xinput1_4.XInputGetState(controller_id, ctypes.byref(state))
    except AttributeError:
        result = ctypes.windll.xinput1_3.XInputGetState(controller_id, ctypes.byref(state))
    if result == 0:
        return state
    else:
        return None


def is_key_pressed(vk_code):
    """Check if a specific key is pressed."""
    return ctypes.windll.user32.GetAsyncKeyState(vk_code) & 0x8000


def input_listener():
    """Listen for input events."""
    print("Input listener started")

    # Initialize the next available screenshot time to 0
    app_state.next_screenshot_time = 0
    holding_back = False

    while True:
        try:
            current_time = time.time()
            # For PC input
            if app_state.input_type == "PC":
                if is_key_pressed(VK_TAB):
                    # Check if screenshot delay has passed
                    if current_time >= app_state.next_screenshot_time:
                        print("Taking screenshot...")
                        game_manager.process_screenshot()
                        # Update next available time based on the delay (convert ms to seconds)
                        app_state.next_screenshot_time = current_time + app_state.screenshot_delay
                    else:
                        # Optionally, you can log that screenshot is not available yet
                        pass

            # For Controller input
            if app_state.input_type == "Controller":
                state = get_controller_state(0)  # Replace with your controller state check
                if state:
                    buttons = state.Gamepad.wButtons
                    if buttons & XINPUT_GAMEPAD_BACK:  # Adjust for specific controller buttons
                        if not holding_back and current_time >= app_state.next_screenshot_time:
                            holding_back = True
                            print("Taking screenshot...")
                            game_manager.process_screenshot()
                            app_state.next_screenshot_time = current_time + app_state.screenshot_delay
                    else:
                        holding_back = False

        except Exception as e:
            print(f"Error in input listener: {e}")
            traceback.print_exc()

        eventlet.sleep(0.1)
