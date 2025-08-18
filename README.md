# NIMAS Notifier

A small tool to watch a web page for availability numbers and notify you via Telegram when they fall below a threshold.
Currently configured for NIMAS.

---

## Requirements

Before running locally or in CI, make sure you have:

- **Python** ≥ 3.12
- **uv** (package/dependency manager for Python)
  - Install:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    exec $SHELL -l
    ```
- **Playwright browser runtime** (Chromium headless)
  - Will be installed via:
    ```bash
    uv run playwright install chromium
    ```

---

## GitHub Actions Setup

Set these in the repo:

- **Secrets** (Settings → Secrets and variables → Actions → Secrets)

  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_CHAT_ID`

- **Variables** (Settings → Secrets and variables → Actions → Variables)
  - `TARGET_URL` (default points to NIMAS page)
  - `ROW_MATCH` (e.g., `AMC-69`)
  - `THRESHOLD` (e.g., `15`)

---

## Local Development

Clone and set up:

```bash
# Install Python deps and set up pre-commit hooks
uv pip install -e ".[dev]" && uv run pre-commit install

# Install Playwright Chromium runtime (needed for scraping JS-rendered table)
uv run playwright install chromium

# Run the watcher (make sure .env is filled, see .env.example)
uv run python -m app.main
```

### Code Quality Tools

This project uses modern Python development tools:

```bash
# Lint and format code
uv run ruff check --fix && uv run ruff format

# Type checking
uv run mypy app/

# Run all pre-commit hooks manually
uv run pre-commit run --all-files
```

**Note:** Pre-commit hooks run automatically on `git commit` and will:
- Auto-fix linting issues with ruff
- Format code with ruff
- Run type checking with mypy
- Check for trailing whitespace and other issues
