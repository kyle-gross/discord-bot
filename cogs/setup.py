#!/usr/bin/env python3
from models.base import BaseModel
from models import storage
from nextcord import Embed, Color
from nextcord.ext import commands
import os

BOT_ROLE = 'Alphas'

class Setup(commands.Cog, BaseModel):

    def __init__(self, bot : commands.Bot):
        BaseModel.__init__(self)
        self.bot = bot
        self.color = Color.green()

    ### COMMANDS ###

    @commands.command(name='def_role', usage='<role name>')
    @commands.has_role(BOT_ROLE)
    async def def_role(self, ctx : commands.Context, def_role : str):
        """Sets the defense role"""
        guild_id = f'Guild.{str(ctx.guild.id)}'
        guild = storage.all()[guild_id]
        setattr(guild, 'def_role', def_role)
        storage.save()
        embed = await self.msg_set_def_role(def_role)
        await ctx.reply(embed=embed)

    @commands.command(name='admin_role', usage='<role name>')
    @commands.is_owner()
    async def admin_role(self, ctx : commands.Context, admin_role : str):
        """Sets the admin role (owner only)"""
        guild_id = f'Guild.{str(ctx.guild.id)}'
        guild = storage.all()[guild_id]
        setattr(guild, 'admin_role', admin_role)
        storage.save()
        embed = await self.msg_set_bot_role(admin_role)
        await ctx.reply(embed=embed)

    ### MESSAGES ###

    async def msg_set_def_role(self, def_role : str) -> Embed:
        return Embed(
            title=f'Defense role has been set: `{def_role}`',
            description='If this is incorrect, run the `!def_role` command again and specify the proper defense role.',
            color=self.color
        ).add_field(
            name='Notes:',
            value='• Use the exact role name as it appears in your server. This is case sensitive.'
        )
    
    async def msg_set_bot_role(self, admin_role : str) -> Embed:
        return Embed(
            title=f'Admin role has been set: `{admin_role}`',
            description='If this is incorrect, run the `!admin_role` command again and specify the proper admin role.',
            color=self.color
        ).add_field(
            name='Notes:',
            value='• Use the exact role name as it appears in your server. This is case sensitive.\n' +
            '• This command may only be executed by the server owner.'
        )


def setup(bot : commands.Bot):
    bot.add_cog(Setup(bot))
