import os
from discord import Intents as ints
from discord.ext import commands
from dotenv import load_dotenv
import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = ints.default()
intents.message_content = True

bot = commands.Bot(command_prefix = '/', intents = intents)

@bot.command(name='newchallenger')
async def roller(ctx, playername, nickname = None):
    await ctx.send(nickname + " has joined the field of battle!")

bot.run(TOKEN)