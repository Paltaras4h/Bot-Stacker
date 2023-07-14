import asyncio

import discord
from discord.ext import commands
from discord.ui import View, Button
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


async def ask_for_time(message, dt_utc):
    def check(msg):
        return msg.author == message.author and msg.channel == message.channel
    field1_response = None
    response1 = None
    while True:
        try:
            # Waiting for the user's response
            response1 = await bot.wait_for('message', check=check, timeout=30)

            # Retrieving the user's response
            field1_response = response1.content

        except asyncio.TimeoutError:
            await message.send("__**Response timed out**__")
            return None

        separator = ""
        for char in field1_response:
            if char.isdigit() and not separator:
                continue
            elif char.isdigit() and separator:
                break
            else:
                separator += char

        try:
            if separator:
                time_list = field1_response.split(separator)
                dt = datetime.now()
                dt = dt.replace(hour=int(time_list[0]), minute=int(time_list[1]), second=0, microsecond=0)
                if not dt_utc:
                    time_zone = dt - response1.created_at.replace(tzinfo=None, second=0, microsecond=0)
                    hours_time_zone = time_zone.total_seconds() // 3600
                    return int(hours_time_zone)
                return dt
            else:
                await message.send("__**I could not understand what time you have given, could you try once "
                                   "more**__")
                continue
        except ValueError:
            await message.send("__**I could not understand what time you have given, could you try once "
                               "more**__")

@bot.command()
async def go(message):
    user_id, user_name = message.author.id, message.author.name
    user = rep.get_user(user_id, user_name)
    if not user.default_time_from:
        embed_time_zone = discord.Embed(title="Providing Time", description="What is your time now?")
        embed_time_zone.add_field(name="Your Time", value="Provide Your Current Time")

        await message.send(embed=embed_time_zone)

        utc = await ask_for_time(message, False)

        if utc:
            embed_time_frame = discord.Embed(title="When Do You Want to Play?", description="Provide Start and End Times "
                                                                                            "of Your Game Session", colour=0xff0000)
            embed_time_frame.add_field(name="Start Time", value="Enter Start Time in First Message")
            embed_time_frame.add_field(name="End Time", value="Enter End Time in Second Message")

            await message.send(embed=embed_time_frame)
            await message.send(f"__**Send Your Start Time:**__")
            time_from = await ask_for_time(message, True)
            if time_from:
                await message.send(f"__**Send Your End Time:**__")
                time_to = await ask_for_time(message, True)
                if time_to:
                    user.default_time_from = time_from
                    user.default_time_to = time_to
                    user.UTC = utc
    else:
        embed_choose_time_option = discord.Embed(title="What Time Frame Do You Want to Use?", description="Do you want to play during prevoiusly stated time or you want to choose new time frame?", colour=0x00ff00)


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
async def ask_to_create_or_join_stack(member):
    guild = member.guild
    channel = discord.utils.get(guild.text_channels, name='бот')#todo ask for general_chat when adding to server
    member_mention = member.mention

    view = View()
    # Add the buttons to the view
    view.add_item(Button(style=discord.ButtonStyle.primary, label="Create new stack", custom_id="button1"))
    if len(rep.get_stacks())!=0:
        view.add_item(Button(style=discord.ButtonStyle.primary, label="Join existing stack", custom_id="button2"))
    # Create the embed message with a field
    embed = discord.Embed(title="You want to play? Let's play!", description=f"{member_mention}")

    await channel.send(embed=embed, view=view)

    @discord.ui.button(custom_id="button1")
    async def my_button_click(self, button: discord.ui.Button, interaction: discord.Interaction):
        await go()

    @discord.ui.button(custom_id="button2")
    async def my_button_click(self, button: discord.ui.Button, interaction: discord.Interaction):
        #TODO await show_stacks()
        pass

def ask_to_leave_stack():
    pass


@bot.event
async def on_voice_state_update(member, before, after):
    # not val and not_afk_channel -> val ask2add
    # if user is in stack:
    #   val -> not_val and not_afk_channel -> wait(5sec) -> ask2leave

    if before.channel != after.channel:  # Check if channel changed
        is_val_channel = lambda c: "ВАЛЕРІЙ" in str(c) or "ВОЛЕРА🧑" in str(c)

        if before.channel is not None and not is_val_channel(before.channel) and before.channel != before.channel.guild.afk_channel and is_val_channel(
                after.channel):
            await ask_to_create_or_join_stack(member)
        if after.channel is not None and is_val_channel(before.channel) and not is_val_channel(after.channel) and after.channel != after.channel.guild.afk_channel:
            await asyncio.sleep(8)
            ask_to_leave_stack()
        if before.channel is not None:  # User left a voice channel
            if is_val_channel(before.channel):
                await channel_left_handler(member, before.channel)
        if after.channel is not None:  # User joined a voice channel
            await channel_joined_handler(member, after.channel)


async def channel_left_handler(member, channel):
    print(f'{member.name} left the voice channel {channel.name}')


async def channel_joined_handler(member, channel):
    print(f'{member.name} joined the voice channel {channel.name}')

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
