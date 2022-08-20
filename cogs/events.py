#!/usr/bin/env python3
from models.guild import Guild
from models import storage
import nextcord
from nextcord.ext import commands
from nextcord import Embed


class Events(commands.Cog):

    def __init__(self, bot : commands.Bot):
        self.color = nextcord.Color.dark_gold()
        self.bot = bot

    ### EVENTS ###

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'We have logged in as: {self.bot.user.name}')

    @commands.Cog.listener()
    async def on_guild_join(self, ctx : commands.Context):
        guild = Guild(
            id=str(ctx.id),
            guild_name=ctx.name,
            def_role=None,
            admin_role=None
        )
        storage.new(guild)
        storage.save()
        embed = await self.msg_on_join()
        await ctx.owner.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, ctx : commands.Context):
        guild = f'Guild.{str(ctx.id)}'
        guild = storage.all()[guild]
        storage.delete(guild)
        storage.save()

    ### MESSAGES ###

    async def msg_on_join(self) -> Embed:
        return Embed(
            title=f'Thank you for inviting {self.bot.user.name} to your server!',
            color=self.color
        ).add_field(
            name='Tips:',
            value='• It is recommended to create a private channel for writing bot commands, so that general channels are not spammed with bot responses.\n' +
            '• To use some bot commands (such as `!countdown`), the `Alphas` role is required.\n' +
            '• Ensure that all users who are allowed to manage the bot are assigned the role `Alphas`.\n' +
            '• Please run the `!def_role` command to set the name of your defender role for your server. ex: `Def`, `Defender`, `Defense`\n',
            inline=False
        ).add_field(
            name='For a full list of commands, please refer to the bot documentation',
            value='https://github.com/kyle-gross/discord-bot/blob/master/README.md'
        )


def setup(bot : commands.Bot):
    bot.add_cog(Events(bot))
