"""Exam preparation tests' questions compiler"""
import argparse
import configparser
import os
import logging

from PIL import Image

from image_processor import ImageProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
"""This executable load, preprocess, analyse and compile a \
sequence of test questions print screens""")
parser.add_argument(
    'src',
    help="""Folder path containing images. Supported file extensions: \
.png, .jpg, .jpeg, .tiff, .bmp""")
parser.add_argument(
    '--config',
    help='Path to configuration file',
    default='config.ini')
args = parser.parse_args()

def get_files_list(directory):
    """Get a sorted list of image files in the specified directory."""
    files_list = os.listdir(directory)
    files_list = sorted(files_list)
    return [os.path.join(directory, f)
            for f in files_list
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp'))]

def parse_config(config_path):
    """Parse configuration file."""
    # Implement configuration parsing logic here
    if config_path is not None and os.path.isfile(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        return {
            'output_dir': config.get('DEFAULT', 'output_dir', fallback='output'),
            'debug': config.getboolean('DEFAULT', 'debug', fallback=False),
            'crop_box': tuple(map(int,
                                  config.get('DEFAULT',
                                             'crop_box',
                                             fallback='420,740,2500,1600').split(',')))
        }
    if not os.path.isfile(config_path):
        logger.warning('Config file %s not found. Using default parameters.',
                       config_path)
    return {}

image_processor_arguments = parse_config(args.config)
image_processor = ImageProcessor(**image_processor_arguments)

for path in get_files_list(args.src):
    image = Image.open(path).convert('RGB')
    crop_image = image_processor.crop_question(image)
    east_box = image_processor.detect_text_boxes(crop_image)
    question = image_processor.extract_question(crop_image, east_box)
    right_answer = image_processor.filter_green_text(crop_image)
