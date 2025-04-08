import discord
import os # default module
from dotenv import load_dotenv
import sqlite3

# Setup the database
conn = sqlite3.connect('base.db') # create a connection to the database
# Create the tables if they don't exist
# This database is used to store a list of music tracks metadata, with the following columns:
# - id: the id of the track
# - usual_name: the usual name of the track
# - artist: the artist of the track
# - number: the number of the track (if there is one)
# - versions: a list of versions along with their name and youtube link
conn.execute('''
CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usual_name TEXT,
    full_name TEXT,
    composer TEXT,
    number TEXT,
    versions JSON
)
''')
intents = discord.Intents.default()
intents.message_content = True

load_dotenv() # load all the variables from the env file
bot = discord.Bot(intents=intents) # create a bot instance
bot.load_extension('src.quiz.quiz')

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    glob_n_tracks = 0
    n_versions = 0
    # Fetch all messages in all channels and save them to a file
    for guild in bot.guilds:
        for channel in guild.text_channels:
            try:
                print(f"Fetching messages from channel {channel.name} in guild {guild.name}")
                messages = await channel.history(limit=500).flatten()
                composer = channel.name.strip() # Get the channel name as the composer name
                # Parse messages that have this format (rating is not used yet, all entries can be empty (aka NULL)):
                """
Usual Name : Arabesque
Full Name : Etude No 2 
Number : Op 100 No 2

Version : 
- Unknown : https://www.youtube.com/watch?v=1oMm_n38OxQ&list=PLjL2pVlc9g88hOHED-xtLGYIkzD2HkGvl&index=665

Rating :
                """
                n_tracks = 0
                for message in messages:
                    print(f"Processing message: {message.content}")
                    lines = message.content.strip().split('\n')
                    # Skip the message if it doesn't have the expected format
                    if len(lines) < 4 or not lines[0].startswith('Usual Name') or not lines[1].startswith('Full Name'):
                        continue
                    n_tracks += 1
                    usual_name = lines[0].split(':')[1].strip() if ':' in lines[0] else None
                    full_name = lines[1].split(':')[1].strip() if ':' in lines[1] else None
                    # If usual_name and full_name are empty, skip the message
                    if not usual_name and not full_name:
                        continue
                    
                    number = lines[2].split(':')[1].strip() if ':' in lines[2] else None
                    versions = []
                    
                    for line in lines[3:]:
                        if line.strip().startswith('-'):
                            # Parse the version name and link with the format:
                            # - <name> : <link>
                            version_parts = line.split(':')
                            if len(version_parts) < 2:
                                continue
                            version_name = version_parts[0].strip().replace('-', '').strip()
                            version_link = ':'.join(version_parts[1:]).strip()
                            
                            versions.append({'name': version_name, 'link': version_link})
                            n_versions += 1
                    # Convert versions to a JSON array
                    versions_str = str(versions) if versions else None
                    
                    # Insert the data into the database
                    conn.execute('''
                    INSERT INTO tracks (usual_name, full_name, composer, number, versions)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (usual_name, full_name, composer, number, versions_str))
                    conn.commit()
                    print(f"Inserted track: {usual_name}, {full_name}, {composer}, {number}, {versions_str}")
                glob_n_tracks += n_tracks
                print(f"Fetched {n_tracks} tracks from {channel.name} in guild {guild.name}")

            except discord.Forbidden:
                print(f"Cannot access channel {channel.name} in guild {guild.name}")
    
    print(f"Fetched {glob_n_tracks} tracks and {n_versions} versions in total from all channels.")

@bot.command(description="Sends the bot's latency.") # this decorator makes a slash command
async def ping(ctx: discord.ApplicationContext): # a slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {bot.latency}")

bot.run(os.getenv('TOKEN')) # run the bot with the token