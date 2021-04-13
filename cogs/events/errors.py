import discord
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks

import config

class errors(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        emb = discord.Embed(title = ':warning: О нет, произошла ошибка в команде!', color=discord.Color.red())
        if isinstance(error, commands.BadArgument):
            emb.add_field(name = 'Ошибка:', value = f'> Пользователь не был найден на сервере или в базе данных' )
        if isinstance(error, commands.errors.MissingPermissions):
            emb.add_field(name = 'Ошибка:', value = f'> У вас не хватает правил для использование этой команды' )
        if isinstance(error, commands.errors.CommandInvokeError):
            emb.add_field(name = 'Ошибка:', value = f'> Возможно у меня не хватает правил или ошибка на стороне кода' )
        if isinstance(error, commands.errors.MissingRequiredArgument):
            emb.add_field(name = 'Ошибка:', value = f'> Не правильное использование {ctx.message.content}! Пожалуйста проверьте через `mhelp <команда>`' )              
        await ctx.send(embed = emb)    


def setup(client):
    client.add_cog(errors(client))
