import tkinter as tk
from PIL import ImageGrab, Image
import pytesseract
import cv2
import numpy as np

# Set path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class SnipTool:
    def __init__(self):
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", 0.3)
        self.root.configure(bg='black')
        self.canvas = tk.Canvas(self.root, cursor="cross", bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        x1 = int(min(self.start_x, self.canvas.canvasx(event.x)))
        y1 = int(min(self.start_y, self.canvas.canvasy(event.y)))
        x2 = int(max(self.start_x, self.canvas.canvasx(event.x)))
        y2 = int(max(self.start_y, self.canvas.canvasy(event.y)))
        self.root.destroy()
        self.capture_and_ocr(x1, y1, x2, y2)

    def capture_and_ocr(self, x1, y1, x2, y2):
        # Grab screenshot region
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))

        # Convert to OpenCV format
        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # Preprocess with adaptive thresholding
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        pil_img = Image.fromarray(thresh)


        # Convert back to PIL for Tesseract
        pil_img = Image.fromarray(thresh)

        # OCR
        text = pytesseract.image_to_string(pil_img, config="--psm 6")
        print("\nOCR Output:\n")
        print(text if text.strip() else "[No text detected]")

if __name__ == "__main__":
    SnipTool().root.mainloop()
