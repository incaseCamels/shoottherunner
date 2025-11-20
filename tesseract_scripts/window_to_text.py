import pygetwindow as gw
import pyautogui
import pytesseract
import cv2
import time
import os
import sys
from PIL import Image

# Set path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def list_windows():
    visible_windows = [w for w in gw.getAllWindows() if w.visible and w.title.strip()]
    if not visible_windows:
        print("No visible windows found.")
        sys.exit(1)

    print("Open Windows:")
    for i, win in enumerate(visible_windows):
        print(f"{i}: {win.title}")
    return visible_windows

def screenshot_and_ocr(win):
    win.restore()
    win.activate()
    time.sleep(1.5)  # Allow time for rendering

    bbox = (win.left, win.top, win.width, win.height)
    screenshot = pyautogui.screenshot(region=bbox)
    screenshot.save("window_capture.png")

    img = cv2.imread("window_capture.png")
    if img is None:
        raise Exception("Failed to load screenshot image.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)[1]
    cv2.imwrite("processed.png", thresh)

    text = pytesseract.image_to_string(Image.open("processed.png"), config="--psm 6")
    print("\nOCR Output:\n")
    print(text if text.strip() else "[No text detected]")

if __name__ == "__main__":
    windows = list_windows()

    try:
        selection = int(input("\nEnter the number of the window to capture: "))
        if selection < 0 or selection >= len(windows):
            raise ValueError("Invalid selection.")
        screenshot_and_ocr(windows[selection])
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
