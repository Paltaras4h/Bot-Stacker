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
embed_color = 0x4ee21d


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

async def register(message, user):
    embed_time_zone = discord.Embed(title="Providing Time", description="What is your time now?")
    embed_time_zone.add_field(name="Your Time", value="Provide Your Current Time")

    await message.send(embed=embed_time_zone)

    utc = await ask_for_time(message, False)
    if utc:
        return await update_time(message, user, utc)
    else:
        return None

async def update_time(message, user, utc=None):
    embed_time_frame = discord.Embed(title="When Do You Want to Play?",
                                     description="Provide Start and End Times "
                                                 "of Your Game Session", colour=embed_color)
    embed_time_frame.add_field(name="Start Time", value="Enter Start Time in First Message")
    embed_time_frame.add_field(name="End Time", value="Enter End Time in Second Message")

    await message.send(embed=embed_time_frame)
    await message.send(f"__**Send Your Start Time:**__")
    time_from = await ask_for_time(message, True)
    if time_from:
        await message.send(f"__**Send Your End Time:**__")
        time_to = await ask_for_time(message, True)
        if time_to:
            return rep.set_user_time_frame(user, time_from, time_to, utc)

@bot.command()
async def go(message):
    user_id, user_name = message.author.id, message.author.name
    user = rep.get_user(user_id, user_name)

    if not user.default_time_from:
        user = await register(message, user)
        if not user:
            return
    else:
        embed_choose_time_option = discord.Embed(title="What Time Frame Do You Want to Use?",
                                                 description="Do you want to play during previously stated time or "
                                                             "you want to choose new time frame?",
                                                 colour=embed_color)
        view = View()

        async def keep_time_callback(interaction):
            await interaction.response.send_message("You have chosen to keep time frame")

        async def update_time_callback(interaction):
            await interaction.response.send_message("You have chosen to update time frame")

        keep_time_button = Button(label="Use Previous Time Frame", style=discord.ButtonStyle.blurple)
        keep_time_button.callback = keep_time_callback
        update_time_button = Button(label="Update Time Frame", style=discord.ButtonStyle.green)
        update_time_button.callback = update_time_callback

        view.add_item(keep_time_button)
        view.add_item(update_time_button)

        await message.send(embed=embed_choose_time_option, view=view)


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
async def send_list(interaction):

    embed_stacks_frame = discord.Embed(title="Choose a stack you want to join", colour=embed_color)

    buttons = []
    for i,stack in enumerate(rep.get_stacks()):
        embed_stacks_frame.add_field(name=f"{i+1}-{stack.name}", value="\n".join([user.name for user in rep.get_participants(stack)]))
        button = Button(label=f"{i+1}-{stack.name}", style=discord.ButtonStyle.green)

        async def but_callback(inter):
            rep.add_user_to_stack(rep.get_user(inter.user.id, inter.user.name), stack)#todo adjust stack timeline
            await inter.response.send_message("Added")
        button.callback = but_callback
        buttons.append(button)

    view = View()
    for but in buttons:
        view.add_item(but)

    await interaction.response.send_message(embed=embed_stacks_frame, view=view)


async def ask_to_create_or_join_stack(member):
    guild = member.guild
    channel = discord.utils.get(guild.text_channels, name='бот')#todo ask for general_chat when adding to server
    member_mention = member.mention

    view = View()

    async def create_stack(interaction):
        # TODO await go()
        rep.create_stack(User(member.id, member.name, datetime.now(), datetime.now().replace(hour=23)))
        await interaction.response.send_message("mnogogo hochesh")

    async def join_stack(interaction):
        await send_list(interaction)
        await interaction.response.send_message("mnogogo hochesh")

    create_but = Button(style=discord.ButtonStyle.primary, label="Create new stack",
                     custom_id="create_stack")
    create_but.callback = create_stack

    join_but = Button(style=discord.ButtonStyle.primary, label="Join existing stacks",
                        custom_id="join_stack")
    join_but.callback = join_stack

    view.add_item(create_but)
    if len(rep.get_stacks())!=0:
        create_but.style = discord.ButtonStyle.secondary
        view.add_item(join_but)

    embed = discord.Embed(title="You want to play? Let's play!", description=f"{member_mention}", color=embed_color)

    await channel.send(embed=embed, view=view)

async def ask_to_leave_stack(member):
    guild = member.guild
    channel = discord.utils.get(guild.text_channels, name='бот')  # todo ask for general_chat when adding to server
    member_mention = member.mention
    view = View()

    async def remove_from_stack(interaction):
        rep.remove_user_from_stacks(member.id)
        await interaction.response.send_message("# You should run!\nSuccessfully removed✔️")

    button1 = Button(style=discord.ButtonStyle.primary, label="Remove me from all stacks", custom_id="remove_from_stack")
    button1.callback = remove_from_stack

    view.add_item(button1)

    embed = discord.Embed(title="Watch them run!", description=f"{member_mention}\nDo you want to leave?", color=embed_color)

    await channel.send(embed=embed, view=view)

@bot.command()
async def t(ctx):
    pass
    # Create the view
    # view = View()
    #
    # # Define button callback functions
    # async def button1_callback(interaction):
    #     await interaction.response.send_message("Button 1 clicked!")
    #
    # async def button2_callback(interaction):
    #     await interaction.response.send_message("Button 2 clicked!")
    #
    # # Create the buttons and assign callback functions
    # # button1 = Button(style=discord.ButtonStyle.primary, label="Button 1", custom_id="button1")
    # # button1.callback = button1_callback
    # #
    # # button2 = Button(style=discord.ButtonStyle.secondary, label="Button 2", custom_id="button2")
    # # button2.callback = button2_callback
    # buts = [Button(style=discord.ButtonStyle.secondary, label=f"Button {i}", custom_id=f"button{i}") for i in range(20)]
    # # Add buttons to the view
    # # view.add_item(button1)
    # # view.add_item(button2)
    # for but in buts:
    #     view.add_item(but)

    # Send the view message
    #await ctx.send("Click a button:", view=view)


@bot.event
async def on_voice_state_update(member, before, after):
    # not val and not_afk_channel -> val ask2add
    # if user is in stack:
    #   val -> not_val and not_afk_channel -> wait(5sec) -> ask2leave

    if before.channel != after.channel:  # Check if channel changed
        is_val_channel = lambda c: "ВАЛЕРІЙ" in str(c) or "ВОЛЕРА🧑" in str(c)
        afk_channel = after.channel.guild.afk_channel if after.channel else before.channel.guild.afk_channel

        if not is_val_channel(before.channel) and before.channel != afk_channel and is_val_channel(
                after.channel):
            await ask_to_create_or_join_stack(member)
        if is_val_channel(before.channel) and not is_val_channel(after.channel) and after.channel != afk_channel:
            await asyncio.sleep(1)
            await ask_to_leave_stack(member)
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
