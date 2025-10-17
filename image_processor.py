"""Define class for image processing."""
import os
from collections import namedtuple
import logging

import pytesseract
from PIL import Image, ImageFilter
import numpy as np

logger = logging.getLogger(__name__)

def debug_decorator(step_name=''):
    """Decorator to enable debug mode for image processing methods."""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if self.debug:
                debug_image = result.image.copy()
                try:
                    debug_image.save(
                        os.path.join(self.output,
                                     'debug',
                                     step_name,
                                     f"{result.file_name}"))
                except FileNotFoundError as e:
                    logger.warning("Debug directory not found. Creating: %s", e)
                    os.makedirs(
                        os.path.join(self.output,
                                     'debug',
                                     step_name),
                        exist_ok=True)
                    debug_image.save(
                        os.path.join(self.output,
                                     'debug',
                                     step_name,
                                     f"{result.file_name}"))
            return result
        return wrapper
    return decorator

Data = namedtuple('Data', ['image', 'file_name', 'output'])

class ImageProcessor:
    """Class for processing images."""
    def __init__(self, output='output', crop_box=(420, 740, 2500, 1600),  debug=False):
        self.output = output
        self.debug = debug
        self.crop_box = crop_box

    def data_constructor(self, path: str) -> Data:
        """Construct Data namedtuple."""
        image = Image.open(path).convert("RGB")
        file_name = os.path.basename(path)
        output = self.output
        return Data(image=image, file_name=file_name, output=output)

    @debug_decorator('cropped')
    def crop_question(self, data: Data) -> Data:
        """Crop the image to the region containing the question."""
        cropped_image = data.image.crop(self.crop_box)
        return Data(image=cropped_image,
                    file_name=data.file_name,
                    output=data.output)

    def _get_text(self, data: Data) -> str:
        """Extract text from the image using OCR."""
        return pytesseract.image_to_string(data.image, lang='por')

    def extract_question(self, data: Data) -> str:
        """Extract the question text from the image."""
        filtered_data = self._filter_question(data)
        text = self._get_text(filtered_data).replace('\n', ' ').strip()
        return text

    @debug_decorator('filtered_question')
    def _filter_question(self, data: Data) -> Data:
        """Filter the image to enhance question text visibility."""
        img_array = np.array(data.image)
        red = img_array[:, :, 0]
        green = img_array[:, :, 1]
        blue = img_array[:, :, 2]
        gray_shades = ((green < 255) & (green > 230)) & \
                        ((red < 255) & (red > 230)) & \
                        ((blue < 255) & (blue > 230))
        gray_line = gray_shades.sum(axis=1) > (0.6 * gray_shades.shape[1])
        blue_dominated = (blue > red) & (blue > green)
        img_array[~gray_line, :] = [255, 255, 255]
        img_array[blue_dominated] = [255, 255, 255]
        filtered_image = Image.fromarray(img_array)
        data = Data(image=filtered_image,
                    file_name=data.file_name,
                    output=data.output)
        return data

    def extract_answer(self, data: Data) -> str:
        """Extract the answer text from the image."""
        filtered_data = self._filter_answer(data)
        text = self._get_text(filtered_data).replace('\n', ' ').strip()
        return text

    @debug_decorator('filtered_answer')
    def _filter_answer(self, data: Data) -> Data:
        """Filter the image to enhance answer text visibility."""
        img_array = np.array(data.image)

        red = img_array[:, :, 0]
        green = img_array[:, :, 1]
        blue = img_array[:, :, 2]
        green_dominant = (green > red) & (green > blue)

        max_rb = np.maximum(red, blue)
        min_rb = np.minimum(red, blue)
        similar_rb = (max_rb - min_rb) <= (0.1 * max_rb)

        mask = green_dominant & similar_rb

        green_text_img = np.zeros_like(img_array)
        green_text_img[mask] = [255, 255, 255]

        green_image = Image.fromarray(green_text_img)
        ghost_filter = ImageFilter.MedianFilter(size=5)

        green_image = green_image.filter(ghost_filter)
        data = Data(image=green_image,
                    file_name=data.file_name,
                    output=data.output)
        return data
