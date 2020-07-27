# import discord
from discord.ext import commands
import asyncio
import random
import re


class Fun(commands.Cog):
    """Silly commands"""

    def __init__(self, bot):
        self.bot = bot
        self.dice_re = re.compile(r"(?:(\d+)\s*X\s*)?(\d*)D(\d*)", re.IGNORECASE)

    @commands.command(help="Screams. (Please don't spam this.)")
    # @commands.cooldown(1, 15, commands.BucketType.user)
    async def scream(self, ctx):
        await ctx.send("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")

    @commands.command(help="Flip a coin!")
    async def flip(self, ctx):
        await ctx.send(random.choice(["Heads!", "Tails!"]))

    @commands.command(help="Roll a dice in NdS format. Examples: `dice 2d6` rolls 2x six-sided dice. "
                           "Max 10 dice of 100 sides. Leave blank for 1d6.")
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
                await ctx.send(f"You rolled {n} {s}-sided dice...")
                msg = '*Result:* '
                rolls = []
                for _ in range(int(n)):
                    rolls.append(random.randint(1, int(s) + 1))
                await asyncio.sleep(0.9)
                for roll in rolls:
                    msg += str(roll) + " "
                msg += f"\n*Total:* {sum(rolls)}"
                await ctx.send(msg)


def setup(bot):
    bot.add_cog(Fun(bot))
