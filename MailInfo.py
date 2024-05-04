from MessageParser import MessageParser, ApplicationStatus


class MailInfo:
    def __init__(self, words_list):
        self.words_list = words_list

    def get_info(self, message: dict) -> dict:
        parser = MessageParser(message, self.words_list)
        try:
            info = {"subject": parser.subject,
                    "body": parser.body,
                    "date": parser.date,
                    "sender": parser.sender,
                    "status": parser.status}
        except Exception as e:
            info = {"error": e, "status": ApplicationStatus.ERROR}
        return info
