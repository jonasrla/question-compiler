"""Define class for image processing."""
import os
import pathlib
from collections import namedtuple
import logging

import pytesseract
from PIL import Image, ImageFilter
import numpy as np

logger = logging.getLogger(__name__)

def debug_decorator(step_name=''):
    """Decorator to enable debug mode for image processing methods."""
    def decorator(func):
        def wrapper(self, data, *args, **kwargs):
            try:
                result = func(self, data, *args, **kwargs)
            except Exception as e:
                logger.error("Error occurred while processing %s in %s: %s",
                             step_name,
                             data.file_path,
                             e)
                data.image.show()
                raise
            if self.debug:
                debug_image = result.image.copy()
                os.makedirs(
                    os.path.join(self.output,
                                 'debug',
                                 step_name,
                                 str(result.file_path.parent)),
                    exist_ok=True)
                debug_image.save(
                    os.path.join(self.output,
                                    'debug',
                                    step_name,
                                    str(result.file_path))
                )
            return result
        return wrapper
    return decorator

Data = namedtuple('Data', ['image', 'file_name', 'file_path'])

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
        file_path = pathlib.Path(path).relative_to(pathlib.Path(path).parts[0])
        return Data(image=image, file_name=file_name, file_path=file_path)

    @debug_decorator('cropped')
    def crop_question(self, data: Data) -> Data:
        """Crop the image to the region containing the question."""
        cropped_image = data.image.crop(self.crop_box)
        return Data(image=cropped_image,
                    file_name=data.file_name,
                    file_path=data.file_path)

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
        question_array = np.array(data.image)

        question_box_limit = np.argmax((question_array.min(axis=2) > 254).sum(axis=1) > 1500)

        text_left_limit = np.argmax(
            (question_array[:question_box_limit, :, :].max(axis=2) < 40).sum(axis=0) > 0
        )

        image_limit = np.argmax(
            (question_array[:question_box_limit, text_left_limit:, :].min(axis=2) > 254) \
                .sum(axis=0) > 0
        )

        if image_limit > 0:
            text_right_limit = np.argmax(
                (
                    np.flip(
                        question_array[:question_box_limit, text_left_limit:image_limit, :],
                        axis=1
                    ) \
                    .max(axis=2) < 40
                ) \
                    .sum(axis=0) > 0
            )

            text_right_limit = image_limit - text_right_limit
        else:
            text_right_limit = np.argmax(
                (np.flip(
                    question_array[:question_box_limit, text_left_limit:, :],
                    axis=1
                ) \
                    .max(axis=2) < 40
                ) \
                    .sum(axis=0) > 0
            )
            text_right_limit = question_array.shape[1] - text_right_limit
        question_box = data.image.crop((
            text_left_limit-5,
             0,
             text_right_limit + 5,
             question_box_limit
        ))

        data = Data(image=question_box,
                    file_name=data.file_name,
                    file_path=data.file_path)
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
                    file_path=data.file_path)
        return data

    def check_correct(self, data: Data) -> bool:
        """Check if the extracted answer is correct."""
        img_array = np.array(data.image)
        red = img_array[:, :, 0]
        green = img_array[:, :, 1]
        blue = img_array[:, :, 2]
        red_dominant = (red > green*1.2) & (red > blue*1.2)
        if np.sum(red_dominant) > 100:
            return False
        return True
