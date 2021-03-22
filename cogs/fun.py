import discord
from discord.ext import commands
import asyncio
import random
import re
import aiohttp
import numpy as np
import matplotlib.pyplot as plt
from os import mkdir
from collections import defaultdict
from io import BytesIO
from matplotlib.ticker import MaxNLocator

dice_data_dir = "./fun/"
try:
    mkdir(dice_data_dir)
except FileExistsError:
    pass


class Fun(commands.Cog):
    """Silly commands"""

    def __init__(self, bot):
        self.bot = bot
        self.dice_re = re.compile(r"(?:(\d+)\s*X\s*)?(\d*)D(\d*)", re.IGNORECASE)

    @commands.command(help="Screams. (Please don't spam this.)")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def scream(self, ctx):

        await ctx.send(
            np.random.choice(["AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "MUMPH KERFUFFLE"], 1, p=[99/100, 1/100])[0]
                       )

    @commands.command(help="Flip a coin!")
    async def flip(self, ctx):
        await ctx.send(random.choice(["Heads!", "Tails!"]))

    @commands.command(help="Roll a dice in NdS format. Example: `dice 2d6` rolls 2x six-sided dice. "
                           "Max of 16 dice with 100 sides. ", aliases=["roll"])
    async def dice(self, ctx: commands.Context, dice: str = None):
        if dice is None or self.dice_re.match(dice) is None:
            await ctx.send("Please enter a dice roll, e.g. \"1d6\"")
            return
        else:
            n, s = dice.split('d')
            if not n:
                n = 1
            if not s:
                s = 6
            if int(n) > 16 or int(n) < 1:
                await ctx.send("Please keep to 16 or less dice, with 100 sides or less.")  # , delete_after=10)
                return
            if int(s) > 100 or int(s) < 1:
                await ctx.send("Please keep to 16 or less dice, with 100 sides or less.")
                return
            async with ctx.typing():
                await asyncio.sleep(0.5)
                rolls = []
                for _ in range(int(n)):
                    rolls.append(random.randint(1, int(s)))
                dice_str = ""
                for roll in rolls:
                    dice_str += "`" + str(roll) + "` "
                embed = discord.Embed(title="Dice rolling...", description=f"You rolled {n} {s}-sided dice",
                                      color=0xff00f7)
                embed.add_field(name="Dice", value=dice_str, inline=False)
                embed.add_field(name="Total", value=str(sum(rolls)), inline=False)
                if sum(rolls) == 1600:
                    embed.set_footer(text="We have a winner!")
                elif all([x==int(s) for x in rolls]):
                    embed.set_footer(text="Woah. ")
                elif int(s) in rolls:
                    embed.set_footer(text="Hey, a critical hit!")
                elif 1 in rolls:
                    embed.set_footer(text="Oof, a critical fail!")
                await ctx.send(embed=embed)

                try:
                    dice_data = np.loadtxt(dice_data_dir + f"{n}d{s}.dat", ndmin=2)
                except IOError:
                    dice_data = [[ctx.author.id, sum(rolls)]]
                else:
                    dice_data = np.append(dice_data, [[ctx.author.id, sum(rolls)]], axis=0)
                try:
                    np.savetxt(dice_data_dir + f"{n}d{s}.dat", dice_data, fmt="%d")
                except:
                    pass

    @commands.is_owner()
    @commands.command(help="Return data about all the dice rolls so far")
    async def dicedata(self, ctx: commands.Context, dice: str = None):  # here be dragons

        if dice is None or self.dice_re.match(dice) is None:
            await ctx.send("Please enter a dice roll, e.g. \"1d6\"")
            return
        else:
            n, s = dice.split('d')
            if not n:
                n = 1
            if not s:
                s = 6
            if int(n) > 16 or int(n) < 1:
                await ctx.send("Valid range is 1-16 dice with 1-100 sides.")  # , delete_after=10)
                return
            if int(s) > 100 or int(s) < 1:
                await ctx.send("Valid range is 1-16 dice with 1-100 sides.")
                return
            async with ctx.typing():
                please_wait_msg = await ctx.send("Please wait...")
                roll_totals = defaultdict(int)
                for total in np.loadtxt(dice_data_dir + f"{n}d{s}.dat", ndmin=2, usecols=1):
                    roll_totals[total[0]] += 1
                x_points = roll_totals.keys()
                y_points = roll_totals.values()
                #plt.hist(y_points,int(s)*int(n), range=[1, int(s)*int(n)])
                plt.bar(x_points, y_points, width=1)
                plt.style.use('ggplot')
                plt.tight_layout()
                plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
                #plt.xticks(list(x_points), rotation=90)
                plt.xticks(rotation=90)
                plt.title(f"{n}d{s}")
                plt.xlabel("Dice roll")
                plt.ylabel("Occurrences")
                # plt.subplots_adjust(bottom=0.1, left=0.1)
                f = BytesIO()
                plt.savefig(f, format="png", bbox_inches="tight")
                f.seek(0)
                await ctx.send(file=discord.File(f, "graph.png"))
                plt.close()
                f.close()
                await please_wait_msg.delete()
                return

    @commands.command(help="Cat pics!")
    async def randomcat(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://aws.random.cat/meow') as r:
                if r.status == 200:
                    js = await r.json()
                    await ctx.send(js['file'])
                else:
                    await ctx.send("Some sort of error o-purred! Try again later :3")

    @commands.command(help="Let me Google that for you")
    async def lmgtfy(self, ctx: commands.Context, *, msg: str):
        if msg.isdigit():
            try:
                await ctx.send(f"https://google.com/search?q={ctx.fetch_message(int(msg))}")
            except (discord.NotFound, discord.HTTPException):
                await ctx.send(f"https://google.com/search?q={msg}")
        else:
            await ctx.send(f"https://google.com/search?q="
                           f"{msg.replace(' ', '+').replace('&', '%26').replace('?', '%3F')}")


def setup(bot):
    bot.add_cog(Fun(bot))
