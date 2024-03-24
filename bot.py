import os
from discord import Intents as ints
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = ints.default()
intents.message_content = True

bot = commands.Bot(command_prefix = '/', intents = intents)

@bot.command(name='newchallenger')
async def roller(ctx, nickname = None):
    playername = ctx.author.id
    await ctx.send(nickname + " has joined the field of battle!")
    await ctx.send("id of " + nickname + "= " + str(playername))
bot.run(TOKEN)