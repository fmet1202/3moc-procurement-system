import os
import json
import html
import urllib.request

# No fallback credentials: an exposed default here means a leaked token can
# never fully be "removed from code" since it's still baked into the file.
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def _esc(value):
    """Escape user-supplied text before embedding it in an HTML-parsed
    Telegram message, so a submitted RFQ can't break formatting or inject
    markup into the notification."""
    return html.escape(str(value)) if value else value


def send_telegram_rfq_alert(sub):
    """
    Sends an instant HTML-formatted notification to Telegram
    whenever a client submits a quote request.
    """
    if not BOT_TOKEN or not CHAT_ID:
        print("[Telegram Bot] Skipped: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set.")
        return False

    message_text = (
        f"🚨 <b>NEW TENDER RFQ RECEIVED — 3 MOC</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏛 <b>Organization:</b> {_esc(sub.organization)}\n"
        f"👤 <b>Contact Person:</b> {_esc(sub.contact_name)}\n"
        f"📞 <b>Phone:</b> <a href='tel:{_esc(sub.phone)}'>{_esc(sub.phone)}</a>\n"
        f"✉️ <b>Email:</b> {_esc(sub.email) or 'N/A'}\n"
        f"🏷 <b>Tender Ref:</b> <code>{_esc(sub.tender_ref) or 'Direct Request'}</code>\n"
        f"📦 <b>Target Lots:</b> {_esc(sub.selected_lots) or 'General'}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 <b>Specifications / Items:</b>\n"
        f"<i>{_esc(sub.message)}</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 <a href='https://threemoc.onrender.com/admin/submissions'>Open Admin Console to Review & Quote</a>"
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=6) as response:
            if response.status == 200:
                print(f"[Telegram Bot] Alert sent for {sub.organization}!")
                return True
    except Exception as e:
        print(f"[Telegram Bot] Warning - failed to send alert: {e}")

    return False