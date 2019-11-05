import pytest
from ezmonitor.notification import slack, mail

GOOD_CONFIG = {
    "database": {"user": "USER", "password": "PASSWORD", "db": "DATABASE"},
    "notification": {
        "slack": {"token": "TOKEN",
                   "channel": "CHANNEL"},
         "email": {"sender": "test@example.com", "sender_password": "TEST",
                   "receiver": "receiver@exampple.com"}
        }
    }

GOOD_PARTIAL_CONFIG = {
      "database": {"user": "USER", "password": "PASSWORD", "db": "DATABASE"},
    "notification": {
    }  
}

BAD_CONFIG = {
    "database": {"user": "USER", "password": "PASSWORD", "db": "DATABASE"},
    "notification": {
        "slack": None,
        "email": None
        }
    }

def test_get_slack_config():
    expected = {"token": "TOKEN", "channel": "CHANNEL"}
    assert all(v == expected[k] for k, v in slack.get_config(GOOD_CONFIG).items())

def test_check_slack_config():
    """"Test function responsible for checking Slack config
    """
    assert slack.check_config(GOOD_CONFIG) == True
    assert slack.check_config(GOOD_PARTIAL_CONFIG) == False
    assert slack.check_config(BAD_CONFIG) == False

def test_get_email_config():
    expected = {"sender": "test@example.com", "sender_password": "TEST",
                   "receiver": "receiver@exampple.com"}
    assert all(v == expected[k] for k, v in mail.get_config(GOOD_CONFIG).items())   

def test_check_email_config():
    """"Test function responsible for checking Email config
    """
    assert mail.check_config(GOOD_CONFIG) == True
    assert mail.check_config(GOOD_PARTIAL_CONFIG) == False
    assert mail.check_config(BAD_CONFIG) == False

# TODO: Find a way to test sender functions with Mocking