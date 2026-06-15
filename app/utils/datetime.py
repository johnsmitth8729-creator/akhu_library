from datetime import datetime

import pytz


APP_TIMEZONE = pytz.timezone("Asia/Tashkent")


def now_local() -> datetime:
    """Return a DB-friendly local timestamp for Asia/Tashkent."""
    return datetime.now(APP_TIMEZONE).replace(tzinfo=None)


def today_local():
    return now_local().date()
