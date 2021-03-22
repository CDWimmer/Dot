# coding: utf-8
"""
Staff Contact cog for Dot the Discord Bot.
Version 2021.03.22

This cog provides commands to allow regular users to send complaints/ suggestions/ questions to server staff in a
managed way.

One can customise the DM sent to a user when they send a message per-server.

Will default to using the globally set logging channel for informing server staff of messages but this can be
overridden.

Dependencies:
-------------
- Config Manager (configmgr.py) cog

"""
import discord
from discord.ext import commands
from discord import utils
import sqlite3

CONFIG_FILE = "config_db.db"
CONTACT_CONFIG_FILE = "staff_contact_db.db"


class StaffContact(commands.Cog):
    def __init__(self, bot: commands.Bot):
        print("[StaffContact] Cog loading...")
        self.bot = bot
        self.config_conn = None  # global config
        self.conn = None  # cog-specific config
        try:
            self.config_conn = sqlite3.connect(CONFIG_FILE)
        except sqlite3.Error as e:
            raise Exception(f"Connection to global config database failed! {str(e)}")
        else:
            pass  # all's good.

        try:
            self.conn = sqlite3.connect(CONTACT_CONFIG_FILE)
        except sqlite3.Error as e:
            raise Exception(f"Connection to staff contact config database failed! {str(e)}")
        else:
            # connected, make sure tables exist
            try:
                c = self.conn.cursor()
                c.execute("""
                          CREATE TABLE IF NOT EXISTS contact_config (
                          id integer PRIMARY KEY,
                          guild_id text NOT NULL,
                          suggestion_text text NOT NULL,
                          complaint_text NOT NULL,
                          question_text NOT NULL,
                          contact_text NOT NULL,
                          channel_id text NOT NULL)
                          """)
                self.conn.commit()
            except sqlite3.Error as e:
                print("[StaffContact] Error creating database table.")
                raise e

        # set the default contact messages.
        self.default_messages = {
            "suggestion": "Your suggestion was submitted. It will be reviewed by the moderators, but we can't respond "
                          "to everyone directly.",
            "complaint": "Your complaint was submitted. It will be reviewed by the moderators, but we can't respond "
                         "to everyone directly.",
            "question": "Your question was submitted. It will be reviewed by moderators, who will try to answer you "
                        "as soon as they can.",
            "contact": "Your message was submitted.",
        }

        # make sure we've got configs for all the servers we are in
        for guild in self.bot.guilds:
            self.make_config(guild)

    def make_config(self, guild: discord.Guild):
        c = self.conn.cursor()  # check we don't already have an entry hanging around
        rows = c.execute("SELECT * FROM contact_config WHERE guild_id=?", (guild.id,)).fetchall()
        if len(rows) == 0:
            # no entry for given guild. Make it! :)
            c.execute("INSERT INTO contact_config (guild_id,suggestion_text,complaint_text,question_text,contact_text,"
                      "channel_id) VALUES(?,?,?,?,?,?)",
                      (
                          guild.id,
                          self.default_messages["suggestion"],
                          self.default_messages["complaint"],
                          self.default_messages["question"],
                          self.default_messages["contact"],
                          "default"
                      )
                      )
            self.conn.commit()

    async def process_contact_cmd(self, ctx: commands.Context, contact_type: str, user_submission: str, ):
        """contact types are `suggestion`, `complaint`, `question` and `contact`"""
        c = self.conn.cursor()
        try:
            row = c.execute(f"SELECT channel_id,{contact_type}_text from contact_config WHERE guild_id=?",
                            [ctx.guild.id, ]).fetchall()[0]
            user_msg_embed = discord.Embed(title=f"Message sent")
            user_msg_embed.add_field(name="__Your message__", value=utils.escape_markdown(user_submission))
            user_msg_embed.set_footer(text=row[1])
            user_msg_embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
            if row[0] == "default":
                # fish from global config for channel id
                c2 = self.config_conn.cursor()
                c2.execute("SELECT log_channel FROM log_channels WHERE guild_id=?", (ctx.guild.id,))
                channel = ctx.guild.get_channel(int(c2.fetchall()[0][0]))
            else:
                channel = ctx.guild.get_channel(int(row[0]))

        except Exception as e:
            await ctx.send(f"Something has gone wrong, please contact an administrator: {str(e)}")
        else:
            staff_msg_embed = discord.Embed(title=f"{contact_type.upper()} received from {ctx.author.name}")
            staff_msg_embed.add_field(name=f"{contact_type.capitalize()}", value=utils.escape_markdown(user_submission))
            staff_msg_embed.set_footer(text=f"{ctx.author.name}#{ctx.author.discriminator}",
                                       icon_url=ctx.author.avatar_url)
            await channel.send(embed=staff_msg_embed)
            await ctx.author.send(embed=user_msg_embed)
            if not isinstance(ctx.channel, discord.channel.DMChannel):
                # if a server channel then delete invoking message
                await ctx.message.delete()

    @commands.command(help="Sends a suggestion to the server Staff.", aliases=["suggest"])
    @commands.guild_only()
    async def suggestion(self, ctx: commands.Context, *, suggestion):
        await self.process_contact_cmd(ctx, "suggestion", suggestion)

    @commands.command(help="Sends a complaint to the server Staff.", aliases=["complain"])
    @commands.guild_only()
    async def complaint(self, ctx, *, complaint):
        await self.process_contact_cmd(ctx, "complaint", complaint)

    @commands.command(help="Sends a question to the server Staff.", aliases=["ask"])
    @commands.guild_only()
    async def question(self, ctx, *, question):
        await self.process_contact_cmd(ctx, "question", question)

    @commands.command(help="Send a message to the server Staff.", aliases=["message"])
    @commands.guild_only()
    async def contact(self, ctx, *, message):
        await self.process_contact_cmd(ctx, "contact", message)

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(ban_members=True)
    async def staffcontact(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid or unknown sub-command...")

    @staffcontact.group(invoke_without_command=True)
    @commands.guild_only()
    async def config(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid or unknown sub-command...")

    @config.group(invoke_without_command=True, name="setmessage", help="Set the message DM'd to a user when they use "
                                                                       "specific contact commands.")
    async def set_message(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid or unknown sub-command...")

    async def process_set_message(self, ctx: commands.Context, contact_type: str, new_message: str):
        c = self.conn.cursor()
        try:
            c.execute(f"UPDATE contact_config SET {contact_type}_text=? WHERE guild_id=?", [new_message, ctx.guild.id])
        except Exception as e:
            await ctx.send(f"Something went wrong, please report this to the bot owner: {str(e)}")
        else:
            await ctx.send(f"Updated {contact_type} DM message. ")
            self.conn.commit()

    @set_message.command(name="suggestion", help="Set the message that is sent to users when they submit a suggestion.")
    async def set_suggestion(self, ctx: commands.Context, *, message):
        await self.process_set_message(ctx, "suggestion", message)

    @set_message.command(name="complaint", help="Set the message that is sent to users when they submit a complaint.")
    async def set_complaint(self, ctx: commands.Context, *, message):
        await self.process_set_message(ctx, "complaint", message)

    @set_message.command(name="question", help="Set the message that is sent to users when they submit a question.")
    async def set_question(self, ctx: commands.Context, *, message):
        await self.process_set_message(ctx, "question", message)

    @set_message.command(name="contact", help="Set the message that is sent to users when they submit a contact.")
    async def set_contact(self, ctx: commands.Context, *, message):
        await self.process_set_message(ctx, "contact", message)

    @config.group(invoke_without_command=True, name="resetmessage", help="Reset the message sent to users when they use"
                                                                         " specific contact commands to their default.")
    async def reset_message(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid or unknown sub-command...")

    async def process_reset_message(self, ctx: commands.Context, contact_type: str):
        c = self.conn.cursor()
        try:
            c.execute(f"UPDATE contact_config SET {contact_type}_text=? WHERE guild_id=?",
                      [self.default_messages[contact_type], ctx.guild.id, ])
        except Exception as e:
            await ctx.send(f"Something went wrong, please report this to the bot owner: {str(e)}")
        else:
            await ctx.send(f"Updated {contact_type} DM message. ")
            self.conn.commit()

    @reset_message.command(name="suggestion", help="Reset the message that is sent to users when they submit a "
                                                   "suggestion to default.")
    async def reset_suggestion(self, ctx: commands.Context):
        await self.process_reset_message(ctx, "suggestion")

    @reset_message.command(name="complaint", help="Reset the message that is sent to users when they submit a "
                                                  "complaint to default.")
    async def reset_complaint(self, ctx: commands.Context):
        await self.process_reset_message(ctx, "complaint")

    @reset_message.command(name="question", help="Reset the message that is sent to users when they submit a "
                                                 "question to default.")
    async def reset_question(self, ctx: commands.Context):
        await self.process_reset_message(ctx, "question")

    @reset_message.command(name="contact", help="Reset the message that is sent to users when they submit a "
                                                "contact to default.")
    async def reset_contact(self, ctx: commands.Context):
        await self.process_reset_message(ctx, "contact")

    @config.command(help="Set the channel to which contacts are logged. Leave blank to reset to the default/global log "
                         "channel for this server. ")
    @commands.has_permissions(ban_members=True)
    async def logchannel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        try:
            c = self.conn.cursor()
            if channel is None:
                c.execute("UPDATE contact_config SET channel_id=? WHERE guild_id=?", ["default", ctx.guild.id])
                await ctx.send(f"Set the staff contacts log channel to server's default log channel.")
            else:
                c.execute("UPDATE contact_config SET channel_id=? WHERE guild_id=?", [channel.id, ctx.guild.id])
                await ctx.send(f"Set the staff contacts log channel to {channel.mention}.")
        except Exception as e:
            await ctx.send(f"Something went wrong, please report this to the bot owner: {str(e)}")

# ===================== Events ========================== #

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Create an entry in the contact_config table with default settings when the bot joins a server. """
        self.make_config(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """Remove old entries from the contact_config when leaving a server."""
        c = self.conn.cursor()
        try:
            c.execute("DELETE FROM contact_config WHERE guild_id=?", (guild.id,))
            self.conn.commit()
        except sqlite3.Error:
            print(f"[StaffContact] Left a guild but failed to remove it from the contact config database. guild id: "
                  f"{guild.id}")

# ====================== DB management ===================== #
    def cog_unload(self):
        """Nicely close the database connections when this cog is unloaded :)"""
        self.conn.close()
        self.config_conn.close()
        return

# ====================== Error Handling ==================== #

    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("This command can only be used in a server. ")


def setup(bot: commands.Bot):
    bot.add_cog(StaffContact(bot))
