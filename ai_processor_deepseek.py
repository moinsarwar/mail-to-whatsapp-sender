import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def extract_actionable_tasks(email_body, sender="Unknown"):
    if not DEEPSEEK_API_KEY:
        print("❌ DeepSeek API key is not set in .env file.")
        return None

    system_instruction = (
        "You are a smart personal assistant reading emails on behalf of your boss.\n"
        "You will be given the sender's name/email and the email content.\n"
        "Read the email carefully. Then respond in one of two ways:\n\n"
        "CASE 1 - If the email has tasks, actions or requests:\n"
        "📧 *What's this email about?*\n"
        "(1-2 sentences. ALWAYS use the actual sender name/email provided, NOT 'The sender'. Example: 'Ali has requested...' or 'moinsarwar19@gmail.com is asking...')\n\n"
        "✅ *Tasks:*\n"
        "• Task 1\n"
        "• Task 2\n"
        "(Use bullet points • for each task)\n\n"
        "CASE 2 - If it's a simple informational/newsletter/notification email with nothing to do:\n"
        "📧 *What's this email about?*\n"
        "(1-2 sentences using the actual sender name. No tasks section needed.)\n\n"
        "RULES:\n"
        "- NEVER write 'The sender'. Always use the actual name or email address given.\n"
        "- Always use bullet point • for tasks\n"
        "- Ignore all URLs, tracking links, unsubscribe links\n"
        "- Be short and direct. No repetition."
    )

    url = "https://api.deepseek.com/anthropic/v1/messages"
    headers = {
        "x-api-key": DEEPSEEK_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-v4-flash",
        "max_tokens": 1024,
        "system": system_instruction,
        "messages": [
            {"role": "user", "content": f"Sender: {sender}\n\nEmail content:\n{email_body}"}
        ]
    }

    try:
        print("Attempting extraction with DeepSeek (Anthropic API)...")
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            print(f"  -> Failed: DeepSeek API Error {response.status_code}: {response.text}")
            return None
        result = response.json()
        # DeepSeek Anthropic may return multiple content blocks (thinking + text)
        # Find the one with type='text'
        for block in result.get('content', []):
            if block.get('type') == 'text':
                return block['text'].strip()
        print("  -> Failed: No text block found in response")
        return None
    except Exception as e:
        print(f"  -> Failed: {e}")
        return None
