# About

This project aims to compile questions from a number printscreen of questions using ocr.

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
