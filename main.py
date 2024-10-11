import discord
import os # default module
import random
import re
from dotenv import load_dotenv

from quiz.quiz import Quiz
intents = discord.Intents.default()
intents.message_content = True

load_dotenv() # load all the variables from the env file
bot = discord.Bot(intents=intents) # create a bot instance
bot.load_extension('quiz')

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.command(description="Sends the bot's latency.") # this decorator makes a slash command
async def ping(ctx: discord.ApplicationContext): # a slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {bot.latency}")

bot.run(os.getenv('TOKEN')) # run the bot with the token