from keep_alive import keep_alive

keep_alive()

import discord
from discord.ext import commands
import os
import requests
from flask import Flask
from threading import Thread

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store channels by type and language
CHANNEL_MAP = {
    # Example: "help": {"en": channel_id, "es": channel_id, "ja": channel_id}
}

# Language codes map (you can expand this)
LANG_CODES = {
    "english": "en",
    "español": "es",
    "japanese": "ja"
}

def translate_text(text, target_lang):
    url = f"https://api.mymemory.translated.net/get?q={text}&langpair=auto|{target_lang}"
    response = requests.get(url)
    data = response.json()
    return data['responseData']['translatedText']

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def addlanguage(ctx, channel: discord.TextChannel, language: str, type: str):
    lang_code = LANG_CODES.get(language.lower())
    if not lang_code:
        await ctx.send("Unsupported language.")
        return

    if type not in CHANNEL_MAP:
        CHANNEL_MAP[type] = {}

    CHANNEL_MAP[type][lang_code] = channel.id
    await ctx.send(f"Added {channel.mention} as {language.title()} channel for {type}.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    for type, langs in CHANNEL_MAP.items():
        if message.channel.id in langs.values():
            source_lang = None
            for lang_code, chan_id in langs.items():
                if chan_id == message.channel.id:
                    source_lang = lang_code
                    break

            for target_lang, target_chan_id in langs.items():
                if target_lang != source_lang:
                    translated = translate_text(message.content, target_lang)
                    embed = discord.Embed(description=translated)
                    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
                    embed.set_footer(text=f"From #{message.channel.name}")
                    target_channel = bot.get_channel(target_chan_id)

                    if message.attachments:
                        file_url = message.attachments[0].url
                        embed.set_image(url=file_url)

                    await target_channel.send(embed=embed)
            break

    await bot.process_commands(message)

# ---------------------------
from keep_alive import keep_alive
import os

# Start the web server
keep_alive()

# Run your bot
bot.run(os.environ['TOKEN'])

