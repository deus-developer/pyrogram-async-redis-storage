import random
import string

import pytest

from pyrogram_async_redis_storage.accessor import (
    BoolValue,
    BytesValue,
    IntValue,
    StrValue,
    Undefined,
    undefined,
)


@pytest.mark.parametrize(
    "value",
    [random.randint(-(2**63), 2**63 - 1) for _ in range(100)],
)
def test_int_value_fuzzing(value: int) -> None:
    packed = IntValue.pack(value)
    unpacked = IntValue.unpack(packed)
    assert unpacked == value


@pytest.mark.parametrize("value", [True, False])
def test_bool_value_fuzzing(value: bool) -> None:  # noqa: FBT001
    packed = BoolValue.pack(value)
    unpacked = BoolValue.unpack(packed)
    assert unpacked is value


def test_bool_value_invalid_unpack() -> None:
    with pytest.raises(ValueError, match="Invalid value: 0x78"):
        BoolValue.unpack(b"x")


@pytest.mark.parametrize(
    "value",
    [
        "".join(
            random.choices(
                string.ascii_letters + string.digits,
                k=random.randint(0, 100),
            ),
        )
        for _ in range(100)
    ],
)
def test_str_value_fuzzing(value: str) -> None:
    packed = StrValue.pack(value)
    unpacked = StrValue.unpack(packed)
    assert unpacked == value


@pytest.mark.parametrize(
    "value",
    [
        bytes(random.getrandbits(8) for _ in range(random.randint(0, 100)))
        for _ in range(100)
    ],
)
def test_bytes_value_fuzzing(value: bytes) -> None:
    packed = BytesValue.pack(value)
    unpacked = BytesValue.unpack(packed)
    assert unpacked == value


def test_undefined_instance() -> None:
    assert isinstance(undefined, Undefined)
