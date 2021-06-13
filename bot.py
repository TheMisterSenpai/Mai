# python3.8.3
# coding: utf-8

import discord
from discord import message
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks
from discord import client
from discord import Webhook, RequestsWebhookAdapter


import requests
import os
import sys
import aiohttp
import traceback

import config
from asyncio import sleep


client = commands.Bot( command_prefix = config.BOT_PREFIX)
client.remove_command('help')
webhook = Webhook.partial(config.ID_GUILD, config.KEY, adapter=RequestsWebhookAdapter())


#Загрузка когов
async def start_session():
    client.session = aiohttp.ClientSession(loop=client.loop)

extensions = [
'cogs.administator.admin',
'cogs.events.errors',
'cogs.member.command',
'cogs.member.fun',
'cogs.member.info',
'cogs.member.love',
'cogs.member.music',
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

	emb = discord.Embed(title = 'Мая загрузилась', color = config.INFO)
	emb.add_field(name = 'Количество серверов', value = f'**{len(client.guilds)}**')
	emb.add_field(name = 'Шардов', value = '0')

	webhook.send(embed = emb)
	
	while True:
		await client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = "sqdsh.top/mai"))
		await sleep(120)
		await client.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = "Spotify"))
		await sleep(120)


client.run(config.TOKEN)
