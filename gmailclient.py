from googleapiclient.discovery import build

from MailInfo import MailInfo
from MessageParser import ApplicationStatus
from WordsList import WordsList
from credentials import obtain_access_token


class GmailClient:
    def __init__(self):
        self.service = build('gmail', 'v1', credentials=obtain_access_token())
        self.mail_info = MailInfo(WordsList())

    def _get_label_id(self, label_name):

        try:
            # List messages with the specified label
            response = self.service.users().labels().list(userId='me').execute()
            labels = response.get('labels', [])
            label = next((item for item in labels if item.get("name") == label_name), None)
            return label["id"] if label else None
        except Exception as e:
            print("An error occurred:", e)

        return None

    def _list_messages_with_label(self, label_id, max):
        all_messages = []

        try:
            # Initialize next_page_token to None to start pagination
            next_page_token = None

            while True:
                # List messages with the specified label and page token
                response = self.service.users().messages().list(userId='me', labelIds=[label_id],
                                                                pageToken=next_page_token).execute()
                messages = response.get('messages', [])

                # Add retrieved messages to the list
                if messages:
                    all_messages.extend(messages)

                # Check if there are more pages
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break  # No more pages, exit the loop

            message_info = []
            for message in all_messages:
                message_data = self.service.users().messages().get(userId="me", id=message["id"]).execute()
                message_info.append(self.mail_info.get_info(message_data))
                if max and len(message_info) >= max:
                    break

            return message_info

        except Exception as e:
            print("An error occurred:", e)
            return []

    def list_messages_with_label_name(self, label_name, max):
        label_id = self._get_label_id(label_name)
        return self._list_messages_with_label(label_id, max)


# Example usage
if __name__ == '__main__':
    # List messages with the specified label
    messages = GmailClient().list_messages_with_label_name("Job Search", 50)
    print("Number of messages:", len(messages))
    for status in ApplicationStatus:
        print(f"Number of : {status.name}",
              len([message for message in messages if message["status"] == status]))
