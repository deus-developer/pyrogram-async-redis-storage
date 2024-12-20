# Pyrogram Redis Storage

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/github/license/deus-developer/pyrogram-async-redis-storage)
![Build Status](https://img.shields.io/github/actions/workflow/status/deus-developer/pyrogram-async-redis-storage/release_pypi.yaml)

Pyrogram Redis Storage is a lightweight and fully asynchronous library designed to manage Pyrogram sessions and peers
using Redis as a storage backend. The library is optimized for performance and efficient storage, making it ideal for
large-scale applications.

## ⚠️ Compatibility

This library is only compatible with a [custom fork of Pyrogram](https://github.com/KurimuzonAkuma/pyrogram/). Make sure
to use this fork for seamless integration.

## ✨ Features

- **Fully Asynchronous**: Built with `asyncio` for high-performance operations.
- **Redis Backend**: Efficiently stores sessions and peer data.
- **Optimized Storage**: Minimal Redis usage while maintaining performance.
- **Scalable**: Designed for high concurrency and large datasets.
- **Future CLI Support**: A command-line interface is planned for future releases.

## 🏗️ Installation

Install the library using pip:

```bash
pip install pyrogram-async-redis-storage
```

## 🚀 Example Usage

Below is an example of how to use Pyrogram Redis Storage to manage your Pyrogram session:

```python
import asyncio
from contextlib import AsyncExitStack

from pyrogram import (  # type: ignore[attr-defined]
    Client,
    filters,
    idle,
)
from pyrogram.types import Message
from redis.asyncio import Redis

from pyrogram_async_redis_storage import RedisAsyncStorage


async def main() -> None:
    async with AsyncExitStack() as stack:
        redis = await stack.enter_async_context(Redis.from_url("redis://localhost:6379"))
        storage = RedisAsyncStorage(
            name="my_account",
            redis=redis,
            prefix="pyrogram_async_redis_storage",
        )

        client: Client = await stack.enter_async_context(
            Client(
                name=storage.name,
                api_id=8,
                api_hash="7245de8e747a0d6fbe11f7cc14fcc0bb",
                storage_engine=storage
            )
        )

        @client.on_message(filters.private)
        async def hello(_: Client, message: Message) -> None:
            await message.reply("Hello from Pyrogram!")

        await idle()


if __name__ == '__main__':
    asyncio.run(main())
```

## 🏛️ Project Structure

```
├── LICENSE
├── README.MD
├── pyproject.toml
├── pyrogram_async_redis_storage
│   ├── __about__.py
│   ├── __init__.py
│   ├── accessor.py
│   ├── py.typed
│   ├── redis_storage.py
│   └── schemas.py
└── requirements.txt
```

## 📃 License

This project is licensed under the [Apache License 2.0](LICENSE).

## 🤝 Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository and submit a pull request. For major
changes, open an issue first to discuss your ideas.

### Contribution Workflow

1. Fork the repository.
2. Create your feature branch: `git checkout -b feature/my-new-feature`.
3. Commit your changes: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature/my-new-feature`.
5. Open a pull request.

## 💬 Contact

For questions, support, or to connect, reach out to the project maintainers:

- **Email**: [deusdeveloper@yandex.com](mailto:deusdeveloper@yandex.com)
- **Telegram**: [@DeusDeveloper](https://t.me/DeusDeveloper)
- **GitHub Issues**: [GitHub Repository](https://github.com/deus-developer/pyrogram-async-redis-storage/issues)

---

Enjoy using Pyrogram Redis Storage! 🚀
