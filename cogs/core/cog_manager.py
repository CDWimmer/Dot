# coding: utf-8
"""
Self Updater cog for Dot the Discord Bot.
Version 2021.03.16

This cog is a core part of Dot and should almost always be loaded!

This cog provides functionality to load, unload, and reload component cogs without having to restart the entire bot.
"""
import discord
from discord.ext import commands


class Cogs(commands.Cog):

    def __init__(self, bot: commands.Bot):
        print("[CogManager] Cog loading...")
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def cog(self, ctx: commands.Context):
        """The root command of all cog/extension actions"""
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Invalid or unknown subcommand. Try `{self.bot.command_prefix}help cog`")

    @cog.command(help="Load a cog by qualified path name, e.g. `cogs.info`.")
    @commands.is_owner()
    async def load(self, ctx, *, cog_name):
        try:
            await ctx.send(f"Attempting to load `{cog_name}`")
            self.bot.load_extension(cog_name)
        except commands.ExtensionNotFound:
            await ctx.send("Extension not found.")
        except commands.ExtensionAlreadyLoaded:
            await ctx.send("Extension is already loaded!")
        except commands.ExtensionFailed as e:
            await ctx.send(f"Extension crashed while loading:\n`{e}`")
        except discord.DiscordException:
            pass
        else:
            await ctx.send("Success!")

    @cog.command(help="Reload a cog by name.")
    @commands.is_owner()
    async def reload(self, ctx, *, cog_name):
        try:
            await ctx.send(f"Attempting to reload `{cog_name}`")
            self.bot.reload_extension(cog_name)
        except commands.ExtensionNotFound:
            await ctx.send("Extension not found.")
        except commands.ExtensionNotLoaded:
            await ctx.send("Extension is not loaded!")
        except commands.ExtensionFailed as e:
            await ctx.send(f"Extension crashed while loading:\n`{e}`")
        except discord.DiscordException:
            pass
        else:
            await ctx.send("Success!")

    @cog.command(help="Unload a cog by name.")
    @commands.is_owner()
    async def unload(self, ctx, *, cog_name):
        try:
            await ctx.send(f"Attempting to unload `{cog_name}`")
            self.bot.unload_extension(cog_name)
        except commands.ExtensionNotFound:
            await ctx.send("Extension not found.")
        except commands.ExtensionNotLoaded:
            await ctx.send("Extension wasn't loaded!")
        except commands.ExtensionFailed as e:
            await ctx.send(f"Extension crashed while unloading:\n`{e}`")
        except discord.DiscordException:
            pass
        else:
            await ctx.send("Success!")

def setup(bot: commands.Bot):
    bot.add_cog(Cogs(bot))