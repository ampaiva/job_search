import base64
from datetime import datetime
from enum import Enum, auto


class ApplicationStatus(Enum):
    UNKNOWN = auto()
    ERROR = auto()
    IGNORE = auto()
    APPLIED = auto()
    REJECTED = auto()


def _contains(text, words):
    text = text.lower()
    return any(word.lower() in text for word in words)


class MessageParser:

    def __init__(self, message):
        self.message = message
        self._body = None
        self._sender = None

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
        if not self._sender:
            self._sender = self._get_header("Sender") or self._get_header("From")
        return self._sender

    @property
    def date(self) -> datetime:
        date_string = self._get_header("Date")
        date_format = "%a, %d %b %Y %H:%M:%S %z"
        if "(" in date_string and ")" in date_string:
            date_format = "%a, %d %b %Y %H:%M:%S %z (%Z)"

        # Parse the date string into a datetime object
        return datetime.strptime(date_string, date_format)

    rejections_words = ["Though", "regret", "although", "not to continue", "time and energy you invested",
                        "after carefully", "você não seguirá"]
    applied_words = ["will carefully review", "will review", "are a strong match for the role", "will contact you if your skills"]
    ignored_words = ["apply@hirewithnear.com", "team@hi.wellfound.com", "contato@geekhunter.com.br", "jobs-noreply@linkedin.com"]

    def _body_contains(self, words):
        return _contains(self.body, words)

    def _sender_contains(self, words):
        return _contains(self.sender, words)

    @property
    def status(self) -> ApplicationStatus:
        if self._body_contains(self.rejections_words):
            return ApplicationStatus.REJECTED
        elif self._body_contains(self.applied_words):
            return ApplicationStatus.APPLIED
        elif self._sender_contains(self.ignored_words):
            return ApplicationStatus.IGNORE
        print("***" * 10)
        print(self.sender)
        print(self.body)
        print(self.message)
        print("***" * 10)
        return ApplicationStatus.UNKNOWN
