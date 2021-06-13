# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks
from discord import message

from random import randint

import config
from pymongo import MongoClient
cluster = MongoClient(config.MONGO)
lists = cluster.maidb.bl

def blacklist(ctx):
    if not lists.find_one({"_id": ctx.author.id}):
        return message
    else:
        pass

class comm(commands.Cog):
	'''здесь только хелп'''

	def __init__(self, client):
		self.client = client

	@commands.command(name='help', aliases=['commands', 'cmds'], hidden = True)
	@commands.check(blacklist)
	async def thelp(self, ctx, *, command: str = None):

		if command is None:
			embed = discord.Embed(timestamp=ctx.message.created_at,
							color=randint(0x000000, 0xFFFFFF),
							title='Справочник по командам')
			__slots__ = []

			for cog in self.client.cogs:
				__slots__.append(self.client.get_cog(cog))

			for cog in __slots__:
				cog_commands = len([x for x in self.client.commands if x.cog_name == cog.__class__.__name__ and not x.hidden])
				if cog_commands == 0:
					pass
				else:
					embed.add_field(name=cog.__class__.__name__,
									value=', '.join([f'`{x}`' for x in self.client.commands if x.cog_name == cog.__class__.__name__ and not x.hidden]),
									inline=False)

		else:
			entity = self.client.get_cog(command) or self.client.get_command(command)

			if entity is None:
				clean = command.replace('@', '@\u200b')
				embed = discord.Embed(timestamp=ctx.message.created_at,
								color=randint(0x000000, 0xFFFFFF),
								title='Справочник по командам',
								description=f'Команда или категория "{clean}" не найдена.')

			elif isinstance(entity, commands.Command):
				embed = discord.Embed(timestamp=ctx.message.created_at,
								color=randint(0x000000, 0xFFFFFF),
								title='Справочник по командам')
				embed.add_field(name=f'{ctx.prefix}{entity.signature}',
								value=entity.help,
								inline=False)

			else:
				embed = discord.Embed(timestamp=ctx.message.created_at,
								color=randint(0x000000, 0xFFFFFF),
								title='Справочник по командам')
				embed.add_field(name=entity.__class__.__name__ + ': ' + entity.__class__.__doc__,
								value=', '.join([f'`{x}`' for x in self.client.commands if x.cog_name == entity.__class__.__name__ and not x.hidden]),
								inline=False)

		embed.set_thumbnail(url=self.client.user.avatar_url)
		embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
		embed.set_footer(text=f'{ctx.prefix}help [команда/категория] для получения доп.информации.')

		await ctx.send(embed=embed)

def setup(client):
    client.add_cog(comm(client))                    