from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
import smtplib
from config import EMAIL_SENDER, EMAIL_SENDER_APP_PASSWORD

agent = smtplib.SMTP_SSL("smtp.gmail.com", 465)
agent.login(EMAIL_SENDER, EMAIL_SENDER_APP_PASSWORD)

def send_email(subject, content, to_addr, mail_type = 'plain'):
    em = MIMEMultipart()
    em["From"] = EMAIL_SENDER
    em["To"] = to_addr
    em["Subject"] = subject
    em.attach(MIMEText(content, mail_type))
    agent.sendmail(EMAIL_SENDER, to_addr, em.as_string())

async def send_signup_notifiction(to_addr:str):
    subject="Account Created at Encrypted-Chat (noreply)"
    content= WELCOME_EMAIL_TEMPLATE
    send_email(to_addr=to_addr, subject=subject, content=content, mail_type='html')
    return True


async def send_verification_email(to_addr: str, user_id: str, base_url: str, verification_id: str):
    subject="[Verify your email] Encrypted-Chat"
    content= VERIFICATION_EMAIL_TEMPLATE.format(user_id=user_id, base_url=base_url, verification_id=verification_id)
    send_email(to_addr=to_addr, subject=subject, content=content, mail_type='html')
    return True


WELCOME_EMAIL_TEMPLATE = '''
<h1>Welcome to Encrypted-Chat (even we can't read your message).</h1>
<h2>Never share your Private Keys with anyone and save it in a Secure place.</h2>

<p>Enjoy your Encrypted Conversations.</p>
'''

VERIFICATION_EMAIL_TEMPLATE = '''
<h1>Hii {user_id}</h1>
<p>Confirm your email by clicking <a href="{base_url}authentication/v/{verification_id}" >here</a></p>
'''