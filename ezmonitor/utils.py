import datetime
import json
from pathlib import Path
from typing import Union

import yaml

from ezmonitor.db import Website, WebsiteList

__default_confg = Path("config.yaml")

def load_config(path: Path = __default_confg) -> dict:
    try:
        with open(path) as fil:
            config = yaml.safe_load(fil)
    except (OSError, FileNotFoundError) as e:
        raise e
    finally:
        return config


def json_encoder(res: Union[Website, WebsiteList], indent: int=None) -> str:
    if not res:
        return json.dumps(res, indent=indent)
    if isinstance(res, list):
        result = [r._asdict() for r in res]
        for rs in result:
            rs['results'] = [r._asdict() for r in rs['results']]
    else:
        result = res._asdict()
        result['results'] = [r._asdict() for r in result['results']]
    return json.dumps(result, indent=indent, default=json_converter)


def json_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()
