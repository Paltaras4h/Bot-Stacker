import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv('venv/secrets.env')

# Access secrets using os.environ
bot_token = os.environ.get('BOT_TOKEN')


# Create an instance of the bot
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Event: Bot is ready and connected to the server
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    print('------')

# Command: !htolox
@bot.command()
async def htolox(ctx):
    await ctx.send('zeniya')

# Event: Message is received
@bot.event
async def on_message(message):
    # Ignore if the message is from the bot itself
    if message.author == bot.user:
        return

    # Respond to a specific message content
    if message.content.lower() == 'ping':
        await message.channel.send('Pong!')

    await bot.process_commands(message)

# Event: Bot joins a server
@bot.event
async def on_guild_join(guild):
    print(f'Bot has joined {guild.name} (ID: {guild.id})')
print(bot_token)
# Run the bot using your bot token
bot.run(bot_token)

#111
