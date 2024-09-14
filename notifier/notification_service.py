import time
import threading
import queue
import logging
from telebot import TeleBot
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants for rate limiting
MESSAGE_LIMIT = 30  # Telegram limit: 30 messages per second to different users
MESSAGE_SLEEP_TIME = 1.1  # Slightly over 1 second to avoid 1 msg per second limit in a chat
MAX_MESSAGES_PER_SECOND = 30

class NotificationService:
    def __init__(self):
        self.bot = TeleBot(TELEGRAM_BOT_TOKEN)
        self.message_queue = queue.Queue()  # Thread-safe queue to store messages
        self.logger = logging.getLogger(__name__)

        # Start a background worker to process the queue
        self.worker_thread = threading.Thread(target=self._process_queue)
        self.worker_thread.daemon = True  # Daemon thread will exit when the program exits
        self.worker_thread.start()

    def send_notification(self, message, chat_id):
        """
        Adds a message to the queue for processing.
        """
        full_message = message
        self.message_queue.put((full_message, chat_id))
        self.logger.debug(f"Message added to queue for chat_id: {chat_id}")

    def _process_queue(self):
        """
        Worker function that processes the message queue and sends messages while respecting Telegram's limits.
        """
        last_message_time = time.time()
        messages_sent_in_second = 0

        while True:
            try:
                # Block until there is a message to process
                message, chat_id = self.message_queue.get()

                # If more than one second has passed, reset the counter
                current_time = time.time()
                if current_time - last_message_time >= 1:
                    messages_sent_in_second = 0
                    last_message_time = current_time

                # Check if we hit the per-second limit
                if messages_sent_in_second >= MAX_MESSAGES_PER_SECOND:
                    self.logger.info(f"Rate limit hit: sleeping for 1 second")
                    time.sleep(1)  # Sleep to avoid hitting the rate limit
                    messages_sent_in_second = 0

                # Send the message to the subscriber
                self.bot.send_message(chat_id, message, parse_mode='Markdown')
                self.logger.info(f"Sent message to chat_id: {chat_id}")

                # Track the number of messages sent in this second
                messages_sent_in_second += 1

                # Make sure to sleep for a short time to respect the "1 message per second per chat" limit
                time.sleep(MESSAGE_SLEEP_TIME)

                # Mark the message as processed
                self.message_queue.task_done()

            except Exception as e:
                self.logger.error(f"Error while sending message: {e}")
                time.sleep(1)  # Sleep for a second to avoid spamming retries in case of errors
