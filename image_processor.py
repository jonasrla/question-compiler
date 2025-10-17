"""Define class for image processing."""
import pytesseract
from PIL import Image
import numpy as np
import cv2

class ImageProcessor:
    def __init__(self, output_dir='output', crop_box=(420, 740, 2500, 1600),  debug_mode=False):
        self.output_dir = output_dir
        self.debug_mode = debug_mode
        self.crop_box = crop_box

    def crop_question(self, image):
        """Crop the image to the region containing the question."""
        return image.crop(self.crop_box)

    def detect_text_boxes(self, image):
        """Detect text boxes in the image."""
        # Implement text box detection logic here
        return text_boxes

    def extract_question(self, image, text_boxes):
        """Extract the question text from the image."""
        # Implement question extraction logic here
        return question_text

    def filter_green_text(self, image):
        """Filter the image to find the green text (the right answer)."""
        # Implement green text filtering logic here
        return green_text
