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

import struct
from enum import IntEnum
from typing import NamedTuple

from pyrogram.raw.types import (  # type: ignore[attr-defined]
    InputPeerChannel,
    InputPeerChat,
    InputPeerUser,
)


class PeerType(IntEnum):
    BOT = 1
    USER = 2
    GROUP = 3
    SUPERGROUP = 4
    CHANNEL = 5


InputPeerType = InputPeerUser | InputPeerChat | InputPeerChannel

peer_constructor_by_id: dict[int, type[InputPeerType]] = {
    InputPeerUser.ID: InputPeerUser,
    InputPeerChat.ID: InputPeerChat,
    InputPeerChannel.ID: InputPeerChannel,
}
peer_type_id_by_string: dict[str, PeerType] = {
    "bot": PeerType.BOT,
    "user": PeerType.USER,
    "group": PeerType.GROUP,
    "supergroup": PeerType.SUPERGROUP,
    "channel": PeerType.CHANNEL,
}

InputPeerStruct = struct.Struct("<iqq")


def read_input_peer(value: bytes) -> InputPeerType:
    peer_type_id, chat_id, access_hash = InputPeerStruct.unpack(value)

    if peer_type_id in (PeerType.USER, PeerType.BOT):
        return InputPeerUser(user_id=chat_id, access_hash=access_hash)

    if peer_type_id == PeerType.GROUP:
        return InputPeerChat(chat_id=-chat_id)

    if peer_type_id in (PeerType.CHANNEL, PeerType.SUPERGROUP):
        return InputPeerChannel(
            channel_id=-(1000000000000 + chat_id),
            access_hash=access_hash,
        )

    raise ValueError(f"Invalid peer type: {peer_type_id}")


def write_input_peer(
    peer_type: str,
    chat_id: int,
    access_hash: int | None = None,
) -> bytes:
    peer_type_id = peer_type_id_by_string.get(peer_type)
    if peer_type_id is None:
        raise ValueError(f"Invalid peer type: {peer_type}")

    return InputPeerStruct.pack(peer_type_id, chat_id, access_hash or 0)


UpdateStateStruct = struct.Struct("<qqqqq")


class UpdateState(NamedTuple):
    state_id: int
    pts: int
    qts: int
    date: int
    seq: int


def read_update_state(value: bytes) -> UpdateState:
    state_id, pts, qts, date, seq = UpdateStateStruct.unpack(value)
    return UpdateState(state_id, pts, qts, date, seq)


def write_update_state(
    state_id: int,
    pts: int | None,
    qts: int | None,
    date: int | None,
    seq: int | None,
) -> bytes:
    return UpdateStateStruct.pack(state_id, pts or 0, qts or 0, date or 0, seq or 0)
