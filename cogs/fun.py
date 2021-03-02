import discord
from discord.ext import commands
import asyncio
import random
import re
import aiohttp


class Fun(commands.Cog):
    """Silly commands"""

    def __init__(self, bot):
        self.bot = bot
        self.dice_re = re.compile(r"(?:(\d+)\s*X\s*)?(\d*)D(\d*)", re.IGNORECASE)

    @commands.command(help="Screams. (Please don't spam this.)")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def scream(self, ctx):
        await ctx.send("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")

    @commands.command(help="Flip a coin!")
    async def flip(self, ctx):
        await ctx.send(random.choice(["Heads!", "Tails!"]))

    @commands.command(help="Roll a dice in NdS format. Example: `dice 2d6` rolls 2x six-sided dice. "
                           "Max 10 dice of 100 sides. Leave blank for 1d6.", aliases=["roll"])
    async def dice(self, ctx, dice: str = None):
        if dice is None or self.dice_re.match(dice) is None:
            await ctx.send("Please enter a dice roll, e.g. \"1d6\"")
            return
        else:
            n, s = dice.split('d')
            if not n:
                n = 1
            if not s:
                s = 6
            if int(n) > 16:
                await ctx.send("Please keep to 16 or less dice, with 100 sides or less.")  # , delete_after=10)
                return
            if int(s) > 100:
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
                if s in rolls:
                    embed.set_footer(text="Hey, a critical hit!")
                elif 1 in rolls:
                    embed.set_footer(text="Oof, a critical fail!")
                await ctx.send(embed=embed)

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
