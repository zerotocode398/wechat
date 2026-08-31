import collections

import yaml

from app.log import logger
from app.utils import Dict2Obj
from app.icode import *


class Config(Dict2Obj):
    def __init__(self, filepath):
        try:
            self.data = collections.defaultdict(dict)
            data = yaml.safe_load(open(filepath, "r", encoding="utf-8"))
            self.data.update(data)
            super().__init__(self.data)
            logger.debug(f"config loaded: {filepath}")

        except FileNotFoundError:
            raise CustomException(config_file_not_found)

        except (yaml.YAMLError, ValueError, TypeError) as e:
            raise CustomException(config_file_parse_error, str(e))
