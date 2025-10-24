import marimo

__generated_with = "0.17.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pytesseract
    from PIL import Image, ImageFilter
    import numpy as np
    return Image, np


@app.cell
def _(Image):
    path = 'files/13-10/renovacao/1-tentativa/q04.png'
    crop_dim = (420, 740, 2440, 1600)
    img = Image.open(path)
    return crop_dim, img


@app.cell
def _(img):
    img
    return


@app.cell
def _(crop_dim, img):
    cropped_img = img.crop(crop_dim)
    cropped_img
    return (cropped_img,)


@app.cell
def _(cropped_img, np):
    question_array = np.array(cropped_img.convert('RGB'))
    white_rows = (question_array.min(axis=2) > 254).sum(axis=1)
    question_box_limit = np.argmax((question_array.min(axis=2) > 254).sum(axis=1) > 1500)

    text_left_limit = np.argmax((question_array[:question_box_limit, :, :].max(axis=2) < 40).sum(axis=0) > 0)

    image_limit = np.argmax((question_array[:question_box_limit, text_left_limit:, :].min(axis=2) > 254).sum(axis=0) > 0)

    if image_limit > 0:
        text_right_limit = np.argmax((np.flip(question_array[:question_box_limit, text_left_limit:image_limit, :], axis=1).max(axis=2) < 40).sum(axis=0) > 0)
        text_right_limit = image_limit - text_right_limit
    else:
        text_right_limit = np.argmax((np.flip(question_array[:question_box_limit, text_left_limit:, :], axis=1).max(axis=2) < 40).sum(axis=0) > 0)
        text_right_limit = question_array.shape[1] - text_right_limit
    rev_question_array = question_array
    # question_number = question_box.crop((text_left_limit-5, 0, question_box.width, question_box.height))
    question_number = cropped_img.crop((text_left_limit-5, 0, text_right_limit, question_box_limit))
    question_number
    return (
        image_limit,
        question_array,
        question_box_limit,
        text_left_limit,
        white_rows,
    )


@app.cell
def _(question_array):
    (question_array.min(axis=2) > 254).sum(axis=1)
    return


@app.cell
def _(white_rows):
    white_rows > 500
    return


@app.cell
def _(question_array, question_box_limit, text_left_limit):
    ((question_array[:question_box_limit, text_left_limit:, :].min(axis=2) > 254).sum(axis=0) > 0).any()
    return


@app.cell
def _(other_array):
    ((other_array.max(axis=2) < 30).sum(axis=0) > 0).any()
    return


@app.cell
def _(other_array, text_left_limit):
    ((other_array[text_left_limit:, :, :].min(axis=2) > 254).sum(axis=0) > 0).any()
    return


@app.cell
def _(image_limit):
    image_limit
    return


@app.cell
def _(text_left_limit):
    text_left_limit
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
