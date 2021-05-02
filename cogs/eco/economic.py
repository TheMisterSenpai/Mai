import discord
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks

import config
from base import economicDB
from pymongo import MongoClient

cluster = MongoClient(config.MONGO)
user = cluster.ecomaidb.user

class экономика(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, per = 300, type = discord.ext.commands.BucketType.guild)
    async def work(self, ctx):
        
        await ctx.send(economicDB.WORK)

    
def setup(client):
    client.add_cog(экономика(client))