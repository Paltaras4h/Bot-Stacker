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
    if not user.default_time_from:
        embed_time_zone = discord.Embed(title="Providing Time", description="What is your time now?")
        embed_time_zone.add_field(name="Your Time", value="Provide Your Current Time")

        text = await message.send(embed=embed_time_zone)
        field1_response = None

        def check(msg):
            return msg.author == message.author and msg.channel == message.channel

        try:
            # Waiting for the user's response
            response1 = await bot.wait_for('message', check=check, timeout=30)

            # Retrieving the user's response
            field1_response = response1.content

            await message.send(f"User ID: {user_id}\nUsername: {user_name}\nField 1 response: {field1_response}")

        except asyncio.TimeoutError:
            await message.send("Response timed out.")

        separator = None
        for char in field1_response:
            if char.isdigit():
                continue
            else:
                separator = char
                break

        if separator:
            format_string = '%H' + separator + '%M'
            dt = datetime.strptime(field1_response, format_string)
            print(dt)
        else:
            print("Time Format Error")

@bot.command()
async def иди(ctx):
    await ctx.send("Sam Poshel")

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
