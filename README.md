# 📧 Mail to WhatsApp Sender

A Python application that automatically reads your Gmail inbox, extracts actionable tasks using DeepSeek AI, and sends summaries to WhatsApp.

## Features

- ✅ Reads unread Gmail emails
- ✅ Extracts tasks using **DeepSeek API**
- ✅ Sends summary to WhatsApp
- ✅ Sends full email as PDF attached
- ✅ Supports multiple WhatsApp numbers
- ✅ Marks emails as read after processing
- ✅ Detects simple informational emails and skips task formatting
- ✅ **HTML Email Rendering**: Converts full HTML emails to PDF preserving layout, images, colors, and buttons
- ✅ **Dual-Channel Delivery**: Sends text summary + PDF attachment for complete context

## Prerequisites

- Python 3.7+
- Gmail account with IMAP enabled
- Meta Cloud API access with WhatsApp Business Account
- API keys for:
  - DeepSeek AI (for task extraction)
  - Meta Cloud API (for WhatsApp messages)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd sender
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the same directory and add your credentials:

```env
# Email Configuration
EMAIL_ACCOUNT="moin.seo19@gmail.com"
EMAIL_PASSWORD="YOUR_GMAIL_APP_PASSWORD"
IMAP_SERVER="imap.gmail.com"

# AI Configuration (DeepSeek)
DEEPSEEK_API_KEY="YOUR_DEEPSEEK_API_KEY"

# WhatsApp Configuration (Meta Cloud API)
META_ACCESS_TOKEN="YOUR_META_ACCESS_TOKEN"
META_PHONE_NUMBER_ID="YOUR_PHONE_NUMBER_ID"
YOUR_WHATSAPP_NUMBERS="YOUR_PHONE_NUMBER"
```

> **Note**: Use an **App Password** for Gmail, not your regular login password.

## Usage

Run the script:

```bash
python main.py
```

The script will:
1. Check for unread emails
2. Process each email:
   - Extract tasks with DeepSeek AI
   - Generate PDF from HTML email (if available)
   - Send text summary via WhatsApp
   - Send PDF attachment via WhatsApp
3. Mark processed emails as read
4. Wait for 60 seconds and repeat

## How HTML Email Rendering Works

1. Parses HTML using **BeautifulSoup**
2. Extracts all embedded `<style>` tags and CSS rules
3. Wraps content in a full HTML document with:
   - Custom header containing From, Subject, Date
   - Preserved styles from original email
   - **`print-color-adjust: exact`** CSS to force background colors and images
4. Renders with **WeasyPrint** to PDF
5. Sends text summary + PDF attachment for complete context

## Troubleshooting

### PDF Not Showing Background Colors

Add these CSS rules to your PDF template:

```css
* {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    color-adjust: exact !important;
}
```

### HTML Email Rendering Issues

If some styles aren't rendering, ensure:
- WeasyPrint and BeautifulSoup are correctly installed
- Email HTML is valid (not corrupted)
- CSS is not overly complex or using unsupported properties

### WhatsApp Integration Errors

Check:
- Valid access token with `whatsapp_business_messaging` scope
- Correct phone number ID
- Rate limits (WhatsApp API has daily limits)

## Customization

- Modify `system_instruction` in `ai_processor_deepseek.py` to change AI behavior
- Adjust `process_emails` loop frequency (current: 60 seconds)
- Customize PDF layout in `pdf_generator.py`

## License

MIT
