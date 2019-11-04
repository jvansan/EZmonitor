import yaml
from pathlib import Path

__default_confg = Path("config.yaml")

def load_config(path: Path = __default_confg) -> dict:
    try:
        with open(path) as fil:
            config = yaml.safe_load(fil)
    except OSError as e:
        config = {}
        raise e
    finally:
        return config
