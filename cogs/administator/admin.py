import discord
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks

import config
import traceback
from pymongo import MongoClient

cluster = MongoClient(config.MONGO)
lists = cluster.maidb.bl

class администрация(commands.Cog):
	'''Команды для администрации серверов'''

	def __init__(self, client):
		self.client = client

	@commands.command(name = 'clear')
	@commands.has_permissions( manage_messages=True )
	async def clear(self, ctx, amount : int):
		'''почистить чат от ненужных сообщений

		Пример:
		mclear 10
		'''
		if amount > 100:
			await ctx.send(f'Число сообщений не должно превышать {amount}.')
		else:
			await ctx.message.delete()
			deleted = await ctx.channel.purge( limit = amount)
			await ctx.send(f'📥⟩ Было очищено сообщений: **{len(deleted)}**', delete_after = 30)

	@commands.command(name = 'clearur')
	@commands.has_permissions(manage_messages=True )
	async def clearur(self, ctx, member: discord.Member, amount : int):
		'''очистить сообщение от пользователя 

		Пример:
		mclearur @Ник 12
		'''
		if amount > 100:
			await ctx.send(f'Число сообщений не должно превышать {amount}.')
		else:
			def is_member(m):
				return m.author == member
			await ctx.channel.purge(limit=amount, check=is_member)


	@commands.command(name = 'ban')
	@commands.has_permissions( kick_members = True)
	async def ban(self, ctx, member : discord.Member, *, reason=None):
		'''заблокировать нарушителя на сервере

		Пример:
		mban @ник <причина>
		'''

		await ctx.message.delete()

		if member == ctx.bot.user:
			await ctx.send('❌⟩ **Нельзя** заблокировать меня!', delete_after = 15)

			return

		elif ctx.author.top_role == member.top_role:
			await ctx.send('❌⟩ Простите, но я **не могу** заблокировать его, так как у вас одинаковые роли', delete_after = 15)

			return

		elif member == ctx.author:
			await ctx.send('❌⟩ Простите, но я **не могу** вас заблокировать', delete_after = 15)

			return

		elif member == ctx.guild.owner:
			await ctx.send('❌⟩ **Нельзя** заблокировать создателя сервера!', delete_after = 15)

			return

		elif ctx.author.top_role < member.top_role:
			await ctx.send('❌⟩ **Нельзя** блокировать пользователя выше тебя(сделанно для безопасности)', delete_after = 15)

			return

		if reason == None:

			emb = discord.Embed( color = discord.Color.red())
			emb.add_field( name = '🔨⟩ Заблокирован', value = f'**{member.name}** был заблокирован с сервера **{ctx.guild.name}**', inline = False)
			emb.add_field( name = 'Модератор', value = f'{ctx.author}')
			await member.ban(reason=None)

			await ctx.send(embed=emb, delete_after = 15)

			return

		else:
			emb = discord.Embed( color = discord.Color.red())
			emb.add_field( name = '🔨⟩ Заблокирован', value = f'**{member.name}** был заблокирован с сервера **{ctx.guild.name}**', inline = False)
			emb.add_field( name = 'По причине:', value = reason, inline = False)
			emb.add_field( name = 'Модератор:', value = f'``{ctx.author}``')
			await member.ban(reason=reason)

			await ctx.send(embed = emb, delete_after = 15)

	@commands.command(name = 'kick')
	@commands.has_permissions( kick_members = True )
	async def kick(self, ctx, member : discord.Member, *, reason=None):

		await ctx.message.delete()

		if member == ctx.bot.user:
			await ctx.send('❌⟩ **Нельзя** заблокировать меня!', delete_after = 15)

			return

		elif ctx.author.top_role == member.top_role:
			await ctx.send('❌⟩ Простите, но я **не могу** заблокировать его, так как у вас одинаковые роли', delete_after = 15)

			return

		elif member == ctx.author:
			await ctx.send('❌⟩ Простите, но я **не могу** вас заблокировать', delete_after = 15)

			return

		elif member == ctx.guild.owner:
			await ctx.send('❌⟩ **Нельзя** заблокировать создателя сервера!', delete_after = 15)

			return

		elif ctx.author.top_role < member.top_role:
			await ctx.send('❌⟩ **Нельзя** блокировать пользователя выше тебя(сделанно для безопасности)', delete_after = 15)

			return

		if reason == None:
			
			emb = discord.Embed( colour = discord.Color.red(), timestamp = ctx.message.created_at)
			emb.add_field(name = '🔨⟩Выгнат', value = f'`{member.name}` был выгнат с сервера {ctx.guild.name}', inline = False)
			emb.add_field(name = 'Модератор:', value = f'**{ctx.author}**')
			await member.ban(reason=None)

			await ctx.send(embed = emb)

			return

		else:

			emb = discord.Embed( colour = discord.Color.red(), timestamp = ctx.message.created_at)
			emb.add_field(name = '🔨⟩Выгнат', value = f'`{member.name}` был выгнат с сервер {ctx.guild.name}', inline = False)
			emb.add_field(name = 'Причина:', value = reason, inline = False)
			emb.add_field(name = 'Модератор:', value = f'**{ctx.author}**')
			await member.ban(reason=reason)

			await ctx.send(embed = emb)


	@commands.command(name = 'banlist')
	async def banlist (self, ctx):
		'''просмотор заблокированых людей

		Пример:
		mbanlist
		'''

		bans = await ctx.guild.bans()

		if len(bans) <= 0:
			emb = discord.Embed(
				timestamp = ctx.message.created_at,
				color = config.BANLISTNOT,
				description = '🔨⟩Заблокированых пользователей нет!')
		else:
			emb = discord.Embed(
				timestamp = ctx.message.created_at,
				color = config.BANLISTYES,
				description = f'🔨⟩Заблокированые пользователи: \n{", ".join([user.user.name for user in bans])}')

		emb.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
		await ctx.send(embed = emb)

	@commands.command(name = 'unban')
	@commands.has_permissions( administrator = True)
	async def unban ( self, ctx, *, member):
		'''разблокировать человека на сервере

		Пример:
		unban @ник
		'''

		await ctx.message.delete()

		banned_users = await ctx.guild.bans()

		for ban_entry in banned_users:
			user = ban_entry.user

			emb = discord.Embed( color = discord.Color.green())
			emb.add_field( name = '❤️⟩ Разблокирован', value = f'**{user.mention}** был разблокирован', inline = False)
			emb.add_field( name = 'Модератор:', value = f'``{ctx.author}``')

			await ctx.send(embed = emb)

			await ctx.guild.unban( user )

			return



def setup(client):
    client.add_cog(администрация(client))
