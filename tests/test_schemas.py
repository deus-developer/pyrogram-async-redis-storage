import random

import pytest

from pyrogram_async_redis_storage.schemas import (
    InputPeerChannel,
    InputPeerChat,
    InputPeerUser,
    UpdateState,
    read_input_peer,
    read_update_state,
    write_input_peer,
    write_update_state,
)

MAX_INT64 = 2**63 - 1
MIN_INT64 = -(2**63)


@pytest.mark.parametrize(
    ("peer_type", "chat_id", "access_hash"),
    [
        (
            random.choice(["user", "bot", "group", "supergroup", "channel"]),
            random.randint(MIN_INT64, MAX_INT64),
            random.randint(MIN_INT64, MAX_INT64),
        )
        for _ in range(100)
    ],
)
def test_input_peer_fuzzing(peer_type: str, chat_id: int, access_hash: int) -> None:
    packed = write_input_peer(peer_type, chat_id, access_hash)
    unpacked = read_input_peer(packed)

    if isinstance(unpacked, InputPeerUser):
        assert unpacked.user_id == chat_id
        assert unpacked.access_hash == access_hash

    elif isinstance(unpacked, InputPeerChat):
        assert unpacked.chat_id == -chat_id

    elif isinstance(unpacked, InputPeerChannel):
        assert unpacked.channel_id == -(1000000000000 + chat_id)
        assert unpacked.access_hash == access_hash
    else:
        pytest.fail("Unknown input peer type")


@pytest.mark.parametrize(
    ("state_id", "pts", "qts", "date", "seq"),
    [
        (
            random.randint(MIN_INT64, MAX_INT64),
            random.randint(0, MAX_INT64),
            random.randint(0, MAX_INT64),
            random.randint(0, MAX_INT64),
            random.randint(0, MAX_INT64),
        )
        for _ in range(100)
    ],
)
def test_update_state_fuzzing(
    state_id: int,
    pts: int,
    qts: int,
    date: int,
    seq: int,
) -> None:
    packed = write_update_state(state_id, pts, qts, date, seq)
    unpacked = read_update_state(packed)
    assert unpacked == UpdateState(state_id, pts, qts, date, seq)
