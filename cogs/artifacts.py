from core.base import Base
import nextcord
from nextcord import Embed
from nextcord.ext import commands

BOT_ROLE = 'Alphas'

class Artifacts(commands.Cog, Base):

    def __init__(self, bot : commands.Bot):
        Base.__init__(self)
        self.bot = bot
        self.possible_artifacts = [
            'small-trainer', 'large-trainer', 'unique-trainer',
            'small-storage', 'large-storage'
        ]

    ### COMMANDS ###
    @commands.has_role(BOT_ROLE)
    @commands.command(name='add_artifact')
    async def add_artifact(self, ctx : commands.Context, artifact : str, hours : int):
        """Adds an artifact for a server & creates associated channel"""
        print(f'{ctx.author} has requested to add an artifact: {artifact} {hours}')
        guild_id = str(ctx.guild.id)
        filepath = f'{self.json_path}{guild_id}'

        if artifact not in self.possible_artifacts:
            raise commands.BadArgument()
        
        guild_info = self.load_json(filepath)
        artifacts = guild_info['artifacts']
        new_info = {
            'hours': hours,
            'current_owner': '',
            'prev_owners': []
        }
        if len(artifacts) == 0:
            new_artifact = artifact + '-1'
            artifacts[new_artifact] = new_info
        else:
            for i in range(len(artifacts) + 1):
                new_artifact = artifact + '-' + str(i + 1)
                if new_artifact not in artifacts.keys():
                    artifacts[new_artifact] = new_info
                    break
        self.create_text_channel(ctx, new_artifact, 'artifacts')

        await ctx.reply(embed=self.msg_add_artifact())
        guild_info['artifacts'] = artifacts
        self.save_json(guild_info, filepath)

    @commands.command(name='update_artifact')
    async def update_artifact(self, ctx : commands.Context, channel_name : str, hours : int):
        """Updates the # of hours that an artifact may be held"""
        print(f'{ctx.author} has requested to update an artifact: {channel_name}\n\tNew hours: {hours}')
        guild_id = str(ctx.guild.id)
        filepath = f'{self.json_path}{guild_id}'
        channel = nextcord.utils.get(ctx.guild.channels, name=channel_name)
        if channel is None:
            raise commands.BadArgument

        guild_info = self.load_json(filepath)
        artifacts = guild_info['artifacts']
        artifacts[channel_name]['hours'] = hours
        guild_info[guild_id]['artifacts'] = artifacts
        self.save_json(guild_info, filepath)

        await ctx.reply(embed=self.msg_update_artifact(channel_name, hours))

    @commands.has_role(BOT_ROLE)
    @commands.command(name='remove_artifact')
    async def remove_artifact(self, ctx : commands.Context, artifact : str):
        """Removes an artifact from a server & deletes the associated channel"""
        print(f'{ctx.author} has requested to remove an artifact: {artifact}')
        guild_id = str(ctx.guild.id)
        filepath = f'{self.json_path}{guild_id}'
        guild_info = self.load_json(filepath)
        artifacts = guild_info['artifacts']

        if artifact not in artifacts.keys():
            raise commands.BadArgument

        artifacts.pop(artifact)
        guild_info['artifacts'] = artifacts
        self.save_json(guild_info, filepath)

        channel = nextcord.utils.get(ctx.guild.channels, name=artifact)
        await channel.delete()
        await ctx.reply(embed=self.msg_rem_artifact(artifact))
    
    ### ERRORS ###
    @add_artifact.error
    async def add_artifact_error(self, ctx : commands.Context, error):
        print(error)
        if not isinstance(error, commands.MissingRole):
            await ctx.reply(embed=self.msg_add_artifact_error(ctx))

    @remove_artifact.error
    async def remove_artifact_error(self, ctx : commands.Context, error):
        print(error)
        if not isinstance(error, commands.MissingRole):
            await ctx.reply(embed=self.msg_rem_err())

    ### MESSAGES ###
    async def msg_add_artifact(self, channel, hours : int) -> Embed:
        return Embed(
            title='Artifact channel has been created.',
            description=f'{channel.mention}',
            color=self.artifact_color
        ).add_field(
            name='May be held for:',
            value=f'{hours} hours'
        ).add_field(
            name='To change the hours held:',
            value='run `!update_artifact "channel-name" "new-hour-amount"`',
            inline=False
        )
    
    async def msg_add_artifact_error(self) -> Embed:
        return Embed(
            title='Incorrect format',
            description='Please follow this example:\n`!add_artifact "artifact-name" "number of hours"`',
            color=self.artifact_color
        ).add_field(
            name='Notes:',
            value='• `"artifact-name"` must be dash separated.\n' +
                '• `"number of hours"` is the number of hours this artifact may be held before the owner is notified to give to the next person.',
                inline=False
        ).add_field(
            name='Available artifacts are:',
            value='• ' + '\n• '.join(self.possible_artifacts)
        )

    async def msg_update_artifact(self, channel_name : str, hours : int) -> Embed:
        return Embed(
            title=f'Artifact: {channel_name} has been updated.',
            description=f'New hours: {hours}',
            color=self.artifact_color
        )
    
    async def msg_rem_artifact(self, artifact : str) -> Embed:
        return Embed(
            title='Artifact channel has been deleted.',
            description=f'~~{artifact}~~',
            color=self.artifact_color
        )
    

def setup(bot : commands.Bot):
    bot.add_cog(Artifacts(bot))
