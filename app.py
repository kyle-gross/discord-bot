import asyncio
from dotenv import load_dotenv
import json
import nextcord
from nextcord.ext import commands
import os

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')
possible_artifacts = ['small-trainer', 'large-trainer', 'small-storage', 'large-storage']


# Command is used to create a def call countdown channel
# Input format: !countdown "name" "amount" "time" "village link"
@commands.has_role('Admin') # Command requires Admin role
@bot.command(name='countdown')
async def countdown(ctx, name:str, troops:int, time:str, link:str):
    print(f'{ctx.author} has requested a countdown:', name, troops, time, link)
    json_path = './json_files/active_calls.json'

    # Create new countdown channel
    countdown_name = 'countdown-' + name
    category = nextcord.utils.get(ctx.guild.categories, name='countdown')
    if category is None:
        category = await ctx.guild.create_category_channel('countdown')
    channel = await ctx.guild.create_text_channel(countdown_name, category=category)
    print(f'Created new channel id: {channel.id}')

    embed = nextcord.Embed(
        title='Countdown channel has been created.',
        description=f'{channel.mention}',
        color=nextcord.Color.green()
    )
    await ctx.reply(embed=embed)

    # Message to be sent in new channel
    role = nextcord.utils.get(ctx.guild.roles, name='def')
    embed = nextcord.Embed(title=f'🛡️ ⚔️ NEW DEFENSE CALL ⚔️ 🛡️', description=f'{role.mention}', color=nextcord.Color.green())
    embed.add_field(name=f'Troops needed:', value=f'{troops}', inline=True)
    embed.add_field(name=f'Before:', value=f'{time}', inline=True)
    embed.add_field(name=f'Send troops to:', value=f'{link}', inline=True)
    embed.add_field(name='Please `!commit` the exact amount of troops (in crop) you are sending.', value='ex: `!commit 10000`', inline=False)
    await channel.send(embed=embed)

    # Save countdown to json file
    with open(json_path) as json_file:
        active_calls = json.load(json_file)
    
    active_calls[countdown_name] = {
        'troops': troops,
        'time': time,
        'link': link
    }

    with open(json_path, 'w') as json_file:
        json.dump(active_calls, json_file)

@countdown.error
async def countdown_error(ctx, error):
    if not isinstance(error, commands.MissingRole):
        print(error)
        embed = nextcord.Embed(
            title='Incorrect format',
            description='Please follow this example:\n' +
                '`!countdown "name-of-channel" "amount" "time" "link to village"`',
            color=nextcord.Color.green()
        )
        embed.add_field(
            name='Notes:',
            value='• "name-of-channel" must be dash seperated, do not use spaces.\n' +
                  '• Do not use "quotation marks".',
            inline=False
        )
        await ctx.reply(embed=embed)

# Command is used to commit troops to a defense call.
# Input format: !commit <int>
@bot.command(name='commit')
async def commit(ctx, troops:int):
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
            embed = nextcord.Embed(
                title=f'{ctx.author.name} has committed {troops} troops.',
                description=f'**{remaining}** remaining before **{time}**\n{link}',
                color=nextcord.Color.green()
            )
            await ctx.reply(embed=embed)
            active_calls[channel_name]['troops'] = remaining
            with open(json_path, 'w') as json_file:
                json.dump(active_calls, json_file)

        # If the call is filled, close comments and delete channel after 24 hours
        else:
            embed = nextcord.Embed(
                title='🛡️ ⚔️ This defense call has been filled! ⚔️ 🛡️',
                description='This channel is now closed and will be deleted in 24 hours.',
                color=nextcord.Color.green()
            )
            await ctx.send(embed=embed)
            perms = ctx.channel.overwrites_for(ctx.guild.default_role)
            perms.send_messages = False
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=perms)

            # Update active_calls.json
            active_calls.pop(channel_name)
            with open(json_path, 'w') as json_file:
                json.dump(active_calls, json_file)
            # Delete channel after 24 hours
            await asyncio.sleep(30) # 86400 seconds in 1 day
            print(f'{channel_name} has been deleted.')
            await ctx.channel.delete()

@commands.has_role('Admin') # Command requires Admin role
@bot.command(name='add_artifact')
async def add_artifact(ctx, artifact:str, hours:int):
    json_path = './json_files/artifacts.json'

    print(f'{ctx.author} has requested to add an artifact: {artifact} {hours}')

    if artifact not in possible_artifacts:
        raise commands.BadArgument()

    with open(json_path) as json_file:
        artifacts = json.load(json_file)

    # Working here

    with open(json_path, 'w') as json_file:
        json.dump(artifacts, json_file)

@add_artifact.error
async def add_artifact_error(ctx, error):
    # If the user has chosen an artifact which is not in the list of possible artifacts
    if isinstance(error, commands.BadArgument):
        embed = nextcord.Embed(
            title='The artifact requested is not available',
            color=nextcord.Color.dark_gold()
        )
        embed.add_field(
            name='Available artifacts are:',
            value='• ' + '\n• '.join(possible_artifacts),
            inline=False
        )
        await ctx.reply(embed=embed)
    # If user has the required role, but has thrown an error
    elif not isinstance(error, commands.MissingRole):
        embed = nextcord.Embed(
            title='Incorrect format',
            description='Please follow this example:\n`!add_artifact "artifact-name" "number of hours"`',
            color=nextcord.Color.dark_gold()
        )
        embed.add_field(
            name='Notes:',
            value='• "artifact-name" must be dash seperated.\n' +
                  '• "number of hours" is the number of hours this artifact may be held before the owner is notified to give to the next person.',
                  inline=False
        )
        await ctx.reply(embed=embed)

@bot.event
async def on_ready():
    print(f'We have logged in as: {bot.user.name}')


if __name__ == '__main__':
    bot.run(TOKEN)
