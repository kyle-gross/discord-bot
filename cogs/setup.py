from core.base import Base
from nextcord import Embed
from nextcord.ext import commands
import os

BOT_ROLE = 'Alphas'

class Setup(commands.Cog, Base):

    def __init__(self, bot : commands.Bot):
        Base.__init__(self)
        self.bot = bot

    @commands.has_role(BOT_ROLE)
    @commands.command(name='def_role')
    async def def_role(self, ctx : commands.Context, def_role : str):
        """Sets the defense role for your Discord server"""
        filepath = os.path.join(self.json_path, str(ctx.guild.id))
        guild_info = self.load_json(filepath)
        guild_info['def_role'] = def_role
        self.save_json(guild_info, filepath)
        await ctx.reply(embed=self.msg_set_role())

    async def msg_set_role(self, def_role : str) -> Embed:
        return Embed(
            title=f'Defense role has been set: {def_role}',
            description='If this is incorrect, run the `!def_role` command again and specify the proper defense role.',
            color=self.def_color
        ).add_field(
            name='Notes:',
            value='• Use the exact role name as it appears in your server. This is case sensitive.'
        )


def setup(bot : commands.Bot):
    bot.add_cog(Setup(bot))
