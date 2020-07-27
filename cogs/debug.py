from discord.ext import commands
import discord
import random
import asyncio

class Debug(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(help="Debug command.")
    async def getcachedms(self, ctx):
        for user in self.bot.users:
            try:
                if user.dm_channel is not None:
                    print(f"Found DMs from {user.name}:")
                    async for message in user.dm_channel.history():
                        print(f"\tMessage: {message.content}")
                        if len(message.attachments) > 0:
                            print(f"\t\twith {len(message.attachments)} attachments")
            except:
                pass

    @commands.is_owner()
    @commands.command(help="Debug command.")
    async def getuserdms(self, ctx, username: discord.User):
        if username.dm_channel is not None:
            async for message in username.dm_channel.history(limit=100):
                print(f"===========\n{message.content}")
                if len(message.attachments) > 0:
                    print(f"\t\twith {len(message.attachments)} attachments:")
                    for att in message.attachments:
                        print(att.url)
        else:
            print("No DMs with", username.name)

    @commands.is_owner()
    @commands.command(help="This restarts the bot.",
                      aliases=["reboot", "rebooty"])
    async def restart(self, ctx):
        """This restarts the bot."""
        async with ctx.typing():
            await asyncio.sleep(1)
            await ctx.send(random.choice(
                ["Back soon :*", "Hold on...", "Back in a second!", "Restarting...", "Rebooting...",
                 "Answering a rebooty call..."]))
            print("Logging out")
            global exit_code
            exit_code = 0
            await self.bot.logout()

        await ctx.message.delete()

    @commands.is_owner()
    @commands.command(help="This kills the bot. ",
                      aliases=["halt", "Halt", "die", "Die", "getthefuckout", "eatadick", "fuckoff",
                               "suckacock", "getfucked", "commitgodie", "shutthefuckup", "goaway", "toasterbath"])
    async def stop(self, ctx):
        """This kills the bot."""
        async with ctx.typing():
            await asyncio.sleep(1)
            await ctx.send(random.choice(
                ["Goodbye", "Shutting down", "Bye bye!", "L8r!", "Going offline",
                 "*Windows XP shutdown noise*", "Auf Wiedersehen, pet"]))
            print("Logging out")
            global exit_code
            exit_code = 2
            await self.bot.logout()


def setup(bot):
    bot.add_cog(Debug(bot))
