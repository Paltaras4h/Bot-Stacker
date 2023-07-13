import asyncio

import discord
from discord.ext import commands
import os
import json
from Models.User import User
from Models.Stack import Stack
import Database.Repository as rep
from datetime import datetime

with open(os.getcwd()+'/venv/configuration.json') as f:
    data = json.load(f)

bot_token = data['botApiToken']

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

@bot.command()
async def go(message):
    user_id, user_name = message.author.id, message.author.name
    user = rep.get_user(user_id, user_name)
    # if not user.default_time_from:
    #     embed = discord.Embed(title="Providing Time", description="Please, enter time when you want to start and "
    #                                                               "finish playing")
    #     embed.add_field(name="Start Time", value="Enter Start Time")
    #     embed.add_field(name="End Time", value="Enter End Time")
    #
    #     text = await message.send(embed=embed)
    #
    #     def check(msg):
    #         return msg.author == message.author and msg.channel == message.channel
    #
    #     try:
    #         # Waiting for the user's response
    #         response1 = await bot.wait_for('message', check=check, timeout=30)
    #         response2 = await bot.wait_for('message', check=check, timeout=30)
    #
    #         # Retrieving the user's response
    #         field1_response = response1.content
    #         field2_response = response2.content
    #
    #         await message.send(f"User ID: {user_id}\nUsername: {user_name}\nField 1 response: {field1_response}")
    #         await message.send(f"User ID: {user_id}\nUsername: {user_name}\nField 2 response: {field2_response}")
    #
    #     except asyncio.TimeoutError:
    #         await message.send("Response timed out.")

    dt = datetime(2023, 7, 13, 16, 2, 30)
    timestamp = discord.utils.format_dt(dt, style='F')
    await message.send(timestamp)

@bot.command()
async def nego(ctx):
    await ctx.send("vsetaki go")

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



# v Paltaras4h's code v

@bot.command()
async def test(ctx):
    user = rep.get_user(ctx.author.id, ctx.author.name)
    print(user.id, user.name)


@bot.command()
async def netest(ctx):
    await ctx.send('ne, vsetaki test')
# ^ Paltaras4h's code ^



# Event: Bot joins a server
@bot.event
async def on_guild_join(guild):
    print(f'Bot has joined {guild.name} (ID: {guild.id})')
# Run the bot using your bot token
bot.run(bot_token)