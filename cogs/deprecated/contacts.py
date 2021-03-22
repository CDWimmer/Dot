from discord.ext import commands
from config import *
# import asyncio
from discord import utils
import discord


class ContactStaff(commands.Cog):
    """Various generic commands for communication and information"""
    def __init__(self, bot):
        self.bot = bot
        self.guild = bot.get_guild(SERVER_ID)

    @commands.command(help="Sends a suggestion to the server Staff.", aliases=["suggest"])
    async def suggestion(self, ctx, *, suggestion):
        channel = self.bot.get_guild(SERVER_ID).get_channel(CONTACT_ID)
        await ctx.author.send("You send a suggestion:")
        await ctx.author.send(utils.escape_markdown(suggestion))
        await channel.send(f"SUGGESTION received from {ctx.author.name}:")
        await channel.send(f"{utils.escape_markdown(suggestion)}")
        await ctx.send("Your suggestion was submitted. It will be reviewed by the moderators, but we can't respond to "
                       "everyone directly. ", delete_after=10)
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            # if a server channel then delete invoking message
            await ctx.message.delete()

    @commands.command(help="Sends a complaint to the server Staff.", aliases=["complain"])
    async def complaint(self, ctx, *, complaint):
        channel = self.bot.get_guild(SERVER_ID).get_channel(CONTACT_ID)
        await ctx.author.send("You send a complaint:")
        await ctx.author.send(utils.escape_markdown(complaint))
        await channel.send(f"COMPLAINT received from {ctx.author.name}:")
        await channel.send(f"{utils.escape_markdown(complaint)}")
        await ctx.send("Your complaint was submitted. It will be reviewed with the administrators.", delete_after=10)
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            # if a server channel then delete invoking message
            await ctx.message.delete()

    @commands.command(help="Sends a question to the server Staff.", aliases=["ask"])
    async def question(self, ctx, *, question):
        channel = self.bot.get_guild(SERVER_ID).get_channel(CONTACT_ID)
        await ctx.author.send("You send a question")
        await ctx.author.send(utils.escape_markdown(question))
        await channel.send(f"QUESTION received from {ctx.author.name}:")
        await channel.send(f"{utils.escape_markdown(question)}")
        await ctx.send("Your question was submitted. It will be looked at by the moderators. If we're asked similar "
                       "questions many times it may be added to some kind of FAQ. ", delete_after=10)
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            # if a server channel then delete invoking message
            await ctx.message.delete()

    @commands.command(help="Send a message to the server Staff.", aliases=["message"])
    async def contact(self, ctx, *, message):
        channel = self.bot.get_guild(SERVER_ID).get_channel(CONTACT_ID)
        await ctx.author.send("You send a message:")
        await ctx.author.send(utils.escape_markdown(message))
        await channel.send(f"CONTACT received from {ctx.author.name}:")
        await channel.send(f"{utils.escape_markdown(message)}")
        await ctx.send("Your message was sent. It will be looked at by the moderators. ", delete_after=10)
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            # if a server channel then delete invoking message
            await ctx.message.delete()

    @commands.is_owner()
    @commands.command(hidden=True)
    async def senddm(self, ctx, user: discord.User, *, msg):
        try:
            await user.send(msg)
        except Exception as e:
            print("uh oh", str(e))

    @commands.command(help=f"Send a DM to a user, will be prefixed with the line \"Response from UINJ server staff:\""
                           f"Arguments: [@User] [Your message]")
    @commands.has_permissions(kick_members=True)
    async def respond(self, ctx, user: discord.User, *, message):
        if len(message) > 1500:
            await ctx.send("Please keep responses to less than 1500 characters.")
        try:
            await user.send(f"Response from UINJ server staff:\n{message}")
        except discord.Forbidden as e:
            await ctx.send(f"I am not allowed to send a DM to that user. Error: {str(e)}")
        except Exception as e:
            await ctx.send(f"Something bad happened when trying to send a DM. Might be a problem at Discord. "
                           f"Error: {str(e)}")
        else:
            await ctx.send("Successfully sent your response.")
            # log message and author to mod-logs:
            await self.bot.get_channel(LOG_CHANNEL).send(f"{ctx.author} sent a response to user {user}:\n{message}")

    # # TODO: plain DM to users with no faff?
    # @commands.command(help=f"Send a DM to a user with no extra information. Arguments: [@User] [Your message]")
    # @commands.has_permissions(kick_members=True)
    # async def dm(self, ctx, user: discord.User, *, message):
    #     if len(message) > 1500:
    #         await ctx.send("Please keep responses to less than 1500 characters.")
    #     try:
    #         await user.send(message)
    #     except discord.Forbidden as e:
    #         await ctx.send(f"I am not allowed to send a DM to that user. Error: {str(e)}")
    #     except Exception as e:
    #         await ctx.send(f"Something bad happened that I don't understand while trying to send a DM. Might "
    #                        f"be a problem at Discord. Error: {str(e)}")
    #     else:
    #         await ctx.send("Successfully send DM!")


def setup(bot):
    bot.add_cog(ContactStaff(bot))
