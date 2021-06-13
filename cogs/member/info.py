import discord
from discord import embeds
from discord import message
from discord.ext import commands
from discord.ext.commands.core import command
from discord.utils import get
from discord.ext import tasks
from discord import Webhook, RequestsWebhookAdapter

from contextlib import redirect_stdout
import sys
import psutil
import config
from pymongo import MongoClient

cluster = MongoClient(config.MONGO)
collection = cluster.maidb.badge
lists = cluster.maidb.bl
pr = cluster.maidb.profile

def blacklist(ctx):
    if not lists.find_one({"_id": ctx.author.id}):
        return message
    else:
        pass

class информация(commands.Cog):
    '''информационнные команды'''

    def __init__(self, client):
        self.client = client


    @commands.command(name = 'about')
    async def about(self, ctx):
        resp = await ctx.send('Информация на данный момент')
        diff = resp.created_at - ctx.message.created_at

        emb = discord.Embed(title = 'Мая#0070', color = config.INFO)
        emb.set_thumbnail(url = self.client.user.avatar_url)
        emb.add_field(name = 'Система', value = f'**ОС | {sys.platform}**\n**Discord.py | 1.7.1**\n**Python | 3.9.2**')
        emb.add_field(name = 'Статистика', value = f'**Всего серверов | {len(self.client.guilds)}**\n**Всего команд | 23**\n**Задержка API | {1000 * diff.total_seconds():.1f}мс**')
        emb.add_field(name = 'Мои разработчики', value = '[TheMisterSenpai#6701](https://sqdsh.top/hack)\n[swd#6250](https://github.com/swdblurple)')
        emb.add_field(name = 'Описание', value = 'Мая простой бот для маленьких и средних серверов дискорда. В боте есть команды для администрации, музыка, интересные команды(для некоторых нужно каналы с nsfw) и также информационные.')
        emb.add_field(name = 'Полезные ссылки', value = '[Мониторинг](https://dsrv.top/mai) • [Сервер поддержки](https://discord.gg/etc66NNCVP) • [Комментарии](https://sqdsh.top/comment) • [Донатик](https://www.donationalerts.com/r/themistersenpai) • [Пригласить меня](https://discord.com/oauth2/authorize?client_id=802987390033330227&permissions=8&scope=bot%20applications.commands) ')
        
        await resp.edit(embed = emb)
        


    @commands.command(name = 'server')
    @commands.check(blacklist)
    async def server(self, ctx):
        '''Узнать информацию о сервере
        '''
        guilds = ctx.guild

        emb = discord.Embed(title = f'Информация о {guilds.name}', color = 0x179c87)
        emb.set_thumbnail(url = guilds.icon_url)
        emb.add_field(name = 'Регион сервера', value = guilds.region)
        emb.add_field(name = 'Основной язык', value = guilds.preferred_locale)
        emb.add_field(name = 'Уровень защиты сервера', value = guilds.verification_level)
        emb.add_field(name = 'Уровень буста сервера', value = f'{guilds.premium_subscription_count} уровень')
        emb.set_footer(text='Вызвал команду: {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)

        await ctx.send(embed = emb)


    @commands.command(name = 'userinfo')
    @commands.check(blacklist)
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
    @commands.check(blacklist)
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
    
    @commands.command(name = 'avatar')
    @commands.check(blacklist)
    async def avatar(self, ctx, member: discord.Member=None):
        '''Показать аватар пользователя на сервере

        Пример:

        mavatar <@ник>
        '''
        user = ctx.message.author if (member == None) else member

        embed = discord.Embed(title=f'{user}', color= 0x008000)

        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)
    
    @commands.command(name = 'bug')
    @commands.check(blacklist)
    async def bug(self, ctx, *, bug=None):
        webhook = Webhook.partial(config.BUG_ID, config.BUGKEY, adapter=RequestsWebhookAdapter())

        if not bug:
            await ctx.send('Пожалуйста, укажите баг для того чтобы наши добрые разработчики исправили его')
        else:
            await ctx.send('Ваш баг был отправлен на сервер поддержки')

            emb = discord.Embed(title = 'новый баг')
            emb.add_field(name = 'описание бага', value = bug)

            await webhook.send(embed = emb)



def setup(client):
    client.add_cog(информация(client))
