import discord
from discord.ext import commands
import random
import asyncio
from pandas import pandas as pd
import datetime

# Initialize the bot with all intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

messages = []

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
 
# Use setup_hook for initialization tasks
@bot.event
async def setup_hook():
    # Start the auto-posting background task
    bot.loop.create_task(auto_post())

# Function to make messages more human-like
def humanize_message(message):
    # Add random typos occasionally (5% chance)
    if random.random() < 0.05:
        chars = list(message)
        # Randomly swap two adjacent characters
        i = random.randint(0, len(chars) - 2)
        chars[i], chars[i+1] = chars[i+1], chars[i]
        message = ''.join(chars)

    # Add random emojis occasionally (20% chance)
    if random.random() < 0.2:
        emojis = ['😊', '😂', '👍', '🤔', '❤️', '🔥', '🎉']
        message += ' ' + random.choice(emojis)

    # Add a random delay typing delay
    delay = random.uniform(0.5, 2.5)

    return message, delay

@bot.command(name='chat')
async def chat(ctx, *, message: str):
    # Delete the command message to make it seem more natural
    try:
        await ctx.message.delete()
    except:
        pass

    # Humanize the message
    human_message, delay = humanize_message(message)

    # Simulate typing
    async with ctx.typing():
        await asyncio.sleep(delay)

    # Send the message
    await ctx.send(human_message)

# Import messages from google sheet
def sync_sheet_data():
    global messages
    # Replace with your Google Sheet URL
    url = ""
    df = pd.read_csv(url)
    data = df.values
    messages = [
        d[0]
        for d in data
    ]

sync_sheet_data()

# Function to post random messages periodically
async def auto_post():
    await bot.wait_until_ready()

    # List of channels to post in (replace with your desired channels)
    target_channels = []

    while not bot.is_closed():
        for channel_id in target_channels:
            channel = bot.get_channel(channel_id)
            if channel:
                # Random chance to post (30% per check)
                if random.random() < 0.3:
                    message = random.choice(messages)
                    human_message, delay = humanize_message(message)

                    async with channel.typing():
                        await asyncio.sleep(delay)

                    await channel.send(human_message)

        # Wait between 18 seconds to 72 seconds before next possible post
        await asyncio.sleep(random.randint(18, 72))

# Run the bot (replace with your actual bot token)
bot.run('')