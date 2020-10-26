# coding: utf-8
"""
Config Management cog for Dot the Discord bot.
Version 2020.10.26
This cog is a required part of Dot!

This cog holds commands for the management of server configuration options like log channels which are used by other
cogs.
"""

import discord
from discord.ext import commands
import sqlite3

config_file = "config_db.db"


class Config(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # initialise the config table(s?)
        self.conn = sqlite3.connect(config_file)
        c = self.conn.cursor()
        # Ensure the creation of the in-server logging channel record, then load into memory.
        c.execute("""
                  CREATE TABLE IF NOT EXISTS log_channels (
                  id integer PRIMARY KEY,
                  guild_id text NOT NULL,
                  log_channel text NOT NULL)
                  """)
        # c.execute("""
        #           CREATE TABLE IF NOT EXISTS example (
        #           id integer PRIMARY KEY,
        #           guild text NOT NULL,
        #           channel text NOT NULL)
        #           """)
        # etc ...
        self.conn.commit()

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(ban_members=True)
    async def config(self, ctx):
        """The root command of all config options"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid or unknown sub-command...")

    # ===================== logs =================== #

    @config.group(invoke_without_command=True)
    async def logs(self, ctx):
        """The root command for all logging configuration options. """
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid or unknown sub-command...")

    @logs.command(help="Update the log channel for this server.")
    async def setchannel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Updates the log channel for the server, or sets it if there is no assigned log channel. """
        myself = ctx.guild.get_member(self.bot.user.id)
        if channel.permissions_for(myself).send_messages:
            c = self.conn.cursor()
            c.execute("SELECT log_channel FROM log_channels WHERE guild_id=?", (ctx.guild.id, ))
            # here we're just checking to make sure that there actually exists a log channel entry at all for this guild
            # and inserting a new one in the case that it's missing. Otherwise update existing entry.
            print()
            if len(c.fetchall()) == 0:
                c.execute("INSERT INTO log_channels(guild_id,log_channel) VALUES(?,?)", (ctx.guild.id, channel.id))
                self.conn.commit()
                await ctx.send(f"Log channel set to {channel.mention}. ")
            else:
                c.execute("UPDATE log_channels SET log_channel=? WHERE guild_id=?", (channel.id, ctx.guild.id))
                self.conn.commit()
                await ctx.send(f"Log channel updated to {channel.mention}. ")
        else:
            await ctx.send("I don't have permission to send messages to that channel! Fix that first, then I'll"
                           "try again!")

    @logs.command(help="Tells you which channel logs are kept in.")
    async def getchannel(self, ctx: commands.Context):
        c = self.conn.cursor()
        c.execute("SELECT log_channel FROM log_channels WHERE guild_id=?", (ctx.guild.id,))
        row = c.fetchall()
        if not row:  # if there was no entry
            await ctx.send(f"There currently isn't a log channel set! "
                           f"Please set one with `{self.bot.command_prefix}config logs setchannel #channel`")
        else:
            await ctx.send(f"The log channel is {ctx.guild.get_channel(int(row[0][0])).mention}.")

    @logs.command(help="Wipe EVERY SERVER'S LOG CHANNEL. DO NOT USE. FUCK.")
    @commands.is_owner()
    async def wipe(self, ctx: commands.Context):
        c = self.conn.cursor()
        c.execute("DELETE FROM log_channels")
        self.conn.commit()
        await ctx.send("WHAT THE FUCK DID YOU DO")

    # =============== Events =================== #

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        channels = guild.text_channels
        myself = guild.get_member(self.bot.user.id)
        for channel in channels:
            if channel.permissions_for(myself).send_messages:
                print("found new log channel :)")
                await channel.send(f"Hello! I'll use this channel as my log channel. "
                                   f"To change this, run `{self.bot.command_prefix}config logs setchannel [channel]`.")
                c = self.conn.cursor()
                c.execute("INSERT INTO log_channels(guild_id,log_channel) VALUES(?,?)", (guild.id, channel.id))
                self.conn.commit()
                break  # stop looping through channels fuckin' hell love calm down

    def cog_unload(self):
        """Nicely close the database connection and stuff :)"""
        self.conn.close()


def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(Config(bot))
