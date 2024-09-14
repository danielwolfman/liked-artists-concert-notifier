import logging
import requests
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.token = TELEGRAM_BOT_TOKEN

    # Send a notification to the given chat_id
    def send_notification(self, message, chat_id):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {
            "chat_id": chat_id,  # The specific chat ID of the subscriber
            "text": message,
            "parse_mode": "Markdown",
        }
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            logger.info(f"Notification sent to chat ID {chat_id}")
        else:
            logger.error(f"Failed to send notification to chat ID {chat_id}: {response.status_code}")
        
        return response.status_code == 200
