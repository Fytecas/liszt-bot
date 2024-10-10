import discord
import os # default module
import random
import re
from dotenv import load_dotenv
from discord.commands import Option

intents = discord.Intents.default()
intents.message_content = True

load_dotenv() # load all the variables from the env file
bot = discord.Bot(intents=intents) # create a bot instance

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.command(description="Sends the bot's latency.") # this decorator makes a slash command
async def ping(ctx: discord.ApplicationContext): # a slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {bot.latency}")

def get_random_right_channel(channels, ctx):
    random_i = random.randint(0, len(channels) - 1)
    random_channel = channels[random_i]
    if random_channel.permissions_for(ctx.guild.me).read_message_history:
        return random_channel
    else:
        # Remove the channel from the list and try again
        channels.pop(random_i)
        if len(channels) == 0:
            return None
        return get_random_right_channel(channels, ctx)

def get_random_url_in_messages(messages):
    random_i = random.randint(0, len(messages) - 1)
    message = messages[random_i]
    # Look for youtubes links in the message
    print(message.content)
    urls = re.findall(r'(https?://www.youtube.com/[^\s]+)', message.content)
    
    if urls and message.author != bot.user:
        # Take the vidio id from the link
        id = urls[0].split('v=')[1]
        id = id.split('&')[0]
        return id, message.content
    
    else:
        # Remove the message from the list and try again
        messages.pop(random_i)
        if len(messages) == 0:
            return None, None
        return get_random_url_in_messages(messages)
    
class QuizView(discord.ui.View):
    video_id: str
    base_message: str
    
    def __init__(self, video_id: str, base_message: str):
        self.video_id = video_id
        self.base_message = base_message
        super().__init__()
        
        self.add_item(discord.ui.Button(label="Go listen it !", style=discord.ButtonStyle.link, url="https://fytecas.github.io/liszt-bot/?id=" + video_id))
    
    @discord.ui.button(label="Think I got it", style=discord.ButtonStyle.primary, row=1)
    async def got_it(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("**Here is the original message:**\n"+ self.base_message)
    
    
@bot.command(description="Quizz")
async def quizz(
    ctx: discord.ApplicationContext, 
    channel: Option(discord.channel.TextChannel, "The channel to get the quizz from", required=False, default='*'), # type: ignore
    channel_category: Option(discord.channel.CategoryChannel, "The category of the channel to get the quizz from", required=False, default='*'), # type: ignore
    ):
    if channel == '*':
        if channel_category == '*':
            text_channels = ctx.guild.text_channels
        else:
            text_channels = [channel for channel in ctx.guild.text_channels if channel.category == channel_category]
        channel = get_random_right_channel(text_channels, ctx)
    else:
        channel = channel
        # Check if the bot has permission to read messages in the channel
        if not channel.permissions_for(ctx.guild.me).read_message_history:
            await ctx.respond("I don't have permission to read messages in the channel.")
            return
    if channel is None:
        await ctx.respond("I don't have permission to read messages in any of the channels.")
        return
    messages = await channel.history(limit=200).flatten()
    id, content = get_random_url_in_messages(messages)
    if id is None:
        await ctx.respond("I couldn't find any URLs in the messages. channel: " + channel.mention)
    else:
        await ctx.respond("**Here is some random music**", view=QuizView(id, content))

bot.run(os.getenv('TOKEN')) # run the bot with the token