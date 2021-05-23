# python3.8.3
# coding: utf-8

import discord
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks
from discord_slash import SlashCommand, SlashContext

import os
import sys
import aiohttp
import traceback

import config
from asyncio import sleep


client = commands.Bot( command_prefix = config.BOT_PREFIX, intents = discord.Intents.all())
slash = SlashCommand(client, override_type = True)
client.remove_command('help')

#Загрузка когов
async def start_session():
    client.session = aiohttp.ClientSession(loop=client.loop)

extensions = [
'cogs.administator.admin',
#'cogs.eco.economic',
'cogs.events.errors',
#'cogs.events.userDB',
'cogs.member.command',
'cogs.member.fun',
'cogs.member.info',
'cogs.member.love',
'cogs.music.music',
'cogs.owner',
'jishaku'
]

if __name__ == '__main__':

	for extension in extensions:
		try:
			client.load_extension(extension)
		except Exception as e:
			print(f'[!] Не удалось загрузить модуль {extension}.', file=sys.stderr)
			traceback.print_exc()
			print('------------------------')
		else:
			print(f'[!] Модуль {extension} успешно загружен.')

#статус
@client.event
async def on_connect():
    await client.change_presence(activity=discord.Game(name='загружаюсь'), status=discord.Status.idle)

@client.event
async def on_ready():

	while True:
		await client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = "sqdsh.top/mai"))
		await sleep(120)
		await client.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = "Spotify"))
		await sleep(120)


@client.event
async def on_message(message):
	await client.process_commands(message)

	msg = message.content.lower()
	maicontent = ["мая", "mai", "@Мая"]

	if msg in maicontent:
		emb = discord.Embed(title = "**Я тут**", color = config.INFO, description = "Привет, мой префикс `m` для всех команд! Но если вам не понятно, то можете написать команду `mhelp`")
		emb.set_thumbnail(url = client.user.avatar_url)

		await message.channel.send(embed = emb)

@slash.slash(name="test")
async def test(ctx: SlashContext):
    embed = discord.Embed(title="embed test")
    await ctx.send(content="test", embeds=[embed])

client.run(config.TOKEN)
