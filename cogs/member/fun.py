# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks

import random
from random import randint, choice
import nekos
import wikipedia
from pymongo import MongoClient
cluster = MongoClient(config.MONGO)
lists = cluster.maidb.bl

def blacklist(ctx):
    if not lists.find_one({"_id": ctx.author.id}):
        return message
    else:
        pass

class интересные(commands.Cog):
	'''весёлые команды для серверов'''

	def __init__(self, client):
		self.client = client

	@commands.command(name = 'hentai', aliases = ['hent'])
	@commands.check(blacklist)
	async def hentai(self, ctx):
		'''Просмотор интересных картинок и gif

		Пример:
		mhentai
		'''

		if ctx.channel.is_nsfw():
			r = ['feet', 'yuri', 'trap', 'futanari', 'hololewd', 'lewdkemo',
			'solog', 'feetg', 'cum', 'erokemo', 'les', 'wallpaper', 'lewdk',
			'ngif', 'tickle', 'lewd', 'feed', 'gecg', 'eroyuri', 'eron',
			'cum_jpg', 'bj', 'nsfw_neko_gif', 'solo', 'kemonomimi', 'nsfw_avatar',
			'gasm', 'poke', 'anal', 'slap', 'hentai', 'avatar', 'erofeet', 'holo',
			'keta', 'blowjob', 'pussy', 'tits', 'holoero', 'lizard', 'pussy_jpg',
			'pwankg', 'classic', 'kuni', 'waifu', 'pat', '8ball', 'kiss', 'femdom',
			'neko', 'spank', 'cuddle', 'erok', 'fox_girl', 'boobs', 'random_hentai_gif',
			'smallboobs', 'hug', 'ero', 'smug', 'goose', 'baka', 'woof']
			rnek = nekos.img(random.choice(r))
			emb = discord.Embed(color = discord.Color.red())
			emb.set_image(url = rnek)
			await ctx.send(embed = emb)
		else:
			await ctx.send(f'🔞⟩ Простите, но здесь нельзя использовать эту команду!')
			await ctx.message.add_reaction('🔞')

	@commands.command(name = 'wiki')
	@commands.check(blacklist)
	async def wiki(self, ctx, *, text):
		'''узнать информацию не открывая браузера

		Пример:
		mwiki discord
		'''

		wikipedia.set_lang("ru")
		new_page = wikipedia.page(text)
		summ = wikipedia.summary(text)
		emb = discord.Embed(
			title= new_page.title,
			description= summ,
			color = 0x00ffff
		)
		emb.set_author(name= 'Больше информации тут! Кликай!', url= new_page.url, icon_url= 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/1200px-Wikipedia-logo-v2.svg.png')

		await ctx.send(embed=emb)

	@commands.command(name = 'osu')
	@commands.check(blacklist)
	async def osu(self, ctx, player: commands.clean_content, \
                            mode: commands.clean_content = 'osu!'):
		'''Статистика пользователя в Osu

		Пример:

		mosu <ник><osu!, taiko, mania, catch>
		'''

		if mode == 'osu!'  or mode == 'o':
			game_mode = {'num': 0, 'name': 'osu!'}

		if mode == 'taiko' or mode == 't':
			game_mode = {'num': 1, 'name': 'osu!taiko'}

		if mode == 'catch' or mode == 'ctb' or mode == 'c':
			game_mode = {'num': 2, 'name': 'osu!catch'}

		if mode == 'mania' or mode == 'm':
			game_mode = {'num': 3, 'name': 'osu!mania'}

		tc = lambda: randint(0, 255)
		osu_desk_color = '%02X%02X%02X' % (tc(), tc(), tc())

		embed = discord.Embed(timestamp=ctx.message.created_at,
						color=randint(0x000000, 0xFFFFFF),
						title=f'Статистика {player} в {game_mode["name"]}')
		embed.set_image(url=f'http://lemmmy.pw/osusig/sig.php?colour=hex{osu_desk_color}&uname={player}&mode={game_mode["num"]}&pp=1&countryrank&removeavmargin&flagshadow&flagstroke&darktriangles&opaqueavatar&avatarrounding=5&onlineindicator=undefined&xpbar&xpbarhex')

		embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

		await ctx.send(embed=embed)

def setup(client):
    client.add_cog(интересные(client))
