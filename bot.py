# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official

import asyncio
import datetime
import sys
import os
import time
from datetime import timezone, timedelta

import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram import Client, filters, __version__ as pyrogram_version
from pyrogram.types import Message

from config import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, KEEP_ALIVE_URL, DB_URI, DB_NAME, ADMINS
from logger import LOGGER

from utils.files import safe_filename, ensure_dir
from utils.cooldown import check_cooldown
from utils.progress import progress_bar
from utils.batch import start_batch, add_to_batch, get_batch, clear_batch, USER_BATCH

logger = LOGGER(__name__)

# Ensure base directory
os.makedirs("/app/downloads", exist_ok=True)

IST = timezone(timedelta(hours=5, minutes=30))

mongo_client = AsyncIOMotorClient(DB_URI)
db = mongo_client[DB_NAME]
users_col = db["logged_users"]


async def keep_alive():
    async with aiohttp.ClientSession() as session:
        while True:
            if KEEP_ALIVE_URL:
                try:
                    await session.get(KEEP_ALIVE_URL)
                except Exception as e:
                    logger.error(f"Keep-alive failed: {e}")
            await asyncio.sleep(100)


class Bot(Client):
    def __init__(self):
        super().__init__(
            "Rexbots Login",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            sleep_threshold=10
        )

    async def start(self):
        await super().start()
        me = await self.get_me()

        logger.info(f"Connected to MongoDB DB: {db.name}")
        self.keep_alive_task = asyncio.create_task(keep_alive())

        now = datetime.datetime.now(IST)
        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        if LOG_CHANNEL:
            await self.send_message(
                LOG_CHANNEL,
                f"🤖 Bot Started\n"
                f"@{me.username}\n"
                f"📅 {now.strftime('%d-%b-%Y')} | 🕒 {now.strftime('%I:%M %p')}\n"
                f"🐍 Python {py_ver}\n"
                f"🔥 Pyrogram {pyrogram_version}"
            )

    async def stop(self, *args):
        if self.keep_alive_task:
            self.keep_alive_task.cancel()
        await super().stop()


BotInstance = Bot()


@BotInstance.on_message(filters.private & filters.incoming, group=-1)
async def log_user(bot: Client, message: Message):
    if not message.from_user:
        return

    await users_col.update_one(
        {"user_id": message.from_user.id},
        {"$setOnInsert": {
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "logged_at": datetime.datetime.now(IST).isoformat()
        }},
        upsert=True
    )


# 🔽 INTERNAL SAFE DOWNLOAD FUNCTION
async def _download(client: Client, message: Message):
    uid = message.from_user.id

    name = safe_filename(message.document.file_name)
    path = f"/app/downloads/{uid}"
    ensure_dir(path)

    temp = f"{path}/{name}.temp"
    final = f"{path}/{name}"

    status = await message.reply("📥 Starting download...")
    start = time.time()

    try:
        await message.download(
            file_name=temp,
            progress=progress_bar,
            progress_args=(start, status)
        )
        os.rename(temp, final)
        await status.edit("✅ Download completed")
    except Exception as e:
        if os.path.exists(temp):
            os.remove(temp)
        await status.edit(f"❌ Failed:\n`{e}`")

    await asyncio.sleep(2)


@BotInstance.on_message(filters.document & filters.private)
async def document_handler(client: Client, message: Message):
    uid = message.from_user.id

    if uid in USER_BATCH:
        add_to_batch(uid, message)
        await message.reply("➕ Added to batch")
        return

    if uid not in ADMINS:
        allowed, wait = check_cooldown(uid)
        if not allowed:
            await message.reply(f"⏳ Wait {wait}s")
            return

    await _download(client, message)


@BotInstance.on_message(filters.command("batch") & filters.private)
async def batch_start_cmd(client, message):
    uid = message.from_user.id

    if uid in USER_BATCH:
        await message.reply("⚠️ Batch already running. Send /done")
        return

    start_batch(uid)
    await message.reply("📦 Batch started. Send files, then /done")


@BotInstance.on_message(filters.command("done") & filters.private)
async def batch_done_cmd(client, message):
    uid = message.from_user.id
    batch = get_batch(uid)

    if not batch:
        await message.reply("❌ No active batch")
        return

    status = await message.reply(f"🚀 Batch started ({len(batch)} files)")

    for i, msg in enumerate(batch, 1):
        await status.edit(f"📥 Downloading {i}/{len(batch)}")
        await _download(client, msg)
        await asyncio.sleep(3)

    clear_batch(uid)
    await status.edit("✅ Batch completed")


BotInstance.run()
