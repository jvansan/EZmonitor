import datetime
import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Union

import yaml

from ezmonitor.db import Website, WebsiteList

__default_confg = Path("config.yaml")
log = logging.getLogger('tornado.application')


def load_config(path: Path = __default_confg) -> dict:
    try:
        with open(path) as fil:
            config = yaml.safe_load(fil)
    except (OSError, FileNotFoundError) as e:
        raise e
    finally:
        return config


def json_encoder(res: Union[Website, WebsiteList], indent: int=None) -> str:
    log.debug(res)
    if not res:
        return json.dumps(res, indent=indent)
    if isinstance(res, list):
        result = [asdict(r) for r in res]
    else:
        result = asdict(res)
    return json.dumps(result, indent=indent, default=json_converter)


def json_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def datetime_in_n_seconds(n: int) -> datetime.datetime:
    return datetime.datetime.now()+datetime.timedelta(seconds=n)
