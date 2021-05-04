import discord
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks

import config
from base import economicDB
from pymongo import MongoClient
import random

cluster = MongoClient(config.MONGO)
bal = cluster.ecomaidb.user

class экономика(commands.Cog):
    def __init__(self, client):
        self.client = client

    #заработок и перевод
    @commands.command(name = 'work')
    @commands.cooldown(1, per = 300, type = discord.ext.commands.BucketType.user) # кулдаун на 5 часов
    async def work(self, ctx):
        '''Заработать валюту 
        
        Пример:
        mwork
        '''
        coins = random.randint(1, 25) 
        data = bal.find_one({"_id": ctx.author.id})
        
        emb = discord.Embed(title = 'Рабочий день закончился', color = discord.Color.green())
        emb.add_field(name = 'Работа', value = random.choice(economicDB.WORK))
        emb.add_field(name = 'Заработали', value = f'{coins} :coin:')
        
        bal.update_one({"_id": ctx.author.id}, 
            {"$set": {"balance": data["balance"] + coins}})

        emb.set_footer(text = 'Ваш баланс отображается в mprofile')
        await ctx.send(embed = emb)

    @commands.command()
    async def pay(self, ctx, member: discord.Member, amount: int):
        '''Перевести деньги другому пользователю
        
        Пример:
        mpay @TheMisterSenpai#6701 25
        '''
        rem = bal.find_one({"_id": ctx.author.id})["balance"]
        add = bal.find_one({"_id": member.id})["balance"]

        if amount <= 0:
            await ctx.send(f"Простите, но вы не можете перевести {amount} монет")
        
        else: 
            if rem <= 0:
                await ctx.send(f'О нет, ваш баланс составляет {rem} :coin:')
            else:
                bal.update_one({"_id": ctx.author.id},
                    {"$set": {"balance": rem - amount}})
            
                bal.update_one({"_id": member.id},
                    {"$set": {"balance": add + amount}})

                await ctx.message.add_reaction("✅")
    
    '''
    #Магазин
    @commands.command()
    async def shop(self, ctx):
    ''' 
        

    
def setup(client):
    client.add_cog(экономика(client))
