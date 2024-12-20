# Copyright (C) 2024-present Artem Ukolov <deusdeveloper@yandex.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Generic,
    TypeVar,
)

T = TypeVar("T")


class RWValue(ABC, Generic[T]):
    @classmethod
    @abstractmethod
    def pack(cls, value: T) -> bytes:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def unpack(cls, value: bytes) -> T:
        raise NotImplementedError


class IntValue(RWValue[int]):
    @classmethod
    def pack(cls, value: int) -> bytes:
        return int.to_bytes(value, length=8, byteorder="little", signed=True)

    @classmethod
    def unpack(cls, value: bytes) -> int:
        return int.from_bytes(value, byteorder="little", signed=True)


class BoolValue(RWValue[bool]):
    BOOL_TRUE = b"t"
    BOOL_FALSE = b"f"

    @classmethod
    def pack(cls, value: bool) -> bytes:  # noqa: FBT001
        if value:
            return cls.BOOL_TRUE
        return cls.BOOL_FALSE

    @classmethod
    def unpack(cls, value: bytes) -> bool:
        if value == cls.BOOL_TRUE:
            return True
        if value == cls.BOOL_FALSE:
            return False
        raise ValueError(f"Invalid value: 0x{value.hex()}")


class StrValue(RWValue[str]):
    @classmethod
    def pack(cls, value: str) -> bytes:
        return value.encode("utf-8")

    @classmethod
    def unpack(cls, value: bytes) -> str:
        return value.decode("utf-8")


class BytesValue(RWValue[bytes]):
    @classmethod
    def pack(cls, value: bytes) -> bytes:
        return value

    @classmethod
    def unpack(cls, value: bytes) -> bytes:
        return value


class Undefined: ...


undefined = Undefined()
