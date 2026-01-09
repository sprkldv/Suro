import sys
import os
import time
import json
import importlib.util
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message

_icon = "♨️"
_name = "System"
_version = "1.0"
_description = "Системные команды Suro"

# -*- variables -*- #
CONFIG_PATH = "settings/system.json"

def check_config():
    if not os.path.exists("settings"):
        os.makedirs("settings")
    
    if not os.path.exists(CONFIG_PATH):
        default_config = {"PREFIX": "."}
        with open(CONFIG_PATH, "w") as f:
            json.dump(default_config, f, indent=4)

check_config()

class BotConfig:
    @staticmethod
    def load_prefix():
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
            return data.get("PREFIX", ".")

    @staticmethod
    def save_prefix(new_prefix):
        with open(CONFIG_PATH, "w") as f:
            json.dump({"PREFIX": new_prefix}, f, indent=4)

    PREFIX = load_prefix()
    start_time = time.time()

def get_uptime():
    uptime_sec = int(time.time() - BotConfig.start_time)
    h = uptime_sec // 3600
    m = (uptime_sec % 3600) // 60
    s = uptime_sec % 60
    return f"{h}:{m:02}:{s:02}"

def dynamic_command(command: str):
    async def func(flt, client, message: Message):
        if not message.text:
            return False
        return message.text.startswith(f"{BotConfig.PREFIX}{command}")
    return filters.create(func)

@Client.on_message(dynamic_command("restart") & filters.me)
async def restart_bot(client: Client, message: Message):
    await message.edit("💠 Restarting...")
    await client.stop(block=False)
    os.execv(sys.executable, [sys.executable] + sys.argv)

@Client.on_message(dynamic_command("install") & filters.me)
async def install_module(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.edit("❌ Reply to a .py file")
    
    doc = message.reply_to_message.document
    if not doc.file_name.endswith(".py"):
        return await message.edit("❌ Not a .py file")

    name = doc.file_name.replace(".py", "")
    path = f"modules/{doc.file_name}"
    await client.download_media(message.reply_to_message, file_name=path)
    
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        for name in dir(module):
            obj = getattr(module, name)
            if hasattr(obj, "handlers"):
                for handler in obj.handlers:
                    client.add_handler(handler[0], group=handler[1])
                    
        await message.edit(f"✅ Module {doc.file_name} loaded")
    except Exception as e:
        await message.edit(f"❌ Error loading module: {e}")

@Client.on_message(dynamic_command("modules") & filters.me)
async def list_modules(client: Client, message: Message):
    text = f"💮 Installed modules:\n\n<blockquote expandable>"
    for file in os.listdir("modules"):
        if file.endswith(".py"):
            mod_name = file.replace(".py", "")
            try:
                m = importlib.import_module(f"modules.{mod_name}")
                icon = getattr(m, "_icon", "@")
                name = getattr(m, "_name", mod_name)
                ver = getattr(m, "_version", "1.0")
                desc = getattr(m, "_description", "No description")
                text += f" [ {icon} ] {name} - {ver}\n {desc}\n\n"
            except:
                text += f" [ ♨️ ] {mod_name}\n\n"
    await message.edit(f"{text}</blockquote>")
    
@Client.on_message(dynamic_command("prefix") & filters.me)
async def change_prefix_cmd(_, message: Message):
    args = message.text.split()
    if len(args) > 1:
        BotConfig.PREFIX = args[1]
        BotConfig.save_prefix(args[1])
        await message.edit(f"✅ New prefix: {BotConfig.PREFIX}")
    else:
        await message.edit("❌ Specify prefix")
        
@Client.on_message(dynamic_command("stop") & filters.me)
async def stop_bot(client: Client, message: Message):
    await message.edit("💠 Stopping...")
    async def shutdown():
        await asyncio.sleep(1)
        await client.stop()
        os._exit(0)
        
    asyncio.create_task(shutdown())
