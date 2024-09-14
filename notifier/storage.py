import json
import os

class Storage:
    def __init__(self, filename='notified_concerts.json'):
        self.filename = filename
        self._ensure_file_exists()

    # Ensure the file exists
    def _ensure_file_exists(self):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump({}, f)  # Empty JSON object to start

    # Load notified concerts from file
    def load_notified_concerts(self):
        with open(self.filename, 'r') as f:
            return json.load(f)

    # Save notified concerts to file
    def save_notified_concerts(self, notified_concerts):
        with open(self.filename, 'w') as f:
            json.dump(notified_concerts, f, indent=4)

    # Check if a concert has already been notified
    def is_concert_notified(self, chat_id, concert_id):
        notified_concerts = self.load_notified_concerts()
        if str(chat_id) in notified_concerts:
            return concert_id in notified_concerts[str(chat_id)]
        return False

    # Mark a concert as notified
    def mark_concert_as_notified(self, chat_id, concert_id):
        notified_concerts = self.load_notified_concerts()
        if str(chat_id) not in notified_concerts:
            notified_concerts[str(chat_id)] = []
        notified_concerts[str(chat_id)].append(concert_id)
        self.save_notified_concerts(notified_concerts)
