import os
import json
from utils import *
from llm import *
from imap_tools import AND
from langchain_core.tools import tool

IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD")

IMAP_FOLDER = "INBOX"

@tool
def list_unread_emails() -> str:
    """
    Retrieve the latest 15 unread emails from the inbox,
    sorted from newest to oldest.
    """

    print("\n[List Unread Emails] Tool called.")

    try:
        with connect(
            host=IMAP_HOST,
            user=IMAP_USER,
            password=IMAP_PASSWORD,
            folder=IMAP_FOLDER
        ) as mb:
            unread = list(
                mb.fetch(
                    AND(seen=False),
                    headers_only=True,
                    bulk=True,
                    mark_seen=False
                )
            )
            
            print("abc")

        # Sort newest first and keep only 15 emails
        unread.sort(
            key=lambda mail: mail.date.timestamp() if mail.date else 0,
            reverse=True
        )

        unread = unread[:15]

        if not unread:
            return json.dumps({
                "status": "success",
                "count": 0,
                "emails": []
            })

        emails = [
            {
                "uid": int(mail.uid),
                "date": mail.date.astimezone().strftime("%Y-%m-%d %H:%M")
                    if mail.date else "Unknown",
                "subject": mail.subject,
                "sender": mail.from_
            }
            for mail in unread
        ]

        print(f"[List Unread Emails] Retrieved {len(emails)} latest unread emails.")

        return json.dumps({
            "status": "success",
            "count": len(emails),
            "emails": emails
        })

    except Exception as e:
        print("[List Unread Emails] Error:", e)

        return json.dumps({
            "status": "error",
            "message": str(e)
        })

@tool
def summarize_email(uid: int) -> str:
    """
    Retrieve the complete content of an email using its IMAP UID.

    Args:
        uid: The actual numeric UID returned by list_unread_emails.

    Never use placeholder values or invented UIDs.
    """

    print(f"\n[Summarize Email] Tool called with UID: {uid}")

    if not isinstance(uid, int) or uid <= 0:
        return "Invalid UID. Please provide a positive numeric email UID."

    try:

        with connect(
            host=IMAP_HOST,
            user=IMAP_USER,
            password=IMAP_PASSWORD,
            folder=IMAP_FOLDER
        ) as mb:

            mail = next(
                mb.fetch(
                    AND(seen=False),
                    AND(uid=str(uid)),
                    mark_seen=False
                ),
                None
            )

            if not mail:
                return f"No email found with UID {uid}."

            email_body = mail.text or mail.html or "No email body available."
            
            print(email_body)
            email_data = {
                "uid": int(mail.uid),
                "subject": mail.subject,
                "sender": mail.from_,
                "date": str(mail.date),
                "body": email_body
            }

            print("[Summarize Email] Email retrieved successfully.")
            return json.dumps(email_data, default=str)

    except Exception as e:

        print("[Summarize Email] Error:", e)

        return f"Could not retrieve email: {str(e)}"
