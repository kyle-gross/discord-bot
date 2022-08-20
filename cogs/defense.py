#!/usr/bin/env python3
import asyncio
from models.base import BaseModel
from models.def_call import DefCall
from models import storage
import nextcord
from nextcord.ext import commands
from nextcord import Embed

BOT_ROLE = 'Alphas'


class Defense(commands.Cog, BaseModel):

    def __init__(self, bot : commands.Bot):
        BaseModel.__init__(self)
        self.bot = bot
        self.color = nextcord.Color.green()

    ### COMMANDS ###

    @commands.has_role(BOT_ROLE)
    @commands.command(name='countdown', usage='<village-name> <troops needed> <time of attack> <link to village>')
    async def countdown(
        self,
        ctx : commands.Context,
        name : str,
        troops : int,
        time : str,
        link : str 
    ):
        """Creates countdowns for defense calls"""
        print(f'{ctx.author} has requested a countdown:', name, troops, time, link)
        guild = f'Guild.{str(ctx.guild.id)}'
        guild = storage.all()[guild]

        role_name = guild.def_role
        if role_name is None:
            print('Countdown creation failed. `def_role` has not been set.')
            embed = await self.msg_def_role_err()
            await ctx.reply(embed=embed)
            return

        countdown_name = 'countdown-' + name
        channel = await self.create_text_channel(ctx, countdown_name, 'countdown')

        def_call = DefCall(
            id=str(channel.id),
            name=name,
            troops=troops,
            time=time,
            link=link,
            guild_id=str(ctx.guild.id)
        )
        storage.new(def_call)
        storage.save()

        role = nextcord.utils.get(ctx.guild.roles, name=role_name)
        embed = await self.msg_countdown_create(role, troops, time, link)
        await channel.send(embed=embed)
    
    @commands.command(name='commit', usage='<# of troops>')
    async def commit(self, ctx : commands.Context, troops : int):
        """Commits troops to countdowns"""
        try:
            def_call = f'DefCall.{str(ctx.channel.id)}'
            def_call = storage.all()[def_call]
        except KeyError:
            return

        def_call.troops -= troops
        storage.save()
        if def_call.troops > 0:
            embed = await self.msg_not_filled(ctx, troops, def_call.troops, def_call.time, def_call.link)
            await ctx.reply(embed=embed)
        else:
            embed = await self.msg_filled()
            await ctx.send(embed=embed)

            perms = ctx.channel.overwrites_for(ctx.guild.default_role)
            perms.send_messages = False
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=perms)
            await asyncio.sleep(86400) # 86400 seconds in 1 day
            await ctx.channel.delete()
            storage.delete(def_call)
            storage.save()
            print(f'{ctx.channel.name} has been deleted.')
    
    ### ERRORS ###

    @countdown.error
    async def countdown_error(self, ctx : commands.Context, error):
        if not isinstance(error, commands.MissingRole):
            print(error)
            embed = await self.msg_countdown_err()
            await ctx.reply(embed=embed)
    
    ### MESSAGES ###

    async def msg_countdown_create(self, role, troops : int, time : str, link : str) -> Embed:
        return Embed(
            title=f'🛡️ ⚔️ NEW DEFENSE CALL ⚔️ 🛡️',
            description=f'{role.mention}',
            color=self.color
        ).add_field(
            name=f'Troops needed:',
            value=f'{troops}',
            inline=True
        ).add_field(
            name=f'Before:',
            value=f'{time}',
            inline=True
        ).add_field(
            name=f'Send troops to:',
            value=f'{link}',
            inline=True
        ).add_field(
            name='Please `!commit` the exact amount of troops (in crop) you are sending.',
            value='ex: `!commit 10000`',
            inline=False
        )

    async def msg_def_role_err(self) -> Embed:
        return Embed(
            title='Defense role not yet specified.',
                description='To specify a defense role, run the command `!def_role "role"`\n' +
                '• `"role"` is the name of the defense role within your specific Discord server.',
                color=self.color
        )

    async def msg_countdown_err(self) -> Embed:
        return Embed(
            title='Incorrect format',
            description='Please follow this example:\n' +
                        '`!countdown "name-of-channel" "amount" "time" "link to village"`',
            color=self.color
        ).add_field(
            name='Notes:',
            value='• `"name-of-channel"` must be dash separated, do not use spaces.\n' +
                '• Do not use "quotation marks".',
            inline=False
        )

    async def msg_not_filled(
        self, ctx : commands.Context,
        troops : int,
        remaining : int,
        time : str,
        link : str
    ) -> Embed:
        return Embed(
            title=f'{ctx.author.name} has committed {troops} troops.',
            description=f'**{remaining}** remaining before **{time}**\n{link}',
            color=self.color
        )

    async def msg_filled(self) -> Embed:
        return Embed(
            title='🛡️ ⚔️ This defense call has been filled! ⚔️ 🛡️',
            description='This channel is now closed and will be deleted in 24 hours.',
            color=self.color
        )


def setup(bot : commands.Bot):
    bot.add_cog(Defense(bot))
