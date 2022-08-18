import json
import nextcord
from nextcord.ext import commands
import os


class Base():
    """The base class for bot objects."""

    def __init__(self):
        self.json_path = './json/'
        self.def_color = nextcord.Color.green()
        self.artifact_color = nextcord.Color.dark_gold()

    async def load_json(self, path : str) -> dict:
        with open(path) as f:
            guild_info = json.load(f)
        return dict(guild_info)

    async def save_json(self, src : dict, dest : str,):
        with open(dest, 'w') as f:
            json.dump(src, f)
    
    async def delete_json(self, path : str):
        filepath = os.path.join(path)
        if os.path.exists(filepath):
            os.remove(filepath)
        else:
            print(f'Cannot delete file "{filepath}" - does not exist')

    async def create_text_channel(self, ctx : commands.Context, channel_name : str, category_name : str):
        """Creates a text channel and corresponding category"""
        category = nextcord.utils.get(ctx.guild.categories, name=category_name)
        if category is None:
            category = await ctx.guild.create_category_channel(category_name)
        channel = await ctx.guild.create_text_channel(channel_name, category=category)
        print(f'Created new channel - id: {channel.id}')
        return channel
