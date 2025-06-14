import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Load .env (only needed locally)
load_dotenv()

# Flask app to keep alive
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8000)

Thread(target=run).start()

# Intents
intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.guilds = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

PREDETERMINED_NAMES = [
    "Timber Hearth", "Brittle Hollow", "Giant's Deep", "Dark Bramble", "Interloper",
    "Moon", "The Stranger", "White Hole Station", "Sun Station", "Ash Twins", "Ember Twins"
]

CATEGORY_NAME = "SPACE"
LOBBY_CHANNEL_NAME = "Venture"

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel and before.channel.category and before.channel.category.name == CATEGORY_NAME:
        if before.channel.name in PREDETERMINED_NAMES and len(before.channel.members) == 0:
            await before.channel.delete()
            print(f"🧹 Deleted empty channel: {before.channel.name}")

    if after.channel and after.channel.name == LOBBY_CHANNEL_NAME:
        guild = member.guild
        category = discord.utils.get(guild.categories, name=CATEGORY_NAME)

        if not category:
            category = await guild.create_category(CATEGORY_NAME)

        used_names = [vc.name for vc in category.voice_channels]
        available_names = [name for name in PREDETERMINED_NAMES if name not in used_names]

        if not available_names:
            await member.send("🚫 All destinations are currently in use. Please try again later.")
            return

        chosen_name = random.choice(available_names)
        new_channel = await category.create_voice_channel(name=chosen_name)
        await member.move_to(new_channel)
        print(f"🚀 Moved {member.display_name} to {chosen_name}")

bot.run(os.getenv("BOT_TOKEN"))
