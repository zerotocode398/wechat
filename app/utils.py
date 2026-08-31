from typing import Any, List, Union


class Dict2Obj(object):
    """
    Returns: dict -> obj
    """

    def __init__(self, map_):
        self.map_ = map_

    def __getattr__(self, name) -> Union["Dict2Obj", List[Any], Any]:
        val = self.map_.get(name)
        if isinstance(val, dict):
            return Dict2Obj(val)
        elif isinstance(val, list):
            return [item for item in val]
        else:
            return self.map_.get(name)

    def __str__(self) -> str:
        return str(self.map_)

    def __getitem__(self, key: Any) -> Any:
        return self.map_[key]

    def get(self, key: Any, default: Any = None) -> Any:
        val = self.map_.get(key, default)
        if isinstance(val, dict):
            return Dict2Obj(val)
        elif isinstance(val, list):
            return [item for item in val]
        return val
