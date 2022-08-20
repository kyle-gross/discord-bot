#!/usr/bin/env python3
import nextcord
from nextcord.ext import commands
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String

Base = declarative_base()


class BaseModel():
    """The base class for bot objects."""

    guild_id = Column(String(60), nullable=False, primary_key=True)
    guild_name = Column(String(256), nullable=False)
    def_role = Column(String(60), nullable=True)
    bot_role = Column(String(60), nullable=True)

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def save(self):
        from models import storage
        storage.new(self)
        storage.save()

    def delete(self):
        from models import storage
        storage.delete(self)

    def to_dict(self) -> dict:
        dict = {}
        dict.update(self.__dict__)
        if '_sa_instance_state' in dict.keys():
            del dict['_sa_instance_state']
        return dict

    async def create_text_channel(self, ctx : commands.Context, channel_name : str, category_name : str):
        """Creates a text channel and corresponding category"""
        category = nextcord.utils.get(ctx.guild.categories, name=category_name)
        if category is None:
            category = await ctx.guild.create_category_channel(category_name)
        channel = await ctx.guild.create_text_channel(channel_name, category=category)
        print(f'Created new channel - id: {channel.id}')
        return channel
