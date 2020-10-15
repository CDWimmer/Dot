from discord.ext import commands
from config import *
# import asyncio
from discord import utils
import discord
from datetime import datetime

class Info(commands.Cog):
    """Information"""
    def __init__(self, bot):
        self.bot = bot
        # self.guild = bot.get_guild(SERVER_ID)

    @commands.command(help="Tells you some stats about the server.")
    async def serverinfo(self, ctx):
        server = ctx.guild.name
        #icon = ctx.guild.icon_url
        created = ctx.guild.created_at.date()
        age = datetime.now().date() - created
        total_members = ctx.guild.member_count
        online_members = len([member for member in ctx.guild.members if member.status != discord.Status.offline and not member.bot])

        msg = f"*__{server}__*\n{online_members} out of {total_members} online members.\nCreated {created} ({age.days } days old)"
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(Info(bot))

