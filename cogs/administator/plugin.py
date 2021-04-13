import discord
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks

import config
from pymongo import MongoClient

cluster = MongoClient(config.MONGO)
# разные плагины
autorole = cluster.maidb.autorole
welcum = cluster.maidb.welcome_text

class плагины(commands.Cog):
    '''Настройки для вашего дискорда сервера'''

    def __init__(self, client):
        self.client = client

    @commands.command(name = 'autorole', hidden = True)
    @commands.has_permissions( administrator = True )
    async def autorole(self, ctx, on_off=None, role: discord.Role=None):
        '''Добавлять при входе пользователям роль(пока что можно добавить 1 роль)

        Пример:

        mautorole on/off @роль
        '''
        if on_off is None:
            await ctx.send('Чтобы установить авто-роли, пожалуйста укажите on или убрать, то off')

        elif on_off == 'off':
            if not autorole.find_one({"role_id": role.id}):
                await ctx.send('**Невозможно** было отключить авто-роли, т.к их никто не включал')
            else:
                await ctx.send('**Авто-роли** были выключины')
                autorole.delete_one({"role_id": role.id})
        elif on_off == 'on':
            if role is None:
                await ctx.send('**Невозможно** было отключить авто-роли, т.к вы не указали роль')
            else:
                await ctx.send('**Авто-роли** были включены')
                autorole.insert_one({"role_id": role.id})
        else:
            await ctx.send('Чтобы установить авто-роли укажите on/off')

    @commands.command(name = 'welcome', hidden = True)
    @commands.has_permissions( administrator = True )
    async def welcome(self, ctx, set_remove=None, channel: discord.TextChannel=None, *, reason=None):
        '''Приветствие при входе на сервер

        Пример:

        mwelcome set/remove #канал текст приветствия
        '''
        if set_remove is None:
            await ctx.send('Чтобы установить текст приветстивия для этого нужно указать set или remove чтобы убрать их')

        elif set_remove == 'remove':
            if not welcum.find_one({"guild_id": ctx.guild.id}):
                await ctx.send('**Невозможно** убрать приветствия, т.к их и небыло)')
            else:
                await ctx.send('Приветствие были убраны с вашего сервера')
                welcum.delete_one({"guild_id": ctx.guild.id})

        elif set_remove == 'set':
            if reason is None:
                await ctx.send('Приветствия были не включины, т.к вы не указали текст')
            else:
                await ctx.send(f'Приветствия были добавлены. Текст: {reason}')
                welcum.insert_one({"guild_id": ctx.guild.id, "channel_id": channel.id, "text": reason})

def setup(client):
    client.add_cog(плагины(client))
