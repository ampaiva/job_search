import base64
from datetime import datetime
from enum import Enum, auto


class ApplicationStatus(Enum):
    UNKNOWN = auto()
    ERROR = auto()
    APPLIED = auto()
    REJECTED = auto()


class MessageParser:

    def __init__(self, message):
        self.message = message
        self._body = None

    @property
    def body(self):
        """
        Extracts the body contents of an email message.

        Args:
            message: The message object obtained from the Gmail API.

        Returns:
            The decoded body contents of the message.
        """
        if self._body:
            return self._body

        payload = self.message['payload']

        # Check if the message has a multi-part MIME structure
        if 'parts' in payload:
            parts = payload['parts']
            for part in parts:
                if part['mimeType'] == 'text/plain' or part['mimeType'] == 'text/html':
                    # Extract and decode the body
                    body = part['body']['data']
                    self._body = base64.urlsafe_b64decode(body).decode('utf-8')
                    return self._body
        else:
            # Extract and decode the body for single-part MIME structure
            body = payload['body']['data']
            self._body = base64.urlsafe_b64decode(body).decode('utf-8')
            return self._body

    def _get_header(self, name):
        return next((item["value"] for item in self.message["payload"]["headers"] if item.get("name") == name),
                    None)

    @property
    def subject(self) -> str:
        return self._get_header("Subject")

    @property
    def sender(self) -> str:
        return self._get_header("Sender")

    @property
    def date(self) -> datetime:
        date_string = self._get_header("Date")
        date_format = "%a, %d %b %Y %H:%M:%S %z"

        # Parse the date string into a datetime object
        return datetime.strptime(date_string, date_format)

    rejections_words = ["regret", "although"]
    applied_words = ["will review your application"]

    def _body_contains(self, words):
        return any(word in self.body for word in words)

    @property
    def status(self) -> ApplicationStatus:
        if self._body_contains(self.rejections_words):
            return ApplicationStatus.REJECTED
        elif self._body_contains(self.applied_words):
            return ApplicationStatus.APPLIED
        print(self._body)
        return ApplicationStatus.UNKNOWN
