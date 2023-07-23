import asyncio
import inspect

import discord
from discord import SelectOption
from discord.ext import commands, tasks
from discord.ui import View, Button, Select
import os
import json
from Models.User import User
from Models.Stack import Stack
import Database.Repository as rep
from datetime import datetime, timedelta, timezone
embed_color = 0x4ee21d

bot_token = None
try:
    with open(os.getcwd()+'/venv/configuration.json') as f:
        bot_token = json.load(f)['botApiToken']
except FileNotFoundError:
    print("Configuration file not found, trying to access environment variables...")
    bot_token= os.environ.get("botApiToken")

# Create an instance of the bot
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Event: Bot is ready and connected to the server
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    print('------')
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    user_time_check.start()

async def ask_for_time(messageable, dt_utc): #messageable = message or interaction
    user = messageable.author if type(messageable) == discord.Message else messageable.user

    def check(msg):
        return msg.author.id == user.id and msg.channel == user.dm_channel

    field1_response = None
    response1 = None
    while True:
        try:
            # Waiting for the user's response
            response1 = await bot.wait_for('message', check=check, timeout=30)

            # Retrieving the user's response
            field1_response = response1.content

        except asyncio.TimeoutError:
            await send_message(user, "__**Response timed out**__")
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
                await send_message(user, "__**I could not understand what time you have given, could you try once "
                                         "more**__")
                continue
        except ValueError:
            await send_message(user, "__**I could not understand what time you have given, could you try once "
                               "more**__")

async def register(inter, user):
    embed_time_zone = discord.Embed(title="Initiated!", description=f"What is your time now?")
    embed_time_zone.add_field(name="Your Time", value="Provide Your Current Time")

    # channel = await send_message(inter.user, embed=embed_time_zone)
    await inter.user.send(embed=embed_time_zone)

    utc = await ask_for_time(inter, False)
    if utc:
        return await update_time(inter, user, utc)
    else:
        return None

async def update_time(messageable, user, utc=None, interaction=None):
    embed_time_frame = discord.Embed(title="**Come on, let’s go!**",
                                     description=f"{messageable.user.mention}, Provide Start and End Times "
                                                 "of Your Game Session", colour=embed_color)
    embed_time_frame.add_field(name="Start Time", value="Enter Start Time in First Message")
    embed_time_frame.add_field(name="End Time", value="Enter End Time in Second Message")

    await send_message(messageable.user, embed=embed_time_frame)
    await send_message(messageable.user, f"__**Send Your Start Time:**__")
    task_message = asyncio.create_task(ask_for_time(messageable, True))
    task_button = asyncio.create_task(now(messageable, user))
    done, _ = await asyncio.wait([task_button, task_message], return_when=asyncio.FIRST_COMPLETED)
    task_completed = done.pop()
    time_from = await task_completed
    for task in done:
        task.cancel()
    if time_from:
        if task_completed == task_message:
            if utc:
                time_from -= timedelta(hours=utc)
            else:
                time_from -= timedelta(hours=user.UTC)
        await send_message(messageable.user, f"__**Send Your End Time:**__")
        time_to = await ask_for_time(messageable, True)
        if time_to:
            if utc:
                time_to -= timedelta(hours=utc)
            else:
                time_to -= timedelta(hours=user.UTC)
            await send_message(messageable.user, "__**Time was successfully updated**__")
            return rep.set_user_time_frame(user, time_from, time_to, utc)
    print("Damn it")

async def now(messageable, user):
    view = View()
    loop = asyncio.get_event_loop()
    button_clicked = loop.create_future()

    now_button = Button(label="Now", style=discord.ButtonStyle.green)

    async def now_callback(interaction):
        if interaction.user.id == user.id:
            now_button.disabled = True
            await interaction.response.edit_message(view=view)
            button_clicked.set_result(True)

    now_button.callback = now_callback
    view.add_item(now_button)

    # await send_message(messageable, view=view)
    await messageable.user.send(view=view)

    try:
        await asyncio.wait_for(button_clicked, timeout=30)
        return datetime.now(timezone.utc).replace(tzinfo=None, second=0, microsecond=0)

    except asyncio.TimeoutError:
        pass

async def notify_about_created_stack(messageable, interaction, _stack):
    guild = messageable.guild
    channel = guild.system_channel
    view1 = View()
    button = Button(label="Join", style=discord.ButtonStyle.green)
    button.callback = create_join_leave_callback(channel, _stack, True)

    embed_notify_all_created_stack = discord.Embed(title="New stack has been created!",
                                                   description=f"{interaction.user.name} created a new stack "
                                                               f"{get_discord_time(_stack.lifetime_from)}-{get_discord_time(_stack.lifetime_to)}\n"
                                                               f"sabaka evrivan",#todo @everyone
                                                   colour=embed_color)
    view1.add_item(button)
    await send_message(channel, embed=embed_notify_all_created_stack, view=view1)

async def time_option_choice(messageable, user, join_create, stack=None, interaction=None):
    embed_choose_time_option = discord.Embed(title="Here comes the party!",
                                             description=f"{messageable.guild.get_member(user.id).mention}"
                                                         f", Do you want to play during "
                                                         f"previously stated time or you want to choose new time "
                                                         f"frame?",
                                             colour=embed_color)
    embed_choose_time_option.add_field(name="Keep Time Frame",
                                       value=f"Use Time Frame: {discord.utils.format_dt(user.default_time_from.replace(tzinfo=timezone.utc), style='t')} - "
                                             f"{discord.utils.format_dt(user.default_time_to.replace(tzinfo=timezone.utc), style='t')}")
    embed_choose_time_option.add_field(name="Update Time Frame",
                                       value="Provide new time frame and use it to create/join a stack")
    view = View()
    keep_time_button = Button(label="Keep Time Frame", style=discord.ButtonStyle.blurple)
    update_time_button = Button(label="Update Time Frame", style=discord.ButtonStyle.green)

    async def keep_time_callback(interaction):
        if interaction.user.id == user.id:
            keep_time_button.disabled = True
            update_time_button.disabled = True
            await interaction.response.edit_message(view=view)
            if not join_create:
                _stack = rep.create_stack(user)
                embed_created_stack = discord.Embed(title="Here We Go!",
                                                    description="Stack with KEPT time frame was created",
                                                    colour=embed_color)
                await send_message(messageable.user, embed=embed_created_stack)
                await notify_about_created_stack(messageable, interaction, _stack)
            else:
                if user.default_time_to < stack.lifetime_from:
                    await send_message(messageable.user, f"**{user.name}, your time ends before the stack starts "
                                                    f"{get_discord_time(stack.lifetime_from)}, "
                                                    f"create a new stack or join another**")
                else:
                    rep.add_user_to_stack(user, stack)
                    await send_message(messageable, f"**Successfully added {interaction.user.mention} to"
                                                    f" __{stack.name}__ stack**")

    async def update_time_callback(interaction):
        if interaction.user.id == user.id:
            keep_time_button.disabled = True
            update_time_button.disabled = True
            await interaction.response.edit_message(view=view)
            user_updated = await update_time(messageable, user, interaction=interaction)
            if user_updated:
                if not join_create:
                    _stack = rep.create_stack(user_updated)
                    embed_created_stack = discord.Embed(title="Here We Go!",
                                                        description="Stack with UPDATED time frame was created",
                                                        colour=embed_color)
                    await send_message(messageable.user, embed=embed_created_stack)
                    await notify_about_created_stack(messageable, interaction, _stack)
                else:
                    if user.default_time_to < stack.lifetime_from:
                        await send_message(messageable.user, f"**{user.name}, your time ends before the stack starts "
                                                        f"{get_discord_time(stack.lifetime_from)}, create a new stack"
                                                        f" or join another**")
                    else:
                        rep.add_user_to_stack(user, stack)
                        await send_message(messageable, f"**Successfully added {interaction.user.mention} to"
                                                        f" __{stack.name}__ stack**")

    keep_time_button.callback = keep_time_callback
    update_time_button.callback = update_time_callback

    view.add_item(keep_time_button)
    view.add_item(update_time_button)

    if interaction:
        await send_message(interaction.user, embed=embed_choose_time_option, view=view)
    else:
        await send_message(messageable.user, embed=embed_choose_time_option, view=view)

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


def get_discord_time(datetime):
    return discord.utils.format_dt(datetime.replace(tzinfo=timezone.utc), style='t')

def get_function_defaults(func):
    signature = inspect.signature(func)
    default_values = {}
    for param_name, param in signature.parameters.items():
        if param.default is not inspect.Parameter.empty:
            default_values[param_name] = param.default
    return default_values

def get_user_from_messageable(messageable):
    """
    :param messageable: discord.abc.Messageable abstract class: message, interaction, member
    :exception TypeError: Passed parameter does not implement discord.abc.Messageable or have no user attributes
    :return: User object
    """
    user = None
    if type(messageable) == discord.Member:
        user = messageable
    else:
        try:
            user = messageable.author # message
        except AttributeError:
            try:
                user = messageable.user # interaction
            except AttributeError:
                raise TypeError("Passed parameter does not implement discord.abc.Messageable or have no user attributes")

    return rep.get_user(user.id, user.name)

async def send_message(messageable, message=None, embed=None, view=None):
    """
    :param messageable: discord.abc.Messageable abstract class: message, interaction
    :exception TypeError: Passed parameter does not implement discord.abc.Messageable or have no send message functions
    :return Channel: if messageable is interaction
    """
    try:
        defaults = get_function_defaults(messageable.send)
        await messageable.send(message,embed=embed if embed else defaults['embed'],
                               view=view if view else defaults['view'])
    except AttributeError:
        try:
            defaults = get_function_defaults(messageable.response.send_message)
            await messageable.response.send_message(message,
                                                    embed=embed if embed else defaults['embed'],
                                                    view=view if view else defaults['view'])
            return messageable.channel
        except AttributeError as e:
            raise TypeError("Passed parameter does not implement discord.abc.Messageable or have no send message funcs")
        except discord.errors.InteractionResponded:
            defaults = get_function_defaults(messageable.channel.send)
            await messageable.channel.send(message,
                                           embed=embed if embed else defaults['embed'],
                                           view=view if view else defaults['view'])

@bot.tree.command(name="go", description="YOU WANT TO PLAY? Create or join stack")
async def go(inter: discord.Interaction):
    user_id, user_name = inter.user.id, inter.user.name
    user = rep.get_user(user_id, user_name)

    if not user.default_time_from:
        user = await register(inter, user)
        if not user:
            return
    else:
        await ask_to_create_or_join_stack(inter)

@bot.tree.command(name="join", description="YOU WANT TO PLAY? Join stack")
async def join(inter: discord.Interaction):
    if len(rep.get_stacks()) != 0:
        await send_list(inter)
    else:
        await send_message(inter, "**There are no stacks currently available, but you can always create one, using**"
                                  " `/go`")

@bot.tree.command(name="q", description="Leave all stacks")
async def q(inter: discord.Interaction):
    await remove_user_from_stacks(inter, inter.user)

@bot.tree.command(name="quit", description="Leave all stacks")
async def quit(inter: discord.Interaction):
    await remove_user_from_stacks(inter, inter.user)

@bot.tree.command(name="leave", description="Leave a stack")
async def leave(inter: discord.Interaction):
    if len(rep.get_stacks()) != 0:
        embed_leave_stack = discord.Embed(title="Which stack do you want to leave?", colour=embed_color)
        view = View()
        buttons = []

        for i, stack in enumerate(rep.get_stacks()):
            participants = rep.get_participants(stack)
            participants_lines = '\n'.join([f"{k+1}. {part.name}" for k, part in enumerate(participants)])
            embed_leave_stack.add_field(name=f"{i+1}. {stack.name} {get_discord_time(stack.lifetime_from)} - "
                                             f"{get_discord_time(stack.lifetime_to)}", value=participants_lines)
            leave_button = Button(label=f"{i+1}. {stack.name}", style=discord.ButtonStyle.green)

            leave_button.callback = create_join_leave_callback(inter, stack, False)
            view.add_item(leave_button)

        leave_all_button = Button(label="Leave all stacks", style=discord.ButtonStyle.blurple)

        async def leave_all_callback(interaction):
            user = get_user_from_messageable(interaction)
            playing_users = rep.get_playing_users()
            accept = False
            for fetched_user in playing_users:
                if user.id == fetched_user.id:
                    accept = True
                    break
            if accept:
                rep.remove_user_from_stacks(user)
                await interaction.response.send_message(f"**__{interaction.user.mention}__ has successfully left all the "
                                                        f"stacks**")
            else:
                await interaction.response.send_message(f"**{interaction.user.mention}, you were not participating in any "
                                                        f"stacks**")

        leave_all_button.callback = leave_all_callback
        view.add_item(leave_all_button)

        await send_message(inter, embed=embed_leave_stack, view=view)
    else:
        await send_message(inter, f"**{inter.user.mention}, There are no running stacks now**")

# Command: !htolox
@bot.tree.command(name="htolox", description="Prints who is lox")
async def htolox(inter: discord.Interaction):
    await send_message(inter, "pavel")

@bot.tree.command(name="register_bot", description="Choosing a chat for bot messages")
async def register_bot_command(inter: discord.Interaction):
    await register_bot(inter)

@bot.tree.command(name="register", description="Change or set your UTC time zone")
async def register_user(inter: discord.Interaction):
    await register(inter, get_user_from_messageable(inter))


async def register_bot(messageable):
    channel = None
    if type(messageable) == discord.Guild:
        guild = messageable
        channel = guild.system_channel
    elif type(messageable) == discord.TextChannel:
        guild = messageable.guild
        channel = messageable
    elif type(messageable) == discord.Interaction:
        guild = messageable.guild
    else:
        raise TypeError("Unsupported messageable")

    text_channels = [channel for channel in guild.channels if isinstance(channel, discord.TextChannel)]

    # Create a list of channel names and their corresponding IDs for the select menu
    options = [discord.SelectOption(label=channel.name, value=str(channel.id)) for channel in text_channels]

    # Create the select menu
    select = discord.ui.Select(placeholder="Select a channel for bot messages", options=options)

    async def select_menu_callback(interaction):
        selected_channel = discord.utils.get(guild.text_channels, id=int(select.values[0]))
        if selected_channel:
            await interaction.response.send_message(f"Bot messages will be sent to {selected_channel.mention}.")
            rep.get_server(guild.id, guild.name, selected_channel.id)
        else:
            await interaction.response.send_message("Channel not found.")

    select.callback = select_menu_callback

    view = View()
    view.add_item(select)
    await channel.send(view=view) if channel else await send_message(messageable, view=view)

pause_check = asyncio.Event()
pause_check.clear()
@tasks.loop(seconds=30)
async def user_time_check():
    for guild in bot.guilds:
        if not pause_check.is_set():
            channel = rep.get_bot_channel(guild)
            playing_users = rep.get_playing_users()
            dt_now = datetime.now(timezone.utc).replace(tzinfo=None)
            for user in playing_users:
                if user.default_time_to <= dt_now:
                    member = guild.get_member(user.id)
                    embed_time_is_up = discord.Embed(title="Your Time has Expired",
                                                     description=f"**{member.mention}, your stated time is up, do you "
                                                                 f"want to add more time or leave all stacks?**")
                    view = View()
                    buttons = [Button(label="+30 mins", style=discord.ButtonStyle.green),
                               Button(label="+1 hour", style=discord.ButtonStyle.green),
                               Button(label="Leave all stacks", style=discord.ButtonStyle.blurple)]

                    add_thirty_callback, add_hour_callback, leave_all_callback = \
                        add_thirty_hour_leave_callbacks(user, channel, view, buttons)

                    buttons[0].callback = add_thirty_callback
                    buttons[1].callback = add_hour_callback
                    buttons[2].callback = leave_all_callback

                    view.add_item(buttons[0])
                    view.add_item(buttons[1])
                    view.add_item(buttons[2])

                    await channel.send(embed=embed_time_is_up, view=view)
                    pause_check.set()


@user_time_check.before_loop
async def before_user_time_check():
    await bot.wait_until_ready()  # Wait for the bot to be ready before starting the task
    print("Background task is now running!")

def add_thirty_hour_leave_callbacks(user, channel, view, buttons):

    async def add_thirty_callback(interaction):
         if interaction.user.id == user.id:
            buttons[0].disabled = True
            await interaction.response.edit_message(view=view)
            user.default_time_to += timedelta(minutes=30)
            rep.set_user_time_frame(user, user.default_time_from, user.default_time_to)
            pause_check.clear()
            await send_message(interaction.user, f"Your End Time now is {get_discord_time(user.default_time_to)}")

    async def add_hour_callback(interaction):
        if interaction.user.id == user.id:
            buttons[1].disabled = True
            await interaction.response.edit_message(view=view)
            user.default_time_to += timedelta(hours=1)
            rep.set_user_time_frame(user, user.default_time_from, user.default_time_to)
            pause_check.clear()
            await send_message(interaction.user, f"Your End Time now is {get_discord_time(user.default_time_to)}")

    async def leave_all_callback(interaction):
        rep.remove_user_from_stacks(user)
        await interaction.response.send_message(f"**{interaction.user.mention} has successfully left all the stacks**")

    return add_thirty_callback, add_hour_callback, leave_all_callback

async def send_list(messageable):
    embed_stacks_frame = discord.Embed(title="Let's turn the tide!", description=f"Choose a stack you want to join",
                                       colour=embed_color)

    buttons = []
    for i, stack in enumerate(rep.get_stacks()):
        participants = rep.get_participants(stack)
        users_time_to = [user.default_time_to for user in participants]
        field_rows = [f"{i+1}.{user.name}" for i, user in enumerate(participants)]
        users_count = len(users_time_to)
        nearest_users_count = 5 - users_count # a count of users that are required to fill a stack to max players
        far_users_count = 5 - users_count
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if now >= stack.lifetime_from:
            near_delta = timedelta(minutes=35)
            far_delta = timedelta(hours=1, minutes=10)
            h_time_to_nearest_free_place = None
            m_time_to_nearest_free_place = 0
            h_time_to_far_free_place = None
            m_time_to_far_free_place = 0
            for time in users_time_to:
                if time < stack.lifetime_to + timedelta(minutes=35):
                    nearest_users_count += 1
                    delta = time - now
                    if delta <= near_delta:
                        hours = delta.total_seconds() // 3600
                        h_time_to_nearest_free_place = None if hours == 0 else int(hours)
                        m_time_to_nearest_free_place = int((delta.total_seconds() // 60) % 60)
                elif time < stack.lifetime_to + timedelta(hours=1, minutes=10):
                    far_users_count += 1
                    delta = time - now
                    if delta < far_delta:
                        hours = delta.total_seconds() // 3600
                        h_time_to_far_free_place = None if hours == 0 else int(hours)
                        m_time_to_far_free_place = int((delta.total_seconds() // 60) % 60)

            field_rows += [
                f"**need {nearest_users_count} in {f'{h_time_to_nearest_free_place}h' if h_time_to_nearest_free_place else ''}"
                f'{f"{m_time_to_nearest_free_place}m**±20min" if m_time_to_nearest_free_place != 0 else "NOW**"}'
                if 3 > nearest_users_count > 0 else "",
                f"**need {far_users_count} in {f'{h_time_to_far_free_place}h' if h_time_to_far_free_place else ''}"
                f'{f"{m_time_to_far_free_place}m**±20min" if m_time_to_far_free_place != 0 else "NOW**"}'
                if 3 > far_users_count > 0 else ""
            ]
        if users_count < 5:
            field_rows+=[f"__**{5 - users_count} to full stack**__"]
        field_value = "\n".join(field_rows)
        embed_stacks_frame.add_field(name=f"{i+1}-{stack.name} {get_discord_time(stack.lifetime_from)}-"
            f"{get_discord_time(stack.lifetime_to)}", value=field_value)
        button = Button(label=f"{i+1}-{stack.name}", style=discord.ButtonStyle.green)

        button.callback = create_join_leave_callback(messageable, stack, True)
        buttons.append(button)

    view = View()
    for but in buttons:
        view.add_item(but)
    await send_message(messageable, embed=embed_stacks_frame, view=view)


def create_join_leave_callback(messageable, _stack, join_leave):
    if join_leave:
        async def dynamic_callback(inter):
            user = get_user_from_messageable(inter)
            if rep.user_participates_in(user, _stack):
                await inter.response.send_message(f"{inter.user.mention}, You have already joined this stack.")
            else:
                await time_option_choice(messageable, user, True, _stack, interaction=inter)
    else:
        async def dynamic_callback(inter):
            user = get_user_from_messageable(inter)
            if rep.user_participates_in(user, _stack):
                rep.remove_user_from_stack(user, _stack)
                await inter.response.send_message(f"**__{inter.user.mention}__ has successfully left __{_stack.name}__ "
                                                  f"stack**")
            else:
                await inter.response.send_message(f"**Эу, тебя итак в этом стаке нету, дядя**")

    return dynamic_callback

async def ask_to_create_or_join_stack(messageable):
    member = None
    if type(messageable) == discord.Member:
        member = messageable # member
        guild = member.guild
        channel = rep.get_bot_channel(guild)
        member_mention = member.mention
    elif type(messageable) == discord.Message:
        message = messageable # message
        channel = message.channel
        member_mention = message.author.mention
    elif type(messageable) == discord.Interaction:
        channel = messageable.channel
        member_mention = messageable.user.mention
    else: raise TypeError("Unsupported messageable")

    view = View()
    create_but = Button(style=discord.ButtonStyle.green, label="Create new stack",
                        custom_id="create_stack")
    join_but = Button(style=discord.ButtonStyle.green, label="Join existing stacks",
                      custom_id="join_stack")

    async def create_stack(interaction):
        clicking_user = get_user_from_messageable(member if member else messageable)
        if interaction.user.id == clicking_user.id:
            create_but.disabled = True
            join_but.disabled = True
            await interaction.response.edit_message(view=view)
            await time_option_choice(messageable, clicking_user, False)

    async def join_stack(interaction):
        if interaction.user.id == get_user_from_messageable(member if member else messageable).id:
            create_but.disabled = True
            join_but.disabled = True
            await interaction.response.edit_message(view=view)
            await send_list(messageable)

    create_but.callback = create_stack

    join_but.callback = join_stack

    view.add_item(create_but)
    if len(rep.get_stacks()) != 0:
        create_but.style = discord.ButtonStyle.secondary
        view.add_item(join_but)

    embed = discord.Embed(title="You want to play? Let's play!", description=f"{member_mention}", color=embed_color)

    await send_message(messageable, embed=embed, view=view) if not member else await channel.send(embed=embed, view=view)

async def remove_user_from_stacks(messageable, user):
    rep.remove_user_from_stacks(user.id)
    await send_message(messageable, f"# You should run!\nSuccessfully removed {user.name} from all stacks✔️")

async def ask_to_leave_stack(member):
    guild = member.guild
    channel = rep.get_bot_channel(guild)
    member_mention = member.mention
    view = View()

    async def remove_from_stack(interaction):
        await remove_user_from_stacks(interaction, member)

    button1 = Button(style=discord.ButtonStyle.green, label="Remove me from all stacks", custom_id="remove_from_stack")
    button1.callback = remove_from_stack

    view.add_item(button1)

    embed = discord.Embed(title="Watch them run!", description=f"{member_mention}\nDo you want to leave all the stacks"
                                                               f" you are in?", color=embed_color)

    await channel.send(embed=embed, view=view)

@bot.command()
async def t(ctx):
    await ask_to_create_or_join_stack(ctx)


@bot.event
async def on_voice_state_update(member, before, after):
    # not val and not_afk_channel -> val ask2add
    # if user is in stack:
    #   val -> not_val and not_afk_channel -> wait(5sec) -> ask2leave

    if before.channel != after.channel:  # Check if channel changed
        is_val_channel = lambda c: "ВАЛЕРІЙ" in str(c) or "ВОЛЕРА" in str(c)
        afk_channel = after.channel.guild.afk_channel if after.channel else before.channel.guild.afk_channel

        if not is_val_channel(before.channel) and before.channel != afk_channel and is_val_channel(
                after.channel):
            await ask_to_create_or_join_stack(member)
        if is_val_channel(before.channel) and not is_val_channel(after.channel) and after.channel != afk_channel:
            await asyncio.sleep(7)
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

# Event: Bot joins a server
@bot.event
async def on_guild_join(guild):
    print(f"Joined {guild.id}:{guild.name} server!")
    await guild.system_channel.send("Hello! Register the bot please:")
    await register_bot(guild)

if bot_token:
    bot.run(bot_token)
else:
    raise ConnectionError("Failed to get bot token from configuration file or env variable")
