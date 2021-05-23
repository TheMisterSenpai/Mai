import discord
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks

import config

import socket
from mcstatus import MinecraftServer
from pymongo import MongoClient

cluster = MongoClient(config.MONGO)
collection = cluster.maidb.badge
lists = cluster.maidb.bl
pr = cluster.maidb.profile

class информация(commands.Cog):
    '''информационнные команды'''

    def __init__(self, client):
        self.client = client

    @commands.command(name = 'info')
    async def info(self, ctx):

        emb = discord.Embed(color= config.INFO, title=f'Привет {ctx.author}!', description=f'''
Меня зовут Мая и создана для маленьких и средних серверов дискорда)\n**Язык программирования**: `Python 3.9`\n**Библиотека**: `discord.py 1.6.0`\n **Разработчики**:`TheMisterSenpai#6701, swd#2745`

**Полезные ссылки**:\n[Сервер Поддержки](https://discord.gg/seQTFSPAWH) | [Хелп](https://github.com/Kali4I/Rewrite-Discord-bot-Naomi) | [Пригласить меня на свой сервер](https://discord.com/api/oauth2/authorize?client_id=802987390033330227&permissions=8&scope=bot) | [BotiCord](https://sqdsh.top/mai) | [Открытый код](https://github.com/TheMisterSenpai/Mai)
''')
        emb.set_thumbnail(url = self.client.user.avatar_url)
        await ctx.send(embed = emb)

    @commands.command(name = 'mc')
    async def mc(self, ctx, ip, port=None):
        '''узнать о статусе майнкрафт сервера

        Пример:

        mmc <ip сервера>
        '''
        message = await ctx.send("Идёт сбор информации, пожалуйста подождите.")

        if port is None:
            server = MinecraftServer.lookup(f"{ip}:25565")
        else:
            try:
                server = MinecraftServer.lookup(f"{ip}:{port}")
            except ValueError:
                embed = discord.Embed(title="Ошибка Подключения", description="Порт вне допустимого диапазона **0-65535**.",
                                      color=0xb20000)
                await message.delete()
                return await ctx.send(embed=embed)

        try:
            server_ping = server.ping()
            server_status = server.status()

        except socket.timeout:
            players = "`❌ Не Доступно`"
            version = "`❌ Не Доступно`"
            description = "`❌ Не Доступно`"
            ping = "`❌ Не Доступно`"
            status = "🔴 Отключен"

        except socket.gaierror:
            embed = discord.Embed(title="Ошибка Ввода", description="Вы ввели не действительный IP или Порт.", color=0xb20000)
            await message.delete()
            return await ctx.send(embed=embed)

        except IOError as error:
            embed = discord.Embed(title="Ошибка Подключение", description="Мне не удалось получить информацию с этого сервера.\n"
                                                                          "Возможно у него стоит какая-та защита.\n\n"
                                                                          f"`Ошибка: {error}`",
                                  color=0xb20000)
            await message.delete()
            return await ctx.send(embed=embed)

        else:
            players = f"{server_status.players.online}/{server_status.players.max}"
            version = server_status.version.name

            if 'extra' in server_status.description:
                description = f"\n- {server_status.description['extra'][0]['text']}\n" \
                              f"- {server_status.description['extra'][1]['text']}\n" \
                              f"- {server_status.description['extra'][2]['text']}"
            else:
                description = server_status.description['text']

            ping = server_ping
            status = "🟢 Включен"

        if status == "🟢 Включен":
            try:
                server_query = server.query()

            except socket.timeout:
                query = "Query отключен на сервере"

            else:
                query = f"**Хост:** {server_query.host}\n" \
                        f"**Софт:** {server_query.software}\n" \
                        f"**MOTD:** {server_query.motd}\n" \
                        f"**Плагины:** {''.join(server_query.plugins)}\n" \
                        f"**Игроки:** {', '.join(server_query.players.names)}"

        else:
            query = "`❌ Не Доступно`"

        embed = discord.Embed(
            title="Статус Travedit Сервер",
            description=f"**IP:** {ip}\n"
                        f"**Описание:** {description}\n"
                        f"**Версия:** {version}",
            color=0xFF7F3F)
        embed.add_field(name="Игроки", value=players, inline=False)
        embed.add_field(name="Статус", value=status, inline=False)
        embed.add_field(name="Пинг", value=ping, inline=False)
        embed.add_field(name="Данные через Query",
                        value=query,
                        inline=False)

        await message.edit(content=None, embed=embed)


    @commands.command(name = 'userinfo')
    async def userinfo(self, ctx, member: discord.Member):
        '''узнать о человеке на сервере

        Пример:
        muserinfo @TheMisterSenpai#6701 или id пользователя
        '''
        user = ctx.message.author if (member == None) else member

        roles = member.roles
        role_list = ""
        for role in roles:
            role_list += f"<@&{role.id}> "

        emb = discord.Embed(title=f'Информация о пользователе {member}', colour = 0x179c87)
        emb.set_thumbnail(url=user.avatar_url)
        emb.add_field(name='ID', value=user.id)
        emb.add_field(name='Имя', value=user.name)
        emb.add_field(name='Высшая роль', value=user.top_role)
        emb.add_field(name='Дискриминатор', value=user.discriminator)
        emb.add_field(name='Присоеденился к серверу', value=member.joined_at.strftime('%Y.%m.%d \n %H:%M:%S'))
        emb.add_field(name='Присоеденился к Discord', value=member.created_at.strftime("%Y.%m.%d %H:%M:%S"))
        emb.add_field(name='Роли', value=role_list)
        emb.set_footer(text='Вызвал команду: {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)

        await ctx.send(embed = emb)


    @commands.command(name = 'profile')
    async def profile(self, ctx, member: discord.Member=None):
        '''Посмотреть свой или чей-то профиль на сервере

        Пример:
        mprofile @ник
        '''
        user = ctx.message.author if (member == None) else member

        if not lists.find_one({"_id": user.id}):
            await ctx.send(f'**Профиль** {user}')
            if not collection.find_one({"_id": user.id}):
                emb = discord.Embed(title = '**Значки**\n-', color = 0xffc0cb)
            else:
                badge = collection.find_one({"_id": user.id})["badge"]
                emb = discord.Embed(title = f'**Значки**\n{badge}', color = 0xffc0cb)
            emb.set_thumbnail(url=user.avatar_url)
            emb.add_field(name = '**Имя**', value = user.name)
            emb.add_field(name='**Зарегистрирован**', value=user.created_at.strftime("%d.%m.%Y"))  
            if not pr.find_one({"_id": user.id}):
                emb.add_field(name = '**О вас**', value = '```Не указанно```')
            else:
                bio = pr.find_one({"_id": user.id})["bio"]
                emb.add_field(name = '**О вас**', value = f'{bio}')    
            emb.set_footer(text='Для настройки профиля, пропишите msetbio <Биография>', icon_url=ctx.author.avatar_url)

            await ctx.send(embed=emb)

        else:
            reas = lists.find_one({"_id": user.id})["prichina"]

            emb = discord.Embed(title=f'Пользователь {user} находится в черном списке бота', colour = 0xff0000)
            emb.set_thumbnail(url=user.avatar_url)
            emb.add_field(name='Причина', value=f'{reas}')

            await ctx.send(embed=emb)

#Для настройки mprofile 
    @commands.command(name = 'setbio', hidden = True)
    async def setbio(self, ctx, *, reason=None): # member: discord.Member=None,
        
        if reason == None:
            await ctx.send('Пожалуйста укажите вашу биографию')

            return

        else:
            if not pr.find_one({"_id": ctx.author.id}):
                emb = discord.Embed(title = 'Установлена ваша биография')
                emb.add_field(name='Биография', value=f'> {reason}')
                await ctx.send(embed=emb)
                pr.insert_one({"_id": ctx.author.id, "bio": reason})
            else:
                emb = discord.Embed(title = 'Ваша биография была изменнена')
                emb.add_field(name='Биография', value=f'> {reason}')
                await ctx.send(embed=emb)
                pr.delete_one({"_id": ctx.author.id})
                pr.insert_one({"_id": ctx.author.id, "bio": reason})         
#

    @commands.command(name = 'donate')
    async def donate(self, ctx):
        emb = discord.Embed(color = 0xffc0cb)
        emb.add_field(name = 'Поддержка бота', value = f'Мая ни имеет и иметь не будет платных услуг и команд. Все донаты идут на улучшение бота, в замен вы получаете роль на тех.поддержке донатер и значок <:donater:817034726946504736> . \n```\nПеред оплатой укажите maidonate и ваш ID\n```\n')
        emb.add_field(name = 'DonateAlerts:', value = 'https://www.donationalerts.com/r/themistersenpai ')

        emb.set_thumbnail(url = self.client.user.avatar_url)
        await ctx.send(embed = emb)


    @commands.command(name = 'avatar')
    async def avatar(self, ctx, member: discord.Member=None):
        '''Показать аватар пользователя на сервере

        Пример:

        mavatar <@ник>
        '''
        user = ctx.message.author if (member == None) else member

        embed = discord.Embed(title=f'{user}', color= 0x008000)

        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(информация(client))
