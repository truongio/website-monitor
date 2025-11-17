from .handlers import setup_handlers


def run_bot():
    from .main import run_bot as _run_bot
    return _run_bot()


__all__ = ['setup_handlers', 'run_bot']
