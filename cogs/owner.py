import discord
from discord import message
from discord.ext import commands
from discord.ext.commands.core import command
from discord.utils import get
from discord.ext import tasks

import ast
import io
import os
import sys
import traceback
import textwrap
import platform
import psutil
import config
from pymongo import MongoClient

from contextlib import redirect_stdout

cluster = MongoClient(config.MONGO)
collection = cluster.maidb.badge
lists = cluster.maidb.bl

def insert_returns(body):
     # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

def blacklist(ctx):
    if not lists.find_one({"_id": ctx.author.id}):
        return message
    else:
        pass

class Owner(commands.Cog):
    '''Команды для тестирования и откладки бота, но может он ненужен, т.к есть jishaku)'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden = True)
    @commands.is_owner()
    async def ping(self, ctx):

    	resp = await ctx.send('Провожу тестирования...')
    	diff = resp.created_at - ctx.message.created_at
    	await resp.edit(content=f':ping_pong: Pong!\nЗадержка API: {1000 * diff.total_seconds():.1f}мс.\nЗадержка {self.bot.user.name}: {round(self.bot.latency * 1000)}мс')

    @commands.command(hidden = True)
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):

      try:
        self.bot.load_extension(cog)
      except Exception as e:
        await ctx.send(f'**`Ошибка при загрузке модуля {cog}:`** \n{type(e).__name__} - {e}')
      else:
        await ctx.send(f'**`Модуль {cog} успешно загружен`**')

    @commands.command(hidden = True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):

      try:
        self.bot.unload_extension(cog)
      except Exception as e:
        await ctx.send(f'**`Ошибка при выгрузке модуля {cog}:`** \n{type(e).__name__} - {e}')
      else:
        await ctx.send(f'**`Модуль {cog} успешно выгружен`**')

    @commands.command(hidden = True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):

      try:
        self.bot.unload_extension(cog)
        self.bot.load_extension(cog)
      except Exception as e:
        await ctx.send(f'**`Ошибка при перезагрузке модуля {cog}:`** \n{type(e).__name__} - {e}')
      else:
        await ctx.send(f'**`Модуль {cog} успешно перезагружен`**')

    @commands.command(hidden = True)
    @commands.is_owner()
    async def debug(self, ctx, on_off=None):
        if not on_off:
            await ctx.send('**Чумба**, выбери включить или выключить дебаг')

            return
        if on_off == 'on':
            self.bot.unload_extension('cogs.events.errors')
            await ctx.send(f'{ctx.author.mention} :white_check_mark:')
        elif on_off == 'off':
            self.bot.load_extension('cogs.events.errors')
            await ctx.send(f'{ctx.author.mention} :white_check_mark:')
        else:
            await ctx.send('>W<')

    @commands.command(hidden = True)
    @commands.is_owner()
    async def eval(self, ctx, *, cmd):
        try:
            fn_name = "_eval_expr"

            cmd = cmd.strip("` ")

            # add a layer of indentation
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

            # wrap in async def body
            body = f"async def {fn_name}():\n{cmd}"

            parsed = ast.parse(body)
            body = parsed.body[0].body

            insert_returns(body)

            env = {
                'bot': ctx.bot,
                'discord': discord,
                'commands': commands,
                'ctx': ctx,
                '__import__': __import__
            }
            exec(compile(parsed, filename="<ast>", mode="exec"), env)

            result = (await eval(f"{fn_name}()", env))
            await ctx.send(result)

        except Exception as error:
            return await ctx.send(embed=discord.Embed(description=f'В вашем коде произошла следующая ошибка:\n`{error}`', color = 0xff0000))

    @commands.command(hidden = True, name = 'badge', pass_context=True)
    @commands.is_owner()
    async def badge(self, ctx, add_remove=None, member: discord.Member = None, emoji: discord.Emoji = None):
        
        if not member:
            member = ctx.author

        if add_remove is None:
            await ctx.send('Напиши, что ты хочешь сделать добавить или убрать значок, **чумба** ведь сам код писал и не помнишь')
            return

        if add_remove == 'remove':
            if not collection.find_one({"_id": member.id, "badge": "<:" + emoji.name + ":" + str(emoji.id)+ ">"}):
                await ctx.send("Что ты будешь уберать, если у него ничего нет?")
            else:
                await ctx.send(f'{ctx.author.mention} :white_check_mark: ')
                collection.delete_one({"_id": member.id})
        elif add_remove == 'add':
            if member is None:
                await ctx.send('Кому собираешься добавить значок?')
            else:
                if not collection.find_one({"_id": member.id}): 
                    collection.insert_one({"_id": member.id, "badge": "<:" + emoji.name + ":" + str(emoji.id)+ ">"})
                    await ctx.send(f' {ctx.author.mention} :white_check_mark: ')
                else:
                    data = collection.find_one({"_id": member.id})
                    collection.update_one({"_id": member.id},
                        {"$set": {"badge": data["badge"] + " " + "<:" + emoji.name + ":" + str(emoji.id)+ ">"}})
                    await ctx.send(f'{ctx.author.mention} :white_check_mark: ')
        else:
            await ctx.send('Хоть бы, что-то указал')

    @commands.command(name = 'bl', hidden = True)
    @commands.is_owner()
    async def bl(self, ctx, member: discord.Member=None, *, reason=None):
        if not member:
            member = ctx.author

            await ctx.send('Укажи человека и причину, чтобы добавить его в ЧС')

            return

        if reason == None:
            await ctx.send('✅')
            lists.insert_one({"_id": member.id, "prichina": "Без указание причины"})

        else:
            await ctx.send(f'✅')
            lists.insert_one({"_id": member.id, "prichina": reason})

    @commands.command(name = 'sy', hidden = True)
    @commands.is_owner()
    async def sy(self, ctx, member: discord.Member=None):

        if not member:
            member = ctx.author
            await ctx.send('Укажи человека, чтобы убрать его в ЧС')

            return

        else:
            await ctx.send('✅')
            lists.delete_one({"_id": member.id})

    @commands.command(name = 'test', hidden = True)
    @commands.check(blacklist)
    async def test(self, ctx):
        await ctx.send('senpai zhopa')

def setup(client):
    client.add_cog(Owner(client))
