import asyncio
from dotenv import load_dotenv
import json
import nextcord
from nextcord import Embed
from nextcord.ext import commands
import os


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = nextcord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot_role = 'Bot Master'

possible_artifacts = [
    'small-trainer', 'large-trainer', 'unique-trainer',
    'small-storage', 'large-storage'
]


# Command for setting the defense role for the server.
# This is required for creating countdowns
@commands.has_role(bot_role) # Requires bot privileges
@bot.command(name='def_role')
async def def_role(ctx, def_role:str):
    json_path = './json_files/server_info.json'
    server_id = str(ctx.guild.id)

    with open(json_path) as json_file:
        server_info = json.load(json_file)

    server_info[server_id]['def_role'] = def_role

    with open(json_path, 'w') as json_file:
        json.dump(server_info, json_file)

    embed = Embed(
        title=f'Defense role has been set: {def_role}',
        description='If this is incorrect, run the `!def_role` command again and specify the proper defense role.',
        color=nextcord.Color.green()
    )
    embed.add_field(
        name='Notes:',
        value='• Use the exact role name as it appears in your server. This is case sensitive.'
    )
    await ctx.reply(embed=embed)

@def_role.error
async def def_role_error(ctx, error):
    if not isinstance(error, commands.MissingRole):
        print(error)
        embed = Embed(
            title='Incorrect format',
            description='Please follow this example:\n' +
            '`!def_role "role"`',
            color=nextcord.Color.green()
        )
        embed.add_field(
            name='Notes:',
            value='• `"role"` is the name of the defense role within your specific Discord server.'
        )
        await ctx.reply(embed=embed)

# Command is used to create a def call countdown channel
# Input format: !countdown "name" "amount" "time" "village link"
@commands.has_role(bot_role) # Requires bot privileges
@bot.command(name='countdown')
async def countdown(ctx, name:str, troops:int, time:str, link:str):
    print(f'{ctx.author} has requested a countdown:', name, troops, time, link)
    json_path = './json_files/server_info.json'
    server_id = str(ctx.guild.id)

    # Ensure that the server has a designated def_role
    with open(json_path) as json_file:
        server_info = json.load(json_file)
        role_name = server_info[server_id]['def_role']

    if role_name is None:
        embed = Embed(
            title='Defense role not yet specified.',
            description='To specify a defense role, run the command `!def_role "role"`\n' +
            '• `"role"` is the name of the defense role within your specific Discord server.',
            color=nextcord.Color.green()
        )
        await ctx.reply(embed=embed)
        return

    # Create new countdown channel
    countdown_name = 'countdown-' + name
    category = nextcord.utils.get(ctx.guild.categories, name='countdown')
    if category is None:
        category = await ctx.guild.create_category_channel('countdown')
    channel = await ctx.guild.create_text_channel(countdown_name, category=category)
    print(f'Created new channel id: {channel.id}')

    embed = Embed(
        title='Countdown channel has been created.',
        description=f'{channel.mention}',
        color=nextcord.Color.green()
    )
    await ctx.reply(embed=embed)

    # Message to be sent in new channel
    role = nextcord.utils.get(ctx.guild.roles, name=role_name)
    embed = Embed(title=f'🛡️ ⚔️ NEW DEFENSE CALL ⚔️ 🛡️', description=f'{role.mention}', color=nextcord.Color.green())
    embed.add_field(name=f'Troops needed:', value=f'{troops}', inline=True)
    embed.add_field(name=f'Before:', value=f'{time}', inline=True)
    embed.add_field(name=f'Send troops to:', value=f'{link}', inline=True)
    embed.add_field(name='Please `!commit` the exact amount of troops (in crop) you are sending.', value='ex: `!commit 10000`', inline=False)
    await channel.send(embed=embed)

    # Save countdown to json file
    with open(json_path) as json_file:
        server_info = json.load(json_file)

    server_info[server_id]['active_calls'][countdown_name] = {
        'troops': troops,
        'time': time,
        'link': link
    }

    with open(json_path, 'w') as json_file:
        json.dump(server_info, json_file)

@countdown.error
async def countdown_error(ctx, error):
    if not isinstance(error, commands.MissingRole):
        print(error)
        embed = Embed(
            title='Incorrect format',
            description='Please follow this example:\n' +
                        '`!countdown "name-of-channel" "amount" "time" "link to village"`',
            color=nextcord.Color.green()
        )
        embed.add_field(
            name='Notes:',
            value='• `"name-of-channel"` must be dash seperated, do not use spaces.\n' +
                  '• Do not use "quotation marks".',
            inline=False
        )
        await ctx.reply(embed=embed)

# Command is used to commit troops to a defense call.
# Input format: !commit <int>
@bot.command(name='commit')
async def commit(ctx, troops:int):
    json_path = './json_files/server_info.json'
    channel_name = ctx.channel.name
    server_id = str(ctx.guild.id)

    with open(json_path) as json_file:
        server_info = json.load(json_file)

    if channel_name in server_info[server_id]['active_calls'].keys():
        # Retreive info from dict
        remaining = server_info[server_id]['active_calls'][channel_name]['troops'] - troops
        time = server_info[server_id]['active_calls'][channel_name]['time']
        link = server_info[server_id]['active_calls'][channel_name]['link']

        # If the call is not full
        if remaining > 0:
            embed = Embed(
                title=f'{ctx.author.name} has committed {troops} troops.',
                description=f'**{remaining}** remaining before **{time}**\n{link}',
                color=nextcord.Color.green()
            )
            await ctx.reply(embed=embed)
            server_info[server_id]['active_calls'][channel_name]['troops'] = remaining
            with open(json_path, 'w') as json_file:
                json.dump(server_info, json_file)

        # If the call is filled, close comments and delete channel after 24 hours
        else:
            embed = Embed(
                title='🛡️ ⚔️ This defense call has been filled! ⚔️ 🛡️',
                description='This channel is now closed and will be deleted in 24 hours.',
                color=nextcord.Color.green()
            )
            await ctx.send(embed=embed)
            perms = ctx.channel.overwrites_for(ctx.guild.default_role)
            perms.send_messages = False
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=perms)

            # Update active_calls.json
            server_info[server_id]['active_calls'].pop(channel_name)
            with open(json_path, 'w') as json_file:
                json.dump(server_info, json_file)

            # Delete channel after 24 hours
            await asyncio.sleep(86400) # 86400 seconds in 1 day
            print(f'{channel_name} has been deleted.')
            await ctx.channel.delete()

# Adds an artifact for a server & create associated channel
# Input format: !add_artifact <artifact_name>
@commands.has_role(bot_role) # Requires bot privileges
@bot.command(name='add_artifact')
async def add_artifact(ctx, artifact:str, hours:int):
    json_path = './json_files/server_info.json'
    server_id = str(ctx.guild.id)

    print(f'{ctx.author} has requested to add an artifact: {artifact} {hours}')

    if artifact not in possible_artifacts:
        raise commands.BadArgument()

    with open(json_path) as json_file:
        server_info = json.load(json_file)
    artifacts = server_info[server_id]['artifacts']

    new_info = {
        'hours': hours,
        'current_owner': '',
        'prev_owners': []
    }

    # If it is the first artifact for the server
    if len(artifacts) == 0:
        new_artifact = artifact + '-1'
        artifacts[new_artifact] = new_info
    
    # Add new entry to artifact dict with an integer label for creating channels
    # Adds 1 to every repeated artifact
    else:
        for i in range(len(artifacts) + 1):
            new_artifact = artifact + '-' + str(i + 1)
            if new_artifact not in artifacts.keys():
                artifacts[new_artifact] = new_info
                break

    category = nextcord.utils.get(ctx.guild.categories, name='artifacts')
    if category is None:
        category = await ctx.guild.create_category_channel('artifacts')
    channel = await ctx.guild.create_text_channel(new_artifact, category=category)
    print(f'Created new channel id: {channel.id}')

    embed = Embed(
        title='Artifact channel has been created.',
        description=f'{channel.mention}',
        color=nextcord.Color.dark_gold()
    )
    embed.add_field(
        name='May be held for:',
        value=f'{hours} hours'
    )
    embed.add_field(
        name='To change the hours held:',
        value='run `!update_artifact "channel-name" "new-hour-amount"`',
        inline=False
    )
    await ctx.reply(embed=embed)

    # Update json file
    server_info[server_id]['artifacts'] = artifacts
    with open(json_path, 'w') as json_file:
        json.dump(server_info, json_file)

@add_artifact.error
async def add_artifact_error(ctx, error):
    # If the user has chosen an artifact which is not in the list of possible artifacts
    # Or if user has the required role, but has thrown an error
    print(error)
    if not isinstance(error, commands.MissingRole):
        embed = Embed(
            title='Incorrect format',
            description='Please follow this example:\n`!add_artifact "artifact-name" "number of hours"`',
            color=nextcord.Color.dark_gold()
        )
        embed.add_field(
            name='Notes:',
            value='• `"artifact-name"` must be dash seperated.\n' +
                  '• `"number of hours"` is the number of hours this artifact may be held before the owner is notified to give to the next person.',
                  inline=False
        )
        embed.add_field(
            name='Available artifacts are:',
            value='• ' + '\n• '.join(possible_artifacts)
        )
        await ctx.reply(embed=embed)

# Updates the # of hours that an artifact may be held
# Input format: !update_artifact <channel_name> <hours>
@commands.has_role(bot_role)
@bot.command(name='update_artifact')
async def update_artifact(ctx, channel_name:str, hours:int):
    json_path = './json_files/server_info.json'
    server_id = str(ctx.guild.id)

    print(
        f'{ctx.author} has requested to update an artifact: {channel_name}\n\tNew hours: {hours}')

    channel = nextcord.utils.get(ctx.guild.channels, name=channel_name)
    if channel is None:
        raise commands.BadArgument

    with open(json_path) as json_file:
        server_info = json.load(json_file)
    artifacts = server_info[server_id]['artifacts']
    artifacts[channel_name]['hours'] = hours
    server_info[server_id]['artifacts'] = artifacts

    with open(json_path, 'w') as json_file:
        json.dump(server_info, json_file)

    embed = Embed(
        title=f'Artifact: {channel_name} has been updated.',
        description=f'New hours: {hours}',
        color=nextcord.Color.dark_gold()
    )
    await ctx.reply(embed=embed)

@update_artifact.error
async def update_artifact_error(ctx, error):
    print(error)
    if not isinstance(error, commands.MissingRole):
        embed = Embed(
            title='Error updating artifact',
            description='Please follow this example:\n`!update_artifact "channel-name" "hours"`',
            color=nextcord.Color.dark_gold()
        )
        embed.add_field(
            name='Notes:',
            value='• `"channel-name"` must be the exact name of the channel.\n' +
                  '• `"hours"` is the number of hours that an artifact may be held before the owner is notified to give it to the next player.'
        )
        await ctx.reply(embed=embed)

# Removes an artifact from a server & deletes the associated channel
# Input format: !remove_artifact <channel_name>
@commands.has_role(bot_role) # Requires bot privileges
@bot.command(name='remove_artifact')
async def remove_artifact(ctx, artifact:str):
    json_path = './json_files/server_info.json'
    server_id = str(ctx.guild.id)

    print(f'{ctx.author} has requested to remove an artifact: {artifact}')

    with open(json_path) as json_file:
        server_info = json.load(json_file)
    artifacts = server_info[server_id]['artifacts']

    if artifact not in artifacts.keys():
        raise commands.BadArgument

    artifacts.pop(artifact)
    server_info[server_id]['artifacts'] = artifacts
    with open(json_path, 'w') as json_file:
        json.dump(server_info, json_file)
    
    channel = nextcord.utils.get(ctx.guild.channels, name=artifact)
    await channel.delete()
    
    embed = Embed(
        title='Artifact channel has been deleted.',
        description=f'~~{artifact}~~',
        color=nextcord.Color.dark_gold()
    )
    await ctx.reply(embed=embed)
    
    print(f'{artifact} has been removed and the channel deleted')

@remove_artifact.error
async def remove_artifact_error(ctx, error):
    print(error)
    if not isinstance(error, commands.MissingRole):
        embed = Embed(
            title='Error removing artifact',
            description='Please follow this example:\n`!remove_artifact "channel-name"`',
            color=nextcord.Color.dark_gold()
        )
        embed.add_field(
            name='Notes:',
            value='• `"channel-name"` must be the exact name of the channel.\n' +
                  '• `"channel-name"` should be all lowercase.'
        )
        await ctx.reply(embed=embed)

@bot.event
async def on_guild_join(ctx):
    print(f'{ctx.owner} has invited {bot.user.name} to the server: {ctx}')

    json_path = './json_files/server_info.json'
    
    with open(json_path) as json_file:
        server_info = json.load(json_file)
    
    server_info[str(ctx.id)] = {
        'server_name': ctx.name,
        'def_role': None,
        'active_calls': {},
        'artifacts': {}
    }

    with open(json_path, 'w') as json_file:
        json.dump(server_info, json_file)

    embed = Embed(
        title=f'Thank you for inviting {bot.user.name} to your server!',
        color=nextcord.Color.dark_gold()
    )
    embed.add_field(
        name='Tips:',
        value='• It is recommended to create a private channel for writing bot commands, so that general channels are not spammed with bot responses.\n' +
        '• To use some bot commands (such as `!countdown`), the `Bot Master` role is required.\n' +
        '• Ensure that all users who are allowed to manage the bot are assigned the role `Bot Master`.\n' +
        '• Please run the `!def_role` command to set the name of your defender role for your server. ex: `Def`, `Defender`, `Defense`\n',
        inline=False
    )
    embed.add_field(
        name='For a full list of commands, please refer to the bot documentation',
        value='https://github.com/kyle-gross/discord-bot/blob/master/README.md'
    )
    await ctx.owner.send(embed=embed)

@bot.event
async def on_guild_remove(ctx):
    json_path = './json_files/server_info.json'

    with open(json_path) as json_file:
        server_info = json.load(json_file)

    server_info.pop(str(ctx.id))

    with open(json_path, 'w') as json_file:
        json.dump(server_info, json_file)

@bot.event
async def on_ready():
    print(f'We have logged in as: {bot.user.name}')


if __name__ == '__main__':
    bot.run(TOKEN)
