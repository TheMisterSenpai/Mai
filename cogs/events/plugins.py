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

class dungermaster(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):

        auro = autorole.find_one({"role_id": role.id})

        guilded = welcum.find_one({"guild_id": ctx.guild.id})
        channelel = welcum.find_one({"guild_id": ctx.guild.id})["channel_id"]
        textet = welcum.find_one({"guild_id": ctx.guild.id})["text"]

        gui = discord.utils.get(client.guilds, id = guilded)
        cha  = discord.utils.get(gui.channels, id = channelel)

        roles = discord.utils.get( member.guild.roles, id = auro)
        await member.add_roles( roles )
        await cha.send(f'> {textet}')


def setup(client):
    client.add_cog(dungermaster(client))
