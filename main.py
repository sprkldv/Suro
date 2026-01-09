from pyrogram import Client, idle
import asyncio
import os

API_ID = 12345678  
API_HASH = "123456789qwertyuiopasdfghjklzxcv" 

if not os.path.exists("sessions"):
    os.makedirs("sessions")

app = Client(
    "sessions/suro",
    api_id=API_ID,
    api_hash=API_HASH,
    plugins=dict(root="modules")
)

async def start_bot():
    try:
        await app.start()
        me = await app.get_me()
        print(" [ > ] Suro started!")
        await idle()
    except Exception as e:
        print(f" [ x ] Error: {e}")
    finally:
        if app.is_connected:
            await app.stop()

if __name__ == "__main__":
    if not os.path.exists("modules"):
        os.makedirs("modules")
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())