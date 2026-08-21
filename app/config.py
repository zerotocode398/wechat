import collections
import traceback

import yaml

from log import Logger
from utils import Dict2Obj
from ierror import *


class Config(Dict2Obj):
    def __init__(self, filepath):
        try:
            self.data = collections.defaultdict(dict)
            data = yaml.safe_load(open(filepath, "r", encoding="utf-8"))
            self.data.update(data)
            super().__init__(self.data)
        except Exception:
            Logger().fatal(
                CustomException(WXErrorInvalidConfigPath, traceback.format_exc())
            )
