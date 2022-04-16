import asyncio
from dotenv import load_dotenv
import json
import nextcord
from nextcord.ext import commands
import os

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
bot = commands.Bot(command_prefix='!')

possible_artifacts = ['small trainer', 'large trainer', 
                      'small storage', 'large storage']


# Command is used to create a def call countdown channel
# Input format: !countdown "name" "amount" "time" "village link"
@commands.has_role('Admin') # Command requires Admin role
@bot.command(name='countdown')
async def countdown(ctx, name:str, troops:int, time:str, link:str):
    print('Countdown request received:', name, troops, time, link)
    json_path = './json_files/active_calls.json'

    # Create new countdown channel
    countdown_name = 'countdown-' + name
    category = nextcord.utils.get(ctx.guild.categories, name='countdown')
    if category is None:
        category = await ctx.guild.create_category_channel('countdown')
    channel = await ctx.guild.create_text_channel(countdown_name, category=category)
    await ctx.reply('#' + channel.name + ' has been created.')
    print(f'Created new channel id: {channel.id}')

    # Message to be sent in new channel
    role = nextcord.utils.get(ctx.guild.roles, name='def')
    msg = f'**Defense call: {name}**\
        \n**Defense amount: {troops}**\
        \n**Before: {time}**\
        \n**Send troops to:** {link}\
        \nPlease `!commit` the exact amount you are sending in this channel.\
        \nex: `!commit 10000`'
    await channel.send(f'{role.mention}\n' + msg)

    # Save countdown to json file
    if os.path.exists(json_path):
        with open(json_path) as json_file:
            active_calls = json.load(json_file)
    else:
        active_calls = {}

    active_calls[countdown_name] = {
        'troops': troops,
        'time': time,
        'link': link
    }

    with open(json_path, 'w') as json_file:
        json.dump(active_calls, json_file)

@countdown.error
async def countdown_error(ctx, error):
    if not isinstance(error, commands.MissingAnyRole):
        print(error)
        await ctx.reply('Incorrect format. To use this command correctly follow this example:\
        \n`!countdown "name-of-channel" "amount" "time" "link to village"`\
        \nNotes:\
        \n* "name-of-channel" must be dash seperated, do not use spaces.\
        \n* Do not use "quotation marks"')

# Command is used to commit troops to a defense call.
# Input format: !commit <int>
@bot.command(name='commit')
async def commit(ctx, troops:int):
    """Commit troops to def call"""
    json_path = './json_files/active_calls.json'
    channel_name = ctx.channel.name

    with open(json_path) as json_file:
        active_calls = json.load(json_file)

    if channel_name in active_calls.keys():
        # Retreive info from dict
        remaining = int(active_calls[channel_name]['troops']) - troops
        time = active_calls[channel_name]['time']
        link = active_calls[channel_name]['link']

        # If the call is not full
        if remaining > 0:
            await ctx.send(f'**{remaining}** remaining before **{time}**!\n{link}')
            active_calls[channel_name]['troops'] = remaining
            with open(json_path, 'w') as json_file:
                json.dump(active_calls, json_file)

        # If the call is filled, close comments and delete channel after 24 hours
        else:
            await ctx.send('🛡️ ⚔️ This defense call has been filled! ⚔️ 🛡️\
                \nThis channel is now closed and will be deleted in 24 hours.')
            perms = ctx.channel.overwrites_for(ctx.guild.default_role)
            perms.send_messages = False
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=perms)

            # Update active_calls.json
            active_calls.pop(channel_name)
            with open(json_path, 'w') as json_file:
                json.dump(active_calls, json_file)
            # Delete channel after 24 hours
            await asyncio.sleep(30) # 86400 seconds in 1 day
            await ctx.channel.delete()

@commands.has_role('Admin') # Command requires Admin role
@bot.command(name='add_artifact')
async def add_artifact(ctx, artifact:str, hours:int):
    # json_path = './json_files/artifacts.json'
    pass

@bot.event
async def on_ready():
    print(f'We have logged in as: {bot.user.name}')


if __name__ == '__main__':
    bot.run(TOKEN)
