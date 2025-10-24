# About

This project aims to compile questions from a number printscreen of questions using ocr. The images are save in `files/` folder and intermediate processing images are saved on `output/debug` if debug mode is set "True".

To visualize the results use marimo notebooks.

## how to run

Edit a file named 'config.ini' with content

```ini
[DEFAULT]
debug=false
```

please refer to template.ini. Then run these commands:

```bash
uv sync
uv run main.py files
```
