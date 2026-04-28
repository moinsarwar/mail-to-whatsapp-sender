import os
import re
import time
from mail_handler import fetch_unread_emails, mark_as_read
# from ai_processor import extract_actionable_tasks  # Gemini + HuggingFace fallback
from ai_processor_deepseek import extract_actionable_tasks  # DeepSeek only
from whatsapp_sender import send_whatsapp_message, upload_whatsapp_media, send_whatsapp_document
from pdf_generator import generate_email_pdf

def get_sender_name(sender_raw):
    """
    Extract display name from sender string.
    'Moin Sarwar <moinsarwar19@gmail.com>' -> 'Moin Sarwar'
    'moinsarwar19@gmail.com' -> 'moinsarwar19@gmail.com'
    """
    match = re.match(r'^(.+?)\s*<.+>$', sender_raw.strip())
    if match:
        name = match.group(1).strip().strip('"')
        return name if name else sender_raw
    return sender_raw

def process_emails():
    print("Checking for new emails...")
    unread_emails = fetch_unread_emails()
    
    if not unread_emails:
        print("No new unread emails.")
        return
        
    processed_uids = []
    
    for email in unread_emails:
        print(f"\nProcessing email from {email['sender']} - Subject: {email['subject']}")
        
        if not email['body'] or len(email['body'].strip()) == 0:
            print("  [SKIP] Empty email body, skipping.")
            processed_uids.append(email['uid'])
            continue
            
        # Extract sender display name (already parsed by mail_handler)
        sender_name = email.get('sender_name', email['sender'])
        
        # Extract tasks using LLM
        tasks = extract_actionable_tasks(email['body'], sender=sender_name)
        
        # Check if AI successfully returned a response
        if tasks:
            ai_text = tasks
        else:
            # Fallback: send raw body (truncated)
            raw_body = email['body'].strip()
            if len(raw_body) > 1500:
                raw_body = raw_body[:1500] + "\n...[truncated]..."
            ai_text = f"⚠️ AI Analysis failed.\n\n📄 Original:\n{raw_body}"
            
        # Prepare message
        message_body = (
            f"📧 *New Email*\n"
            f"*From:* {email['sender']}\n"
            f"*Subject:* {email['subject']}\n\n"
            f"{ai_text}\n\n"
            f"📎 _Full email attached as PDF below._"
        )

        # Enforce hard limit to prevent Meta API 400 error (4096 max length)
        if len(message_body) > 4000:
            message_body = message_body[:4000] + "\n\n... [Message Truncated]"

        # ── Step 1: Generate PDF first ──────────────────────────────────
        media_id = None
        pdf_path = None
        try:
            print("  [PDF] Generating PDF...")
            pdf_path = generate_email_pdf(email)
            print("  [PDF] Uploading to Meta...")
            media_id = upload_whatsapp_media(pdf_path)
        except Exception as e:
            print(f"  [PDF ERROR] {e}")

        # ── Step 2: Send text message ───────────────────────────────────
        send_whatsapp_message(message_body)

        # ── Step 3: Send PDF immediately after ─────────────────────────
        if media_id:
            subject_safe = email['subject'][:40].replace('/', '-')
            send_whatsapp_document(
                media_id=media_id,
                filename=f"Email - {subject_safe}.pdf",
                caption="📄 Full email content"
            )

        # Cleanup temp file
        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)

        processed_uids.append(email['uid'])
        
    # Mark processed emails as read
    if processed_uids:
        mark_as_read(processed_uids)
        

if __name__ == "__main__":
    try:
        while True:
            process_emails()
            print("\nSleeping for 60 seconds...")
            time.sleep(60) # wait for 60 seconds before checking again
    except KeyboardInterrupt:
        print("\nScript stopped by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
