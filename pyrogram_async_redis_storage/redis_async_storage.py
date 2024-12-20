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

import time
from collections.abc import Coroutine
from typing import (
    TypeVar,
)

from pyrogram.storage import Storage  # type: ignore[attr-defined]
from redis.asyncio import Redis

from pyrogram_async_redis_storage.accessor import (
    BoolValue,
    BytesValue,
    IntValue,
    RWValue,
    Undefined,
    undefined,
)
from pyrogram_async_redis_storage.schemas import (
    InputPeerType,
    UpdateState,
    read_input_peer,
    read_update_state,
    write_input_peer,
    write_update_state,
)

AccessorT = TypeVar("AccessorT", int, bytes, bool, str)


class RedisAsyncStorage(Storage):
    VERSION = 1

    def __init__(
        self,
        name: str,
        redis: Redis[bytes],
        prefix: str,
    ) -> None:
        super().__init__(name)
        self.name = name
        self.prefix = prefix
        self.redis = redis

        self._session_name = f"{self.prefix}:session"
        self._state_name = f"{self.prefix}:state"

    async def delete(self) -> None:
        await self.redis.hdel(
            self._session_name,
            "dc_id",
            "test_mode",
            "auth_key",
            "date",
            "user_id",
            "is_bot",
            "version",
            "api_id",
        )

    async def open(self) -> None:
        version = await self.version()
        if version is None:
            await self.version(self.VERSION)
            return

        if version > self.VERSION:
            raise ValueError("Redis storage version too old")

        if version == self.VERSION:
            return

        raise NotImplementedError("Redis storage upgrade not implemented")

    async def save(self) -> None:
        await self.date(int(time.time()))

    async def close(self) -> None:
        await self.save()

    async def _get_all_update_states(self) -> list[UpdateState]:
        states = await self.redis.hgetall(self._state_name)
        return list(map(read_update_state, states.values()))

    async def _delete_update_state(self, state_id: int) -> None:
        key = state_id.to_bytes(length=8, byteorder="little", signed=True)
        await self.redis.hdel(self._state_name, key)

    async def _update_update_state(
        self,
        state_id: int,
        pts: int,
        qts: int,
        date: int,
        seq: int,
    ) -> None:
        key = state_id.to_bytes(length=8, byteorder="little", signed=True)
        await self.redis.hset(
            name=self._state_name,
            key=key,
            value=write_update_state(
                state_id=state_id,
                pts=pts,
                qts=qts,
                date=date,
                seq=seq,
            ),
        )

    async def update_state(
        self,
        update_state: tuple[int, int, int, int, int] | int | Undefined = undefined,
    ) -> list[UpdateState] | None:
        if isinstance(update_state, Undefined):
            return await self._get_all_update_states()

        if isinstance(update_state, int):
            await self._delete_update_state(update_state)
            return None

        state_id, pts, qts, date, seq = update_state
        await self._update_update_state(state_id, pts, qts, date, seq)
        return None

    async def update_peers(
        self,
        peers: list[tuple[int, int, str, str]],
    ) -> None:
        mapping: dict[str, bytes] = {}
        for chat_id, access_hash, peer_type, _phone_number in peers:
            del _phone_number  # TODO(deus-developer): update phone number pointer.
            mapping[f"{self.prefix}:peer:{chat_id}"] = write_input_peer(
                peer_type=peer_type,
                chat_id=chat_id,
                access_hash=access_hash,
            )

        if mapping:
            await self.redis.mset(mapping)  # type: ignore[arg-type]

    async def update_usernames(self, usernames: list[tuple[int, list[str]]]) -> None:
        del usernames  # TODO(deus-developer): update usernames pointer.

    async def get_peer_by_id(self, peer_id: int) -> InputPeerType:
        value = await self.redis.get(f"{self.prefix}:peer:{peer_id}")
        if value is None:
            raise KeyError(f"ID not found: {peer_id}")

        return read_input_peer(value)

    async def get_peer_by_username(self, username: str) -> InputPeerType:
        pointer = await self.redis.get(f"{self.prefix}:username:{username}")
        if pointer is None:
            raise KeyError(f"Username not found: {username}")

        chat_id = int.from_bytes(pointer, byteorder="little", signed=True)
        return await self.get_peer_by_id(chat_id)

    async def get_peer_by_phone_number(self, phone_number: str) -> InputPeerType:
        pointer = await self.redis.get(f"{self.prefix}:phone:{phone_number}")
        if pointer is None:
            raise KeyError(f"Phone number not found: {phone_number}")

        chat_id = int.from_bytes(pointer, byteorder="little", signed=True)
        return await self.get_peer_by_id(chat_id)

    async def _get(self, attr: str, rw: type[RWValue[AccessorT]]) -> AccessorT | None:
        value = await self.redis.hget(self._session_name, attr)  # type: bytes | None
        if value is None:
            return None

        return rw.unpack(value)

    async def _set(
        self,
        attr: str,
        value: AccessorT | None,
        rw: type[RWValue[AccessorT]],
    ) -> None:
        if value is None:
            await self.redis.hdel(self._session_name, attr)
        else:
            await self.redis.hset(
                name=self._session_name,
                key=attr,
                value=rw.pack(value),
            )

    def _accessor(
        self,
        field_name: str,
        rw: type[RWValue[AccessorT]],
        value: AccessorT | None | Undefined,
    ) -> Coroutine[None, None, AccessorT | None]:
        if isinstance(value, Undefined):
            return self._get(field_name, rw)
        return self._set(field_name, value, rw)

    def dc_id(
        self,
        value: int | None | Undefined = undefined,
    ) -> Coroutine[None, None, int | None]:
        return self._accessor(field_name="dc_id", rw=IntValue, value=value)

    def test_mode(
        self,
        value: bool | None | Undefined = undefined,
    ) -> Coroutine[None, None, bool | None]:
        return self._accessor(field_name="test_mode", rw=BoolValue, value=value)

    def auth_key(
        self,
        value: bytes | None | Undefined = undefined,
    ) -> Coroutine[None, None, bytes | None]:
        return self._accessor(field_name="auth_key", rw=BytesValue, value=value)

    def date(
        self,
        value: int | None | Undefined = undefined,
    ) -> Coroutine[None, None, int | None]:
        return self._accessor(field_name="date", rw=IntValue, value=value)

    def user_id(
        self,
        value: int | None | Undefined = undefined,
    ) -> Coroutine[None, None, int | None]:
        return self._accessor(field_name="user_id", rw=IntValue, value=value)

    def is_bot(
        self,
        value: bool | None | Undefined = undefined,
    ) -> Coroutine[None, None, bool | None]:
        return self._accessor(field_name="is_bot", rw=BoolValue, value=value)

    def version(
        self,
        value: int | None | Undefined = undefined,
    ) -> Coroutine[None, None, int | None]:
        return self._accessor(field_name="version", rw=IntValue, value=value)

    def api_id(
        self,
        value: int | None | Undefined = undefined,
    ) -> Coroutine[None, None, int | None]:
        return self._accessor(field_name="api_id", rw=IntValue, value=value)
