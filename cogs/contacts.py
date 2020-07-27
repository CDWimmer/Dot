from discord.ext import commands
from config import *
# import asyncio
from discord import utils


class ContactStaff(commands.Cog):
    """Various generic commands for communication and information"""
    def __init__(self, bot):
        self.bot = bot
        self.guild = bot.get_guild(SERVER_ID)

    @commands.command(help="Sends a suggestion to the server Staff.", aliases=["suggest"])
    async def suggestion(self, ctx, *, suggestion):
        channel = self.guild.get_channel(CONTACT_ID)
        ctx.author.send("You send a suggestion:")
        ctx.author.send(utils.escape_markdown(suggestion))
        await channel.send(f"SUGGESTION received from {ctx.author.name}:")
        await channel.send(f"{utils.escape_markdown(suggestion)}")
        await ctx.send("Your suggestion was submitted. It will be reviewed by the moderators, but we can't respond to "
                       "everyone directly. ", delete_after=10)
        await ctx.message.delete()

    @commands.command(help="Sends a complaint to the server Staff.", aliases=["complain"])
    async def complaint(self, ctx, *, complaint):
        channel = self.guild.get_channel(CONTACT_ID)
        ctx.author.send("You send a complaint:")
        ctx.author.send(utils.escape_markdown(complaint))
        await channel.send(f"COMPLAINT received from {ctx.author.name}:")
        await channel.send(f"{utils.escape_markdown(complaint)}")
        await ctx.send("Your complaint was submitted. It will be reviewed with the administrators.", delete_after=10)
        await ctx.message.delete()

    @commands.command(help="Sends a question to the server Staff.")
    async def question(self, ctx, *, question):
        channel = self.guild.get_channel(CONTACT_ID)
        ctx.author.send("You send a question")
        ctx.author.send(utils.escape_markdown(question))
        await channel.send(f"QUESTION received from {ctx.author.name}:")
        await channel.send(f"{utils.escape_markdown(question)}")
        await ctx.send("Your question was submitted. It will be looked at by the moderators. If we're asked similar "
                       "questions many times it may be added to some kind of FAQ. ", delete_after=10)
        await ctx.message.delete()

    @commands.command(help="Send a message to the server Staff.")
    async def contact(self, ctx, *, message):
        channel = self.guild.get_channel(CONTACT_ID)
        ctx.author.send("You send a message:")
        ctx.author.send(utils.escape_markdown(message))
        await channel.send(f"CONTACT received from {ctx.author.name}:")
        await channel.send(f"{utils.escape_markdown(message)}")
        await ctx.send("Your message was sent. It will be looked at by the moderators. ", delete_after=10)
        await ctx.message.delete()

    @commands.command(help="List the boosty bois", aliases=["whopremium", "listboosters"])
    async def whoboost(self, ctx):
        members = ""
        for member in self.guild.premium_subscribers:
            members += f"**{member.name}** \n"
        if len(list(self.guild.premium_subscribers)) == 0:
            await ctx.send(f"A massive thanks to this very cool person for boosting the server:\n{members}")
        await ctx.send(f"A massive thanks to these very cool people for boosting the server:\n{members}")


def setup(bot):
    bot.add_cog(ContactStaff(bot))
