from __future__ import annotations

import json

from collections.abc import Mapping
from types import SimpleNamespace
from typing import TYPE_CHECKING
from warbler.constant import CWD

if TYPE_CHECKING:
    from pathlib import Path
    from typing_extensions import Any, Self


def resolve(relative: str) -> Settings:
    path = CWD.joinpath(relative)
    return Settings.from_file(path)


class Settings(SimpleNamespace):
    def __init__(self, **data: Any):
        super().__init__(**data)

    def __getitem__(self, k: Any):
        if k not in self.__dict__:
            self.__dict__[k] = Settings()

        return self.__dict__[k]

    def __setitem__(self, k: Any, v: Any):
        if isinstance(v, Mapping):
            v = Settings(**v)
            self.__dict__.setdefault(k, v)
        else:
            self.__dict__[k] = v

    def __repr__(self):
        return repr(self.__dict__)

    @classmethod
    def deserialize(cls: type[Self], data: str) -> Self:
        settings = json.loads(data)
        return cls(**settings)

    @classmethod
    def from_dict(cls: type[Self], data: dict[str, Any]) -> Self:
        return cls(**data)

    @classmethod
    def from_file(cls: type[Self], path: str | Path) -> Self:
        with open(path, 'r') as handle:
            data = json.load(handle)
            return cls(**data)

    @classmethod
    def from_object(cls: type[Self], data: object) -> Self:
        return cls(**data.__dict__)

    def update(self, data: dict[str, Any]) -> None:
        for k in data:
            if k in self.__dict__:
                self.__dict__[k] = data[k]

    def save(self, path: str | Path) -> None:
        with open(path, 'w+') as file:
            json.dump(
                self.__dict__,
                file,
                indent=4
            )

    def serialize(self) -> str:
        return json.dumps(self.__dict__)