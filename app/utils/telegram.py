import urllib.request
import json
from flask import current_app
from app.utils.helpers import get_setting_value

def send_telegram_notification(message: str) -> bool:
    """Send a notification to Telegram using the saved bot token and chat ID."""
    try:
        token = get_setting_value("telegram_bot_token")
        chat_id = get_setting_value("telegram_chat_id")
        
        if not token or not chat_id:
            return False
            
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        try:
            current_app.logger.error(f"TELEGRAM NOTIFICATION ERROR: {e}")
        except Exception:
            print(f"TELEGRAM NOTIFICATION ERROR: {e}")
        return False
