import platform
import os
import sys

SYSTEM = platform.system()
IS_WINDOWS = SYSTEM == "Windows" or sys.platform.startswith("win")
IS_MAC = SYSTEM == "Darwin" or sys.platform == "darwin"
IS_LINUX = SYSTEM == "Linux"


def system_name():
    return SYSTEM


def shutdown():
    if IS_LINUX:
        os.system("shutdown now")
    elif IS_WINDOWS:
        os.system("shutdown /s /t 0")
    elif IS_MAC:
        os.system("sudo shutdown -h now")


def reboot():
    if IS_LINUX:
        os.system("reboot")
    elif IS_WINDOWS:
        os.system("shutdown /r /t 0")
    elif IS_MAC:
        os.system("sudo reboot")
