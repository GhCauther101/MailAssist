import os
import imaplib
import utils
import json
import imaplib
import email
from imap_tools import AND
from dotenv import load_dotenv
from envar import *
# load_dotenv()

# IMAP_HOST = os.getenv('IMAP_HOST')
# IMAP_USER = os.getenv('IMAP_USER')
# IMAP_PASSWORD = os.getenv('IMAP_PASSWORD')
# IMAP_FOLDER = 'INBOX'

# OLLAMA_URL = os.getenv('OLLAMA_URL')

def fetch_unread_emails():
    # Connect to IMAP server
    mail = imaplib.IMAP4_SSL(IMAP_HOST)
    mail.login(IMAP_USER, IMAP_PASSWORD)

    # Select inbox
    mail.select(IMAP_FOLDER)

    # Search for unread emails
    status, messages = mail.search(None, "UNSEEN")

    email_ids = messages[0].split()

    results = []

    for e_id in email_ids:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        raw_email = msg_data[0][1]

        msg = email.message_from_bytes(raw_email)

        subject = msg["subject"]
        sender = msg["from"]

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")

        results.append({
            "from": sender,
            "subject": subject,
            "body": body.strip()
        })

    mail.logout()
    return results

def fetch_all_emails():
    unread = []
    with utils.connect(host=IMAP_HOST, user=IMAP_USER, password=IMAP_PASSWORD) as mb:
        unread = list(mb.fetch(criteria=AND(seen=False), headers_only=True, mark_seen=False))

    if not unread:
        return 'you have no unread messages.'
    
    response = json.dumps([{
        'uid':int(mail.uid),
        'date':mail.date.astimezone().strftime('%Y-%m-%D %H:%M'),
        'subject': mail.subject,
        'sender':mail.from_
    } for mail in unread ])
