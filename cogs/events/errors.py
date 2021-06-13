import discord
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks

import config
from base import random_comment
import random

class errors(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            emb = discord.Embed(title = ':warning: О нет, произошла ошибка в команде!', color=discord.Color.red())
            emb.add_field(name = 'Ошибка:', value = f'> Пользователь не был найден на сервере или в базе данных' )
            emb.set_footer(text = random.choice(random_comment.COMMENT))
            await ctx.send(embed = emb, delete_after = 15)  
        if isinstance(error, commands.CommandOnCooldown):
            emb = discord.Embed(title = ':warning: О нет, у команды кулдаун!', color=discord.Color.red())
            emb.add_field(name = 'Ошибка:', value = f'> У этой команды есть кулдаун: ``5 часов``' )
            emb.set_footer(text = random.choice(random_comment.COMMENT))
            await ctx.send(embed = emb, delete_after = 15) 
        if isinstance(error, commands.errors.MissingPermissions):
            emb = discord.Embed(title = ':warning: О нет, произошла ошибка в команде!', color=discord.Color.red())
            emb.add_field(name = 'Ошибка:', value = f'> У вас не хватает правил для использование этой команды' )
            emb.set_footer(text = random.choice(random_comment.COMMENT))
            await ctx.send(embed = emb, delete_after = 15)  
        if isinstance(error, commands.errors.CommandInvokeError):
            emb = discord.Embed(title = ':warning: О нет, произошла ошибка в команде!', color=discord.Color.red())
            emb.add_field(name = 'Ошибка:', value = f'> Возможно у меня не хватает правил или ошибка на стороне кода' )
            emb.set_footer(text = random.choice(random_comment.COMMENT))
            await ctx.send(embed = emb, delete_after = 15)  
        if isinstance(error, commands.errors.MissingRequiredArgument):
            emb = discord.Embed(title = ':warning: О нет, произошла ошибка в команде!', color=discord.Color.red())
            emb.add_field(name = 'Ошибка:', value = f'> Не правильное использование {ctx.message.content}! Пожалуйста проверьте через `mhelp <команда>`' )   
            emb.set_footer(text = random.choice(random_comment.COMMENT))
            await ctx.send(embed = emb, delete_after = 15)   
        if isinstance(error, commands.errors.CheckFailure):
            emb = discord.Embed(title = ':warning: Вы находитесь в черном списке бота', color=discord.Color.red())
            emb.add_field(name = 'Что делать?', value = '> Если вы попали в черный список бота, то выйти из него невозможно! Причину можете глянуть в команде `mprofile`' )   
            emb.set_footer(text = random.choice(random_comment.COMMENT))
            await ctx.send(embed = emb)               


def setup(client):
    client.add_cog(errors(client))
