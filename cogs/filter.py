# coding: utf-8
"""
Word Filter cog for Dot the Discord bot.
Version 2021.06.09

A Configurable per-server word filter.

Ensure that the bot has a log channel set up from Config Manager for this to send logs into.

Logging stuff for the explicit purpose of moderation is fine:
https://gist.github.com/meew0/a3168b8fbb02d5a5456a06461b9e829e

Dependencies:
-------------
- Config Manager (configmgr.py) cog

"""

from collections import defaultdict
from discord.ext import commands
import discord
import sqlite3

CONFIG_FILE = "config_db.db"
FILTER_CONFIG_FILE = "filter_db.db"


# TODO: Fix it so it doesn't delete your command message that just removed a word from the whitelist or added a major
#  filter word. Suggestions: 1-Add a user whitelist. or 2-Anyone with permission to use the commands.


class WordFilter(commands.Cog):

    def __init__(self, bot: commands.Bot):
        print("[WordFilter] Starting Cog...")
        self.bot = bot
        self.major_filter = {}
        self.minor_filter = {}
        self.whitelist = {}
        # Connect to the config DB:
        self.config_conn = None
        try:
            self.config_conn = sqlite3.connect(CONFIG_FILE)
        except sqlite3.Error as e:
            raise Exception(f"Connection to global config database failed! {str(e)}")
        else:
            pass  # all's good.

        # Connect to word filter DB:
        self.conn = None
        try:
            self.conn = sqlite3.connect(FILTER_CONFIG_FILE)
            print(sqlite3.version)
        except sqlite3.Error as e:
            raise Exception(f"Connection to filter database failed! {str(e)}")
        else:
            # connected, ensure tables exist then try loading words into dicts :)
            try:
                c = self.conn.cursor()
                c.execute("""
                          CREATE TABLE IF NOT EXISTS minor_filter (
                          id integer PRIMARY KEY,
                          guild_id text NOT NULL,
                          word text NOT NULL)
                          """)
                c.execute("""
                          CREATE TABLE IF NOT EXISTS major_filter (
                          id integer PRIMARY KEY,
                          guild_id text NOT NULL,
                          word text NOT NULL)
                          """)
                c.execute("""
                          CREATE TABLE IF NOT EXISTS whitelist (
                          id integer PRIMARY KEY,
                          guild_id text NOT NULL,
                          word text NOT NULL)
                          """)
                self.conn.commit()
            except sqlite3.Error as e:

                print("[WordFilter] Error creating filter database tables.")
                raise e
            try:
                c.execute("SELECT guild_id,word FROM minor_filter")
                rows_minor = c.fetchall()
                c.execute("SELECT guild_id,word FROM major_filter")
                rows_major = c.fetchall()
                c.execute("SELECT guild_id,word FROM whitelist")
                rows_whitelist = c.fetchall()
            except sqlite3.Error as e:
                print(e)
                pass  # likely the tables don't exist
            else:  # go through and load all the lists into memory:
                self.minor_filter = defaultdict(list)
                for r in rows_minor:
                    self.minor_filter[int(r[0])].append(r[1])

                self.major_filter = defaultdict(list)
                for r in rows_major:
                    self.major_filter[int(r[0])].append(r[1])

                self.whitelist = defaultdict(list)
                for r in rows_whitelist:
                    self.whitelist[int(r[0])].append(r[1])

        print("[WordFilter] Cog successfully loaded!")

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(kick_members=True)
    async def wordfilter(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid or unknown sub-command...")

    # ============== Word Addition ============ #

    @wordfilter.group(invoke_without_command=True)
    @commands.has_permissions(ban_members=True)
    async def add(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid or unknown sub-command...")

    @add.command(help="Add a word to the minor filter", name='minor')
    @commands.has_permissions(ban_members=True)
    async def add_minor(self, ctx, word: str):
        word = word.lower()
        if word not in self.minor_filter[ctx.guild.id]:
            try:
                c = self.conn.cursor()
                c.execute("INSERT INTO minor_filter(guild_id,word) VALUES(?,?)", (ctx.guild.id, word))
                self.conn.commit()
            except sqlite3.Error as e:
                await ctx.send(f"A database error occurred: {str(e)}")
            else:  # it worked, add to in-memory list too:
                self.minor_filter[ctx.guild.id].append(word.lower())
                await ctx.send("Added word to minor filter.")
        else:
            await ctx.send("Word already in minor list.")

    @add.command(help="Add a word to the major filter.", name='major')
    @commands.has_permissions(ban_members=True)
    async def add_major(self, ctx, word: str):
        word = word.lower()
        if word not in self.major_filter[ctx.guild.id]:
            try:
                c = self.conn.cursor()
                c.execute("INSERT INTO major_filter(guild_id,word) VALUES(?,?)", (ctx.guild.id, word))
                self.conn.commit()
            except sqlite3.Error as e:
                await ctx.send(f"A database error occurred: {str(e)}")
            else:  # it worked, add to in-memory list too:
                self.major_filter[ctx.guild.id].append(word.lower())
                await ctx.send("Added word to major filter.")
        else:
            await ctx.send("Word already in major list.")

    @add.command(help="Add a word to the ignore list/whitelist.", name='whitelist')
    @commands.has_permissions(ban_members=True)
    async def add_whitelist(self, ctx, word: str):
        word = word.lower()
        if word not in self.whitelist[ctx.guild.id]:
            try:
                c = self.conn.cursor()
                c.execute("INSERT INTO whitelist(guild_id,word) VALUES(?,?)", (ctx.guild.id, word))
                self.conn.commit()
            except sqlite3.Error as e:
                await ctx.send(f"A database error occurred: {str(e)}")
            else:  # it worked, add to in-memory list too:
                self.whitelist[ctx.guild.id].append(word.lower())
                await ctx.send("Added word to whitelist.")
        else:
            await ctx.send("Word already in whitelist.")

    # =========== Word Removal =========== #

    @wordfilter.group(invoke_without_command=True)
    @commands.has_permissions(ban_members=True)
    async def remove(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid or unknown sub-command...")

    @remove.command(help="Remove a word from the minor filter.", name='minor')
    @commands.has_permissions(ban_members=True)
    async def remove_minor(self, ctx, word: str):
        if word in self.minor_filter[ctx.guild.id]:
            try:
                c = self.conn.cursor()
                c.execute("DELETE FROM minor_filter where guild_id=? AND word=?", (ctx.guild.id, word))
                self.conn.commit()
            except sqlite3.Error as e:
                await ctx.send(f"A database error occurred: {str(e)}")
            else:  # it worked, remove from in-memory list too:
                self.minor_filter[ctx.guild.id].remove(word.lower())
                await ctx.send("Removed word from minor filter.")
        else:
            await ctx.send("Word not in minor list.")

    @remove.command(help="Remove a word from the major filter.", name='major')
    @commands.has_permissions(ban_members=True)
    async def remove_major(self, ctx, word: str):
        if word in self.major_filter[ctx.guild.id]:
            try:
                c = self.conn.cursor()
                c.execute("DELETE FROM major_filter where guild_id=? AND word=?", (ctx.guild.id, word))
                self.conn.commit()
            except sqlite3.Error as e:
                await ctx.send(f"A database error occurred: {str(e)}")
            else:  # it worked, remove from in-memory list too:
                self.major_filter[ctx.guild.id].remove(word.lower())
                await ctx.send("removed word from major filter.")
        else:
            await ctx.send("Word not in major list.")

    @remove.command(help="Remove a word from the whitelist.", name='whitelist')
    @commands.has_permissions(ban_members=True)
    async def remove_whitelist(self, ctx, word: str):
        if word in self.whitelist[ctx.guild.id]:
            try:
                c = self.conn.cursor()
                c.execute("DELETE FROM whitelist where guild_id=? AND word=?", (ctx.guild.id, word))
                self.conn.commit()
            except sqlite3.Error as e:
                await ctx.send(f"A database error occurred: {str(e)}")
            else:  # it worked, remove from in-memory list too:
                self.whitelist[ctx.guild.id].remove(word.lower())
                await ctx.send("removed word from whitelist.")
        else:
            await ctx.send("Word not in whitelist.")

    # ========== Word Display ============= #

    @wordfilter.group(invoke_without_command=True)
    @commands.has_permissions(ban_members=True)
    async def show(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid or unknown sub-command...")

    @show.command(help="List the words in the minor filter.", name='minor')
    @commands.has_permissions(kick_members=True)
    async def show_minor(self, ctx):
        msg = "__Minor Filter Words__\n"
        for word in self.minor_filter[ctx.guild.id]:
            msg += word + " "
        await ctx.send(msg)

    @show.command(help="List the words in the major filter.", name='major')
    @commands.has_permissions(kick_members=True)
    async def show_major(self, ctx):
        msg = "__Major Filter Words__\n"
        for word in self.major_filter[ctx.guild.id]:
            msg += word + " "
        await ctx.send(msg)

    @show.command(help="List the words in the whitelist.", name='whitelist')
    @commands.has_permissions(kick_members=True)
    async def show_whitelist(self, ctx):
        msg = "__Whitelisted Words__\n"
        for word in self.whitelist[ctx.guild.id]:
            msg += word + " "
        await ctx.send(msg)

    # ========= Filter implementation ========== #

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if isinstance(message.channel, discord.channel.DMChannel):
            return  # don't care about DMs.
        if message.author == self.bot.user:
            return  # don't reply to ourselves lol.
        if message.author.guild_permissions.ban_members:
            return  # leave administrators alone.

        def get_log_channel():
            """Helper function to obtain the server's log channel. """
            c = self.config_conn.cursor()
            c.execute("SELECT log_channel FROM log_channels WHERE guild_id=?", (message.guild.id,))
            log_channel_id = int(c.fetchall()[0][0])
            return message.guild.get_channel(log_channel_id)

        # Remove whitelisted words before further processing:
        msg_filtered = message.content.lower()
        try:
            for word in self.whitelist[message.guild.id]:
                msg_filtered = msg_filtered.replace(word, "")
        except KeyError:
            pass  # no words configured for that server I guess
        #  Filter for suspect stuff:
        try:
            if any(x in msg_filtered for x in self.minor_filter[message.guild.id]):  # detected minor word
                channel = get_log_channel()  # helper function
                await channel.send(f"Word filter detected a potentially minor offensive message:\n"
                                   f"{message.jump_url}\n"
                                   f"Sent by {message.author.display_name} (id: `{message.author.id}`) in channel "
                                   f"'{message.channel.mention} (id: `{message.channel.id}`)'.\n"
                                   f"Message read:")
                await channel.send(f"{message.content}")
        except KeyError:
            pass  # no words configured for that server I guess
        try:
            if any(x in msg_filtered for x in self.major_filter[message.guild.id]):
                channel = get_log_channel()  # helper function
                await channel.send(f"Word filter detected a potentially major offensive message and will delete it.\n"
                                   f"Sent by {message.author.display_name} (id: `{message.author.id}`) in channel "
                                   f"'{message.channel.mention} (id: `{message.channel.id}`)'.\n"
                                   f"Message read:")
                await channel.send(f"{message.content}")
                try:
                    await message.delete()
                except discord.Forbidden:
                    await channel.send(f"I am not allowed to delete messages in that channel. Here is a link to it:\n"
                                       f"{message.jump_url}")
        except KeyError:
            pass  # no words configured for that server I guess

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Compare the before and after of a member update and check if it's done anything fancy"""
        # print("Member update detected")
        if after.guild_permissions.ban_members:
            return  # ignore admins!
        if before.status != after.status:
            pass  # ignore status changes
        if before.activity != after.activity:
            pass  # ignore activity changes
        if before.nick != after.nick and after.nick is not None:  # `is not None` so a reset doesn't trigger it again.
            nick_filtered = after.nick
            print(before.nick, after.nick)
            print(nick_filtered)
            for word in self.whitelist[after.guild.id]:  # remove whitelist items
                nick_filtered = nick_filtered.replace(word, "")
            if any(x in nick_filtered for x in self.major_filter[after.guild.id]):
                # get log channel for this server...
                log_channel_id = None
                c = self.config_conn.cursor()
                c.execute("SELECT log_channel FROM log_channels WHERE guild_id=?", (after.guild.id,))
                row = c.fetchall()
                if not row:  # There is no log channel. Fuck! Up to server operator to solve that one.
                    print(f"[WordFilter] There is no log channel set for server with id ({after.guild.id}).")
                else:
                    log_channel_id = int(row[0][0])

                channel = after.guild.get_channel(log_channel_id)
                try:
                    await channel.send(f"The member `{after.name}` (with id `{after.id}`) has set a profane nickname "
                                       f"('{after.nick}'), I'll attempt to reset it and DM them about it.")
                    await after.edit(reason="Reset profane nickname.", nick=None)
                except discord.Forbidden as e:
                    await channel.send(f"Word Filter tried to reset a nickname but failed. "
                                       f"Does my role allow me to change nicknames, and is that role *higher* on the "
                                       f"list than the person whose nickname I tried to change? "
                                       f"\nError: {str(e)}")
                try:
                    await after.send(f"You tried to set your nickname to something containing strong profanity. "
                                     f"This has been reversed. If you think this has been done in error, please contact"
                                     f" a server administrator to add it to the whitelist. "
                                     f"For reference, you tried to changed your nick to `{after.nick}`. ")
                except discord.Forbidden as e:
                    await channel.send(f"Failed to DM the user about their nickname. I might not be allowed to DM that "
                                       f"person. "
                                       f"\nError: {str(e)}")
                except discord.HTTPException:
                    await channel.send(f"The nickname was on a bot, so I did not DM them, because Discord does not like"
                                       f" me doing that. ")

    # ================= DB Management ================ #

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def filterdb(self, ctx):
        """A bunch of database management commands for the bot owner."""
        if ctx.invoked_subcommand is None:
            await ctx.send('Missing or unknown sub-command...')

    @filterdb.command(help="Show list of DB tables.")
    @commands.is_owner()
    async def showtables(self, ctx):
        c = self.conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        msg = "__tables__\n"
        for item in c.fetchall():
            msg += (item[0]) + " "
        await ctx.send(msg)

    @filterdb.command(help="")
    @commands.is_owner()
    async def reloaddb(self, ctx):
        c = self.conn.cursor()
        try:
            c.execute("SELECT guild_id,word FROM minor_filter")
            rows_minor = c.fetchall()
            c.execute("SELECT guild_id,word FROM major_filter")
            rows_major = c.fetchall()
            c.execute("SELECT guild_id,word FROM whitelist")
            rows_whitelist = c.fetchall()
        except sqlite3.Error as e:
            ctx.send(f"Failed with error: {str(e)}")
        else:
            self.minor_filter = defaultdict(list)
            for r in rows_minor:
                self.minor_filter[int(r[0])].append(r[1])

            self.major_filter = defaultdict(list)
            for r in rows_major:
                self.major_filter[int(r[0])].append(r[1])

            self.whitelist = defaultdict(list)
            for r in rows_whitelist:
                self.whitelist[int(r[0])].append(r[1])

    def cog_unload(self):
        """Nicely close the database connections :)"""
        self.conn.close()
        self.config_conn.close()


def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(WordFilter(bot))
