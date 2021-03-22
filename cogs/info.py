from discord.ext import commands
import discord
from datetime import datetime


class Info(commands.Cog):
    """Information"""

    def __init__(self, bot):
        self.bot = bot
        # self.guild = bot.get_guild(SERVER_ID)

    @commands.guild_only()
    @commands.command(help="Tells you some stats about the server.")
    async def serverinfo(self, ctx):
        # icon = ctx.guild.icon_url
        created = ctx.guild.created_at.date()
        age = datetime.now().date() - created
        total_members = ctx.guild.member_count
        online_members = len([member for member in ctx.guild.members if member.status != discord.Status.offline and not
                              member.bot])
        embed = discord.Embed(title=f"__{ctx.guild.name}__", description=f"Guild information",
                              color=0xff00f7)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name="Members", value=str(total_members), inline=False)
        embed.add_field(name="Online", value=str(online_members), inline=False)
        embed.add_field(name="Server birthday", value=f"{created} ({age.days} days old)")
        embed.set_footer(text=f"Guild owner: {ctx.guild.owner.name}", icon_url=ctx.guild.owner.avatar_url)
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command(help="Lists the server boosters", aliases=["whopremium", "listboosters", "showboosters",
                                                                 "listboosts", "showboosts", "whosubscribe",
                                                                 "boosters", "subscribers"])
    async def whoboost(self, ctx):
        members = ""
        for member in ctx.message.guild.premium_subscribers:
            members += f"{member.name}#{member.discriminator} \n"
        if len(list(ctx.message.guild.premium_subscribers)) == 1:
            embed = discord.Embed(title="Guild Boosters", description="A massive thanks to this very cool person for "
                                                                      f"boosting the server", color=0x00FFFF)
            embed.add_field(name="Booster", value=f"{members}")
        elif len(list(ctx.message.guild.premium_subscribers)) > 1:
            embed = discord.Embed(title="Guild Boosters", description="A massive thanks to these very cool people for "
                                                                      "boosting the server", color=0x00FFFF)
            embed.add_field(name="Boosters", value=f"{members}")
        else:
            embed = discord.Embed(title="Server Boosters", description=f"Currently, there are no boosters on this "
                                                                       f"server :cry:", color=0x00FFFF)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
