import base64
import resend
from .config import settings

def send_receipt_and_signature(email: str, signature_html: str, session_id: str):
    resend_key = settings.RESEND_API_KEY
    if not resend_key or "Mock" in resend_key:
        print(f"[EMAIL MOCK/TEST] Email send simulated for {email}. Session: {session_id}")
        return {"success": True, "simulated": True}

    resend.api_key = resend_key
    from_email = "SigHub <onboarding@resend.dev>"
    subject = "Your SigHub Email Signature is Ready!"
    return_link = f"{settings.BASE_URL}/builder.html?session_id={session_id}"

    text_content = f"""Thank you for your purchase from SigHub ($1.99)!

Access your signature anytime using your permanent purchase link:
{return_link}

Order Session ID: {session_id}

Your signature is also attached to this email as signature.html.
"""

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 4px solid #000; box-shadow: 4px 4px 0 #000;">
      <h1 style="text-transform: uppercase; font-weight: 900;">SigHub Receipt & Signature</h1>
      <p style="font-size: 16px;">Thank you for your purchase ($1.99)! Your custom email signature is attached to this email.</p>
      
      <div style="margin: 20px 0; padding: 15px; background: #fffde7; border: 2px solid #000;">
        <strong>Order Reference:</strong> {session_id}<br/>
        <strong>Status:</strong> Paid & Verified<br/><br/>
        <strong>Permanent Access Link:</strong><br/>
        <a href="{return_link}" style="color: #000; font-weight: bold; text-decoration: underline;">{return_link}</a>
      </div>

      <p>Click the link above anytime to load and export your unlocked signature directly in SigHub.</p>
      <hr style="border: 2px solid #000; margin: 20px 0;"/>
      <p style="font-size: 12px; color: #666;">SigHub — Modern Email Signature Builder</p>
    </div>
    """

    attachment_bytes = (signature_html or "").encode("utf-8")
    attachment_b64 = base64.b64encode(attachment_bytes).decode("utf-8")

    params = {
        "from": from_email,
        "to": [email],
        "subject": subject,
        "text": text_content,
        "html": html_content,
        "attachments": [
            {
                "filename": "signature.html",
                "content": attachment_b64
            }
        ]
    }

    try:
        r = resend.Emails.send(params)
        print(f"[EMAIL SENT] Successfully sent to {email}")
        return {"success": True, "data": r}
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email to {email}: {e}")
        return {"success": False, "error": str(e)}
