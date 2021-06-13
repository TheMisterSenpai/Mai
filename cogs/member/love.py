import discord
from discord.ext import commands
from discord.utils import get
from discord import message

import config
import nekos
import random
from pymongo import MongoClient
cluster = MongoClient(config.MONGO)
lists = cluster.maidb.bl

def blacklist(ctx):
    if not lists.find_one({"_id": ctx.author.id}):
        return message
    else:
        pass

class реакции(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name = 'hug')
    @commands.check(blacklist)
    async def hug(self, ctx, member: discord.Member):
        '''обнять любого на сервере

        Пример:

        mhug <@ник>
        '''
        if member == ctx.bot.user:
            await ctx.send('>__<')


        elif member == ctx.author:
            await ctx.send('>__< ты не можешь сам себя обнять')

            return

        g = ['hug']
        gnek = nekos.img(random.choice(g))
        emb = discord.Embed(title = f'**Обнимашки!**',description = f'{ctx.author.mention} обнял(а) {member.mention}', color=0xFF0000)
        emb.set_image(url = gnek)
        emb.set_footer(text=f'Вызвано: {ctx.message.author}',icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=emb)


    @commands.command(name = 'poke')
    @commands.check(blacklist)
    async def poke(self, ctx, member: discord.Member):
        '''тыкнуть любого на сервере

        Пример:

        mpoke <@ник>
        '''
        if member == ctx.bot.user:
            await ctx.send('>__<')


        elif member == ctx.author:
            await ctx.send('>__< ты не можешь сам себя тыкнуть')

            return

        n = ['poke']
        nnek = nekos.img(random.choice(n))
        emb = discord.Embed(title = f'**Тыкание!**',description = f'{ctx.author.mention} тыкнул(а) {member.mention}', color=0xFF0000)
        emb.set_image(url = nnek)
        emb.set_footer(text=f'Вызвано: {ctx.message.author}',icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=emb)


    @commands.command(name = 'kiss')
    @commands.check(blacklist)
    async def kiss(self, ctx, member: discord.Member):
        '''поцеловать любого человека

        Пример:

        mkiss <@ник>
        '''
        if member == ctx.bot.user:
            await ctx.send('>__<')

        elif member == ctx.author:
            await ctx.send('>__< ты не можешь сам себя поцеловать')

            return

        k = ['kiss']
        knek = nekos.img(random.choice(k))
        emb = discord.Embed(title = f'**Поцелуйчик!**',description = f'{ctx.author.mention} поцеловал(а) {member.mention}', color=0xFF0000)
        emb.set_image(url = knek)
        emb.set_footer(text=f'Вызвано: {ctx.message.author}',icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=emb)

def setup(client):
    client.add_cog(реакции(client))
