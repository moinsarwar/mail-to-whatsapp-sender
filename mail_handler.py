import os
from imap_tools import MailBox, AND
from dotenv import load_dotenv

load_dotenv()

EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")

def fetch_unread_emails():
    """
    Connects to the IMAP server and fetches unread emails.
    Returns a list of dictionaries containing email details.
    """
    if not EMAIL_ACCOUNT or not EMAIL_PASSWORD:
        raise ValueError("Email credentials are not set in the environment variables.")

    unread_emails = []
    
    try:
        # Connect to the mailbox
        with MailBox(IMAP_SERVER).login(EMAIL_ACCOUNT, EMAIL_PASSWORD) as mailbox:
            # Fetch unread emails
            for msg in mailbox.fetch(AND(seen=False)):
                # Build sender string: "Name <email>" if name exists, else just email
                sender_name = msg.from_values.name.strip() if msg.from_values.name else ""
                sender_email = msg.from_values.email.strip() if msg.from_values.email else msg.from_
                
                if sender_name:
                    full_sender = f"{sender_name} <{sender_email}>"
                else:
                    full_sender = sender_email
                
                email_data = {
                    'uid': msg.uid,
                    'subject': msg.subject,
                    'sender': full_sender,
                    'sender_email': sender_email,
                    'sender_name': sender_name or sender_email,
                    'body': msg.text or msg.html,   # for AI processing
                    'html': msg.html,               # for PDF rendering
                    'text': msg.text,               # plain text fallback
                    'date': msg.date
                }
                unread_emails.append(email_data)
                
            return unread_emails
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []

def mark_as_read(email_uids):
    """
    Marks a list of email UIDs as read.
    """
    if not email_uids:
        return
        
    try:
        with MailBox(IMAP_SERVER).login(EMAIL_ACCOUNT, EMAIL_PASSWORD) as mailbox:
            mailbox.flag(email_uids, '\\Seen', True)
    except Exception as e:
        print(f"Error marking emails as read: {e}")
