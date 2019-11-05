import slack
from ezmonitor.utils import first

def check_config(config: dict) -> bool:
    """Check the application config for Slack App credentials
    
    Parse the config dictionary which should come form `config.yaml` or similar
    """
    slack_config = get_config(config)
    return bool(slack_config.get("token")) and bool(slack_config.get("channel"))


def get_config(config: dict) -> dict:
    """Take app config and return Slack config"""
    notification_config = config.get("notification", [])
    try:
        return first(notification_config, lambda x: x.get("slack")).get("slack")
    except StopIteration:
        return {}


def connect_slack(config: dict) -> slack.WebClient:
    client = slack.WebClient(
        token=get_config(config).get("token"),
        run_async=True
    )
    return client


async def send_message(config: dict, message: str) -> None:
    if not check_config(config):
        raise Exception("Missing configuration")
    client = connect_slack(config)
    resp = await client.chat_postMessage(
        channel="#"+get_config(config).get("channel"),
        text=message
    )
    assert resp['ok']
