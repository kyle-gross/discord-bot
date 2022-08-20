#!/usr/bin/env python3
from models import storage
from models.artifact import Artifact
from models.base import BaseModel
import nextcord
from nextcord import Embed
from nextcord.ext import commands

BOT_ROLE = 'Alphas'

class Artifacts(commands.Cog, BaseModel):

    def __init__(self, bot : commands.Bot):
        BaseModel.__init__(self)
        self.bot = bot
        self.color = nextcord.Color.dark_gold()
        self.possible_artifacts = [
            'small-trainer', 'large-trainer', 'unique-trainer',
            'small-storage', 'large-storage'
        ]

    ### COMMANDS ###

    @commands.command(name='add_artifact', usage='<artifact name> <hours>')
    @commands.has_role(BOT_ROLE)
    async def add_artifact(self, ctx : commands.Context, artifact : str, hours : int):
        """Adds an artifact & creates text channel"""
        print(f'{ctx.author} has requested to add an artifact: {artifact} {hours}')
        guild = f'Guild.{str(ctx.guild.id)}'
        guild = storage.all()[guild]

        if artifact not in self.possible_artifacts:
            raise commands.BadArgument()
        
        channel_name = f'{artifact}-'
        channels = [channel.name for channel in ctx.guild.text_channels]
        for i in range(len(channels)):
            channel_name = f'{artifact}-{str(i+1)}'
            if channel_name not in channels:
                channel = await self.create_text_channel(ctx, channel_name, 'artifacts')
                break

        artifact = Artifact(
            id=str(channel.id),
            name=channel_name,
            hours=hours,
            current_owner=None,
            guild_id=str(ctx.guild.id)
        )
        storage.new(artifact)
        storage.save()

        embed = await self.msg_add_artifact(channel, hours)
        await ctx.reply(embed=embed)

    @commands.command(name='update_artifact', usage='<channel name> <hours>')
    @commands.has_role(BOT_ROLE)
    async def update_artifact(self, ctx : commands.Context, channel_name : str, hours : int):
        """Updates the # of hours for an artifact"""
        print(f'{ctx.author} has requested to update an artifact: {channel_name}\n\tNew hours: {hours}')
        channel = nextcord.utils.get(ctx.guild.channels, name=channel_name)
        if channel is None:
            raise commands.BadArgument
        artifact = f'Artifact.{str(channel.id)}'
        artifact = storage.all()[artifact]
        artifact.hours = hours
        storage.save()

        embed = await self.msg_update_artifact(channel_name, hours)
        await ctx.reply(embed=embed)

    @commands.command(name='remove_artifact', usage='<channel name>')
    @commands.has_role(BOT_ROLE)
    async def remove_artifact(self, ctx : commands.Context, channel_name : str):
        """Removes an artifact & deletes channel"""
        print(f'{ctx.author} has requested to remove an artifact: {channel_name}')
        channel = nextcord.utils.get(ctx.guild.channels, name=channel_name)
        if channel is None:
            raise commands.BadArgument
        artifact = f'Artifact.{str(channel.id)}'
        artifact = storage.all()[artifact]
        storage.delete(artifact)
        storage.save()
       
        await channel.delete()
        embed = await self.msg_rem_artifact(channel_name)
        await ctx.reply(embed=embed)
    
    ### ERRORS ###

    @add_artifact.error
    async def add_artifact_error(self, ctx : commands.Context, error):
        print(error)
        if not isinstance(error, commands.MissingRole):
            embed = await self.msg_add_artifact_error()
            await ctx.reply(embed=embed)

    @remove_artifact.error
    async def remove_artifact_error(self, ctx : commands.Context, error):
        print(error)
        if not isinstance(error, commands.MissingRole):
            embed = await self.msg_rem_err()
            await ctx.reply(embed=embed)

    ### MESSAGES ###

    async def msg_add_artifact(self, channel, hours : int) -> Embed:
        return Embed(
            title='Artifact channel has been created.',
            description=f'{channel.mention}',
            color=self.color
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
            color=self.color
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
            color=self.color
        )
    
    async def msg_rem_artifact(self, artifact : str) -> Embed:
        return Embed(
            title='Artifact channel has been deleted.',
            description=f'~~{artifact}~~',
            color=self.color
        )

    async def msg_rem_err(self):
        return Embed(
            title='Error removing artifact',
            description='Please follow this example:\n`!remove_artifact "channel-name"`',
            color=self.color
        ).add_field(
            name='Notes:',
            value='• `"channel-name"` must be the exact name of the channel.\n' +
                  '• `"channel-name"` should be all lowercase.'
        )
    

def setup(bot : commands.Bot):
    bot.add_cog(Artifacts(bot))
