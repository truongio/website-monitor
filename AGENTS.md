# Repository Guidelines

## Project Structure & Module Organization
Core bot logic lives in `bot/` (`main.py` defines the Telegram entrypoint and `handlers.py` wires commands). Monitoring, parsing, and change detection utilities sit in `monitor/` with `checker.py` and `content_cleaner.py` orchestrating crawl logic. Database helpers and SQL migrations are under `database/` alongside helper scripts such as `run_migration.py`. Root-level utilities (`run_monitor.py`, `test_*.py`) let you exercise flows end-to-end.

## Build, Test, and Development Commands
Use Python 3.11 (see `runtime.txt`) and a virtualenv: `python -m venv .venv && source .venv/bin/activate`, then `pip install -r requirements.txt`. Run the Telegram bot via `python -m bot.main` (requires `.env` with `TELEGRAM_BOT_TOKEN` and `DATABASE_URL`). Execute change detection offline with `python run_monitor.py` to mirror the scheduled Action. Apply migrations through `python run_migration.py <file.sql>` before deploying to Supabase.

## Coding Style & Naming Conventions
Follow PEP 8/Black-style formatting: four-space indentation, 88-character lines, and snake_case everywhere. Keep modules cohesive—each class or helper belongs in its own file. Prefer explicit imports (`from monitor.forum_parser import ForumThreadParser`) and guard entrypoints with `if __name__ == "__main__":`. Log short, actionable strings and avoid leaking secrets into stdout.

## Testing Guidelines
Debug harnesses double as smoke tests; run them directly (`python test_forum_parser.py`, `python test_button_with_attributes.py`) after touching selectors or parser logic. For a single pass, run `pytest` so each `test_*.py` script executes under the same interpreter. Name new tests after the behavior under scrutiny and assert both success flags and payload shape to catch regressions. When adjusting monitoring heuristics, capture before/after hashes to document the expected delta.

## Commit & Pull Request Guidelines
History shows short, imperative summaries (e.g., “Enhance selector monitoring to track element state attributes”). Keep subject lines under ~72 characters, describe what changed, and mention the surface area (`bot`, `monitor`) when helpful. Squash work-in-progress commits; each PR should cover a cohesive unit and note any migrations or scripts executed. Reference related issues and attach logs or screenshots if Telegram output diverges from CLI runs.

## Security & Configuration Tips
Never commit populated `.env` files or Telegram tokens. Keep Supabase credentials in local shells plus Render/GitHub secrets, and rotate them at the first sign of leakage. Redact URLs in logs and avoid printing response bodies outside debug scripts. Make migrations idempotent and test them on a staging database before applying to production.
