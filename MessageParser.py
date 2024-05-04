import base64
from datetime import datetime
from enum import Enum, auto

from WordsList import WordsList


class ApplicationStatus(Enum):
    UNKNOWN = auto()
    ERROR = auto()
    IGNORE = auto()
    APPLIED = auto()
    ADVANCED = auto()
    REJECTED = auto()


def _contains(text, words):
    text = text.lower()
    return any(word.lower() in text.replace('\n', ' ') for word in words)


class MessageParser:

    def __init__(self, message, words_list: WordsList):
        self.message = message
        self.words_list = words_list
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

        # Check if the date string contains timezone information
        if "(" in date_string and ")" in date_string:
            date_string = date_string[:-6]
        date_format = "%a, %d %b %Y %H:%M:%S %z"

        # Parse the date string into a datetime object
        return datetime.strptime(date_string, date_format)

    applied_words = ["will carefully review", "will review", "are a strong match for the role",
                     "will contact you if your skills", "if you're selected to move forward",
                     "application has been received", "If your profile is a good fit"]
    ignored_words = ["apply@hirewithnear.com", "team@hi.wellfound.com", "contato@geekhunter.com.br", "jobs-noreply@linkedin.com"]

    def _body_contains(self, words):
        return _contains(self.body, words)

    def _sender_contains(self, words):
        return _contains(self.sender, words)

    @property
    def status(self) -> ApplicationStatus:
        if self._body_contains(self.words_list.words("rejected")):
            return ApplicationStatus.REJECTED
        elif self._body_contains(self.words_list.words("applied")):
            return ApplicationStatus.APPLIED
        elif self._body_contains(self.words_list.words("advanced")):
            return ApplicationStatus.ADVANCED
        elif self._sender_contains(self.words_list.words("ignored")):
            return ApplicationStatus.IGNORE
        print("***" * 10)
        print(self.sender)
        print(self.body)
        print(self.message)
        print("***" * 10)
        return ApplicationStatus.UNKNOWN
