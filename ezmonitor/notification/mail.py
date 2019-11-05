import aiosmtplib
from ezmonitor.utils import first

EMAIL_TEMPLATE = """\
From: {sender}
To: {receiver}
Subject: {subject}

{body}
"""

def get_config(config: dict) -> dict:
    """Take app config and return Email config"""
    notification_config = config.get("notification", [])
    try:
        return first(notification_config, lambda x: x.get("email")).get("email")
    except StopIteration:
        return {}


def check_config(config: dict) -> bool:
    """Check the application config for necessary Email credentials
    
    Parse the config dictionary which should come form `config.yaml` or similar
    """
    mail_config = get_config(config)
    return bool(mail_config.get("sender")) and \
        bool(mail_config.get("sender_password")) and \
        bool(mail_config.get("receiver"))


async def send_message(config: dict, message: str) -> None:
    if not check_config(config):
        raise Exception("Missing configuration")
    mail_config = get_config(config)
    email = EMAIL_TEMPLATE.format(
        sender=mail_config.get("sender"),
        receiver=mail_config.get("receiver"),
        subject="Message from EZmonitor",
        body=message
        )
    await aiosmtplib.send(
        email,
        sender=mail_config.get("sender"),
        recipients=[mail_config.get("receiver")],
        hostname="smtp.gmail.com", port=465, use_tls=True,
        username=mail_config.get("sender"),
        password=mail_config.get("sender_password")
    )