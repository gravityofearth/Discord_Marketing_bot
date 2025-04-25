import discord
from discord.ext import commands
import random
import asyncio
import pandas as pd
import multiprocessing

class DiscordBot:
    def __init__(self, token, prefix='!', target_channels=None, message_probability=0.3, 
                 post_interval_min=18, post_interval_max=72):
        # Initialize the bot with all intents
        self.intents = discord.Intents.all()
        self.bot = commands.Bot(command_prefix=prefix, intents=self.intents)
        self.token = token
        self.target_channels = target_channels or []
        self.message_probability = message_probability
        self.post_interval_min = post_interval_min
        self.post_interval_max = post_interval_max
        self.messages = []
        
        # Register events
        self.bot.event(self.on_ready)
        self.bot.event(self.setup_hook)
        self.bot.command(name='chat')(self.chat)
        
        # Load messages
        self.sync_sheet_data()

    async def on_ready(self):
        print(f'Logged in as {self.bot.user.name} ({self.bot.user.id})')
        print('------')
    
    async def setup_hook(self):
        # Start the auto-posting background task
        self.bot.loop.create_task(self.auto_post())
    
    def humanize_message(self, message):
        # Add random typos occasionally (5% chance)
        if random.random() < 0.05:
            chars = list(message)
            # Randomly swap two adjacent characters
            if len(chars) >= 2:
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
    
    async def chat(self, ctx, *, message: str):
        # Delete the command message to make it seem more natural
        try:
            await ctx.message.delete()
        except:
            pass

        # Humanize the message
        human_message, delay = self.humanize_message(message)

        # Simulate typing
        async with ctx.typing():
            await asyncio.sleep(delay)

        # Send the message
        await ctx.send(human_message)
    
    def sync_sheet_data(self):
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQ5VWDSMXKIWOaTxuMNhJEXNOrGy1QAiW6E0sQR4S194mM2n6u7i4oUSdpK4_tgUBnn4CF0niAWvDT/pub?output=csv"
        df = pd.read_csv(url)
        data = df.values
        self.messages = [d[0] for d in data]
    
    async def auto_post(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            for channel_id in self.target_channels:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    # Random chance to post
                    if random.random() < self.message_probability:
                        if self.messages:  # Make sure we have messages to choose from
                            message = random.choice(self.messages)
                            human_message, delay = self.humanize_message(message)

                            async with channel.typing():
                                await asyncio.sleep(delay)

                            await channel.send(human_message)

            # Wait between configured interval before next possible post
            await asyncio.sleep(random.randint(self.post_interval_min, self.post_interval_max))
    
    def run(self):
        self.bot.run(self.token)

# Define bot configurations
bot_configs = [
    {
        # Enter your bot1 token here
        "token": "",
        "prefix": "!",
        # Enter your target channel IDs here
        "target_channels": [],
        "message_probability": 0.3,
        "post_interval_min": 18,
        "post_interval_max": 72
    },
    # Add more bot configurations as needed
    {
        # Enter your bot2 token here
        "token": "",
        "prefix": "?",~
        # Enter your target channel IDs here
        "target_channels": [],
        "message_probability": 0.2,
        "post_interval_min": 25,
        "post_interval_max": 90
    },
]

# Define this function outside the if __name__ block so multiprocessing can find it
def start_bot(config):
    bot = DiscordBot(**config)
    bot.run()

# Function to run all bots concurrently
async def run_all_bots():
    # Create tasks for each bot
    tasks = []
    for config in bot_configs:
        bot = DiscordBot(**config)
        # We need to use create_task to run the bot without blocking
        task = asyncio.create_task(bot.run())
        tasks.append(task)
    
    # Wait for all tasks to complete (they shouldn't unless there's an error)
    await asyncio.gather(*tasks)

# Run all bots
if __name__ == "__main__":
    # We need to use asyncio.run to start the main coroutine
    try:
        asyncio.run(run_all_bots())
    except RuntimeError:
        # Discord.py's run method already creates an event loop, so we need a different approach
        # Create and run each bot in separate processes
        processes = []
        for config in bot_configs:
            p = multiprocessing.Process(target=start_bot, args=(config,))
            p.start()
            processes.append(p)
        
        for p in processes:
            p.join()
