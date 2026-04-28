import os
import requests
from dotenv import load_dotenv

load_dotenv()

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID")

# Support multiple recipients: comma-separated list
# Works with both YOUR_WHATSAPP_NUMBERS and old YOUR_WHATSAPP_NUMBER
_numbers_raw = os.getenv("YOUR_WHATSAPP_NUMBERS", os.getenv("YOUR_WHATSAPP_NUMBER", ""))
WHATSAPP_RECIPIENTS = [n.strip().replace("+", "") for n in _numbers_raw.split(",") if n.strip()]


def _api_url():
    return f"https://graph.facebook.com/v25.0/{META_PHONE_NUMBER_ID}/messages"

def _auth_headers():
    return {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }


def send_whatsapp_message(message_body):
    """
    Sends a WhatsApp text message to ALL recipients in YOUR_WHATSAPP_NUMBERS.
    """
    if not all([META_ACCESS_TOKEN, META_PHONE_NUMBER_ID]) or not WHATSAPP_RECIPIENTS:
        print("Meta WhatsApp credentials are not fully set.")
        return None

    for number in WHATSAPP_RECIPIENTS:
        try:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {"preview_url": False, "body": message_body}
            }
            response = requests.post(_api_url(), headers=_auth_headers(), json=data)
            if response.status_code == 200:
                print(f"Message sent to {number} ✅")
            else:
                print(f"Error sending to {number}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error sending to {number}: {e}")


def upload_whatsapp_media(file_path):
    """
    Uploads a file to Meta's media endpoint and returns the media_id.
    """
    if not all([META_ACCESS_TOKEN, META_PHONE_NUMBER_ID]):
        print("Meta credentials not set.")
        return None

    url = f"https://graph.facebook.com/v25.0/{META_PHONE_NUMBER_ID}/media"
    headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}"}

    try:
        with open(file_path, 'rb') as f:
            files = {
                'file': (os.path.basename(file_path), f, 'application/pdf'),
                'messaging_product': (None, 'whatsapp'),
                'type': (None, 'application/pdf')
            }
            response = requests.post(url, headers=headers, files=files)

        if response.status_code == 200:
            return response.json().get('id')
        else:
            print(f"Error uploading PDF: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error uploading media: {e}")
        return None


def send_whatsapp_document(media_id, filename, caption=""):
    """
    Sends a document (PDF) via WhatsApp to ALL recipients.
    """
    if not all([META_ACCESS_TOKEN, META_PHONE_NUMBER_ID]) or not WHATSAPP_RECIPIENTS:
        print("Meta WhatsApp credentials are not fully set.")
        return None

    for number in WHATSAPP_RECIPIENTS:
        try:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "type": "document",
                "document": {
                    "id": media_id,
                    "filename": filename,
                    "caption": caption
                }
            }
            response = requests.post(_api_url(), headers=_auth_headers(), json=data)
            if response.status_code == 200:
                print(f"PDF sent to {number} ✅")
            else:
                print(f"Error sending PDF to {number}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error sending PDF to {number}: {e}")
