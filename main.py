import discord
import os
from dotenv import load_dotenv

import aiohttp
import tempfile
import subprocess

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name = "hello", description = "Say hello to the bot")
async def hello(ctx):
    await ctx.respond("Hey!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    for attachment in message.attachments:
        supported_exts = [
            '.zip'
        ]

        ext: str
        for supported_ext in supported_exts:
            if attachment.filename.endswith(supported_ext):
                ext = supported_ext
                break

        if not ext:
            continue

        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as response:
                if response.status != 200:
                    print('Response status is not 200')
                    continue

                data = await response.read()
                with tempfile.NamedTemporaryFile(suffix=ext) as temp:
                    name = temp.name
                    with open(name, 'wb') as archive:
                        archive.write(data)

                        with tempfile.TemporaryDirectory() as temp_dir:
                            bsdtar = subprocess.run(['bsdtar', '-vxf', name], capture_output=True, cwd=temp_dir, text=True)
                            print(bsdtar.stdout)

                            if bsdtar.returncode == 0:
                                tree = subprocess.run(['tree', '-a'], capture_output=True, cwd=temp_dir, text=True)
                                stdout = tree.stdout
                                print(stdout)

                                await message.channel.send(f'```\n{stdout}\n```', silent=True)
                            else:
                                print('bsdtar did not return 0')
                                continue

bot.run(os.getenv('TOKEN'))
