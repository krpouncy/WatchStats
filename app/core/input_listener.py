import os
import eventlet
# Set the environment variable before any other imports
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE" # TODO workaround to issue about libiomp5md.dll
# TODO CRITICAL ISSUE DETAILED INCLUDED
# OMP: Error #15: Initializing libiomp5md.dll, but found libiomp5md.dll already initialized.
# OMP: Hint This means that multiple copies of the OpenMP runtime have been linked into the program. That is dangerous, since it can degrade performance or cause incorrect results. The best thing to do is to ensure that only a single OpenMP runtime is linked into the process, e.g. by avoiding static linking of the OpenMP runtime in any library. As an unsafe, unsupported, undocumented workaround you can set the environment variable KMP_DUPLICATE_LIB_OK=TRUE to allow the program to continue to execute, but that may cause crashes or silently produce incorrect results. For more information, please see http://www.intel.com/software/products/support/.

import ctypes # TODO consider using another library like (inputs or pynput) instead of keyboard (DOESN"T WORK)
from app.core.state import app_state
from app.core.classification import process_screenshot

import traceback

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
    print("Input listener started")

    holding_back = False

    while True:
        try:
            if app_state.input_type == "PC":
                if is_key_pressed(VK_TAB):
                    print("Taking screenshot...")
                    process_screenshot()
                    eventlet.sleep(0.5)  # Prevent spamming

            if app_state.input_type == "Controller":
                state = get_controller_state(0)  # Replace with your controller state check
                if state:
                    buttons = state.Gamepad.wButtons
                    if buttons & XINPUT_GAMEPAD_BACK:  # Adjust for specific controller buttons
                        if not holding_back:
                            holding_back = True
                            print("Taking screenshot...")
                            process_screenshot()
                    else:
                        holding_back = False

        except Exception as e:
            print(f"Error in input listener: {e}")
            traceback.print_exc()

        eventlet.sleep(0.1)