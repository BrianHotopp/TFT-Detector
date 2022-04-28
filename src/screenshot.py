from PIL import Image
import win32gui
import pyautogui
from ctypes import windll
import argparse
from pathlib import Path
def get_tft_window_screenshot() -> Image.Image:
    window_name = "League of Legends (TM) Client"
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        win32gui.SetForegroundWindow(hwnd)
        x, y, x1, y1 = win32gui.GetClientRect(hwnd)
        x, y = win32gui.ClientToScreen(hwnd, (x, y))
        x1, y1 = win32gui.ClientToScreen(hwnd, (x1 - x, y1 - y))
        im = pyautogui.screenshot(region=(x, y, x1, y1))
        # check that the screenshot is the right size
        if im.size != (1920, 1080):
            im.show()
            raise Exception("Image is not 1920x1080. Dimensions: " + str(im.size))
        return im
    else:
        print('Window not found!')

if __name__ == "__main__":
    # program takes one command line arg - the folder to save the screenshot to
    # by default, it assumes the screenshots in the folder are named sequentially
    # and saves the screenshot to the next available file
    parser = argparse.ArgumentParser(description='Take a screenshot of the League of Legends window.')
    # optional argument to specify the folder to save the screenshot to; defaults to ../screenshots if not specified
    parser.add_argument('-f', '--folder', help='Folder to save the screenshot to.')
    args = parser.parse_args()
    here = Path(__file__).parent
    if args.folder:
        folder = args.folder
    else:
        folder = here/'../screenshots'
    # make sure the folder exists
    folder.mkdir(parents=True, exist_ok=True)

    while True:
        # get the screenshot
        try:
            im = get_tft_window_screenshot()
            # compute the next available file name
            file_name = folder/'{}.png'.format(str(len(list(folder.glob('*.png')))))
            # save the screenshot
            im.save(file_name)
        except Exception as e:
            print(e)
        # wait for the user to press enter
        input("Press enter to take another screenshot")
        print("Screenshot taken")