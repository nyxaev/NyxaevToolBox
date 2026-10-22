# NYXAEV Toolbox

A local web panel served by Python's built-in `http.server`, with the whole page embedded in a single script. No Flask, no FastAPI, no `pip install`.

**Author:** NYXAEV

## What's inside

| Tool                 | What it does                                                                      |
|----------------------|-----------------------------------------------------------------------------------|
| Password generator   | Secure passwords via `secrets`, with length, character sets, look-alike filter and an entropy estimate |
| UUID generator       | Versions 4, 1, 3 and 5, with uppercase and hyphen options and one-click copy      |
| JSON workbench       | Format, minify or validate, with sorted keys, custom indent and exact error line and column |

## Highlights

- Standard library only (`http.server`, `json`, `secrets`, `uuid`, `argparse`)
- Binds to `127.0.0.1` only, so nothing is exposed to your network
- Host header check and `application/json` requirement on the API
- Falls back to the next free port when the preferred one is busy
- Dark, responsive single-screen interface

## Project structure

```
nyxaev-toolbox/
├── toolbox.py     server, API logic and embedded HTML page
├── README.md
└── .gitignore
```

## How to run

From the terminal:

```bash
python toolbox.py
```

Your browser opens at `http://127.0.0.1:8765`. Press `Ctrl+C` to stop.

In PyCharm: open the folder, right-click `toolbox.py` and choose **Run 'toolbox'**.

### Options

| Flag           | Description                         | Default |
|----------------|-------------------------------------|---------|
| `--port`       | Preferred port                      | `8765`  |
| `--no-browser` | Do not open the browser on start    | off     |

```bash
python toolbox.py --port 9000 --no-browser
```

## API

All routes accept and return JSON.

| Method | Route            | Purpose                      |
|--------|------------------|------------------------------|
| GET    | `/`              | The web panel                |
| GET    | `/health`        | Health check                 |
| POST   | `/api/password`  | Generate passwords           |
| POST   | `/api/uuid`      | Generate UUIDs               |
| POST   | `/api/json`      | Format, minify or validate   |

Example:

```bash
curl -s http://127.0.0.1:8765/api/uuid \
  -H "Content-Type: application/json" \
  -d '{"version": "4", "count": 3}'
```

## Requirements

Python 3.8 or newer. Nothing else.

---

Made by NYXAEV
