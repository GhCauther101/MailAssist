from imap_tools import MailBox, AND
from typing import TypedDict

class ChatState(TypedDict):
    messages: list

def connect(host, user, password, folder="INBOX"):

    if not host:
        raise ValueError("IMAP_HOST is missing.")

    if not user:
        raise ValueError("IMAP_USER is missing.")

    if not password:
        raise ValueError("IMAP_PASSWORD is missing.")

    print(f"Connecting to IMAP server: {host}:993")

    try:

        mailbox = MailBox(
            host=host,
            port=993,
            timeout=30
        )

        # IMPORTANT: Use positional arguments
        mailbox.login(user, password, initial_folder=folder)

        print("IMAP connection successful!")

        return mailbox

    except Exception as e:

        print(f"IMAP connection failed: {type(e).__name__}: {e}")
        raise