import discord
from discord.ext import commands

"""This custom help command is a perfect replacement for the default one on any Discord Bot written in Discord.py!
However, you must put "bot.remove_command('help')" in your bot, and the command must be in a cog for it to work.
Written by Jared Newsom (AKA Jared M.F.)! - edited by ceron21"""


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def help(self, ctx, *cog):
        """Gets all cogs and commands of mine."""
        try:
            if not cog:
                """Cog listing.  What more?"""
                halp = discord.Embed(title='Command Categories. ',
                                     description='Use `!help *Category*` to find out more about them!')
                cogs_desc = ''
                for x in self.bot.cogs:
                    cogs_desc += ('{} - {}'.format(x, self.bot.cogs[x].__doc__) + '\n')
                halp.add_field(name='Cogs', value=cogs_desc[0:len(cogs_desc) - 1], inline=False)
                cmds_desc = ''
                for y in self.bot.walk_commands():
                    if not y.cog_name and not y.hidden:
                        cmds_desc += ('{} - {}'.format(y.name, y.help) + '\n')
                if cmds_desc != '':
                    halp.add_field(name='Uncatergorized Commands', value=cmds_desc[0:len(cmds_desc) - 1], inline=False)
                await ctx.message.add_reaction(emoji='✉')
                await ctx.message.author.send('', embed=halp)
            else:
                splice = cog[0]
                cog = splice[0].upper() + splice[1:].lower()
                # printing commands of cog
                """Command listing within a cog."""
                found = False
                # finding Cog
                for x in self.bot.cogs:
                    # for y in cog:
                    if x == cog:
                        # making title
                        halp = discord.Embed(title=cog + ' - Commands', description=self.bot.cogs[cog].__doc__,
                                             color=discord.Color.green())
                        for c in self.bot.get_cog(cog).get_commands():
                            if not c.hidden:  # if cog not hidden
                                halp.add_field(name=c.name, value=c.help, inline=False)
                        found = True
                    if not found:
                        """Reminds you if that cog doesn't exist."""
                        halp = discord.Embed(title='Error!', description='How do you even use "' + cog[0] + '"?',
                                             color=discord.Color.red())
                    else:
                        await ctx.message.add_reaction(emoji='✉')
                    await ctx.message.author.send('', embed=halp)
        except Exception as e:
            await ctx.send("Excuse me, something broke in the help command: " + str(e))


def setup(bot):
    bot.remove_command('help')
    bot.add_cog(Help(bot))
