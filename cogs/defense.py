import asyncio
from core.base import Base
import nextcord
from nextcord.ext import commands
from nextcord import Embed

BOT_ROLE = 'Alphas'


class Defense(commands.Cog, Base):

    def __init__(self, bot : commands.Bot):
        Base.__init__(self)
        self.bot = bot

    ### COMMANDS ###
    @commands.has_role(BOT_ROLE)
    @commands.command(name='countdown')
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

        filepath = f'{self.json_path}{str(ctx.guild.id)}'
        role_name = self.load_json(filepath)['def_role']
        if role_name is None:
            print('Countdown creation failed. `role_name` has not been set.')
            await ctx.reply(embed=self.msg_def_role_err())
            return

        countdown_name = 'countdown-' + name
        channel = self.create_text_channel(ctx, countdown_name, 'countdown')

        role = nextcord.utils.get(ctx.guild.roles, name=role_name)
        await channel.send(embed=self.msg_countdown_create(role, troops, time, link))

        guild_info = self.load_json(filepath)
        guild_info['active_calls'][countdown_name] = {
            'troops': troops,
            'time': time,
            'link': link
        }
        self.save_json(guild_info, filepath)
    
    @commands.command(name='commit')
    async def commit(self, ctx : commands.Context, troops : int):
        """Commits troops to countdowns"""
        filepath = f'{self.json_path}{str(ctx.guild.id)}'
        guild_info = self.load_json(filepath)
        channel_name = ctx.channel.name
        def_call = guild_info['active_calls'][channel_name]

        if channel_name in guild_info['active_calls'].keys():
            remaining = def_call['troops'] - troops
            time = def_call['time']
            link = def_call['link']

            if remaining > 0:
                await ctx.reply(embed=self.msg_not_filled(ctx, troops, remaining, time, link))
                guild_info['active_calls'][channel_name]['troops'] = remaining
                self.save_json(guild_info, filepath)
            else:
                await ctx.send(embed=self.msg_filled())

                perms = ctx.channel.overwrites_for(ctx.guild.default_role)
                perms.send_messages = False
                await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=perms)

                guild_info['active_calls'].pop(channel_name)
                self.save_json(guild_info, filepath)

                await asyncio.sleep(86400) # 86400 seconds in 1 day
                await ctx.channel.delete()
                print(f'{channel_name} has been deleted.')
    
    ### ERRORS ###
    @countdown.error
    async def countdown_error(self, ctx : commands.Context, error):
        if not isinstance(error, commands.MissingRole):
            print(error)
            await ctx.reply(embed=self.msg_countdown_err())

    async def msg_def_role_err(self) -> Embed:
        return Embed(
            title='Defense role not yet specified.',
                description='To specify a defense role, run the command `!def_role "role"`\n' +
                '• `"role"` is the name of the defense role within your specific Discord server.',
                color=self.def_color
        )
    
    ### MESSAGES ###
    async def msg_countdown_create(self, role, troops : int, time : str, link : str) -> Embed:
        return Embed(
            title=f'🛡️ ⚔️ NEW DEFENSE CALL ⚔️ 🛡️',
            description=f'{role.mention}',
            color=self.def_color
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

    async def msg_countdown_err(self,) -> Embed:
        return Embed(
            title='Incorrect format',
            description='Please follow this example:\n' +
                        '`!countdown "name-of-channel" "amount" "time" "link to village"`',
            color=self.def_color
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
            color=self.def_color
        )

    async def msg_filled(self) -> Embed:
        return Embed(
            title='🛡️ ⚔️ This defense call has been filled! ⚔️ 🛡️',
            description='This channel is now closed and will be deleted in 24 hours.',
            color=self.def_color
        )


def setup(bot : commands.Bot):
    bot.add_cog(Defense(bot))
