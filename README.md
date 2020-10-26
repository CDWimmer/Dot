![Auntie Dot logo](https://www.myfconline.com/character_avatars/237686_79407.jpg)

# Dot the Discord Bot

An in-progress, modular, administrative and general-purpose Discord bot using [discord.py](https://github.com/Rapptz/discord.py). 

Please note this is far from a finished project and at this moment is not usable. If you're so inclined, most of the cogs available [here](/cogs) *do* work independantly, so you could add them to your own bot if you know what you're doing!  

## Info for bot users:
This isn't a thing on its own yet so nothing to report :)

## Important info for people hosting their own bot:
`cogs/info.py` requires you to enable **intents** for Presences and Members in your Discord Developer Portal.

`cogs/configmgr.py` is considered a required cog given it creates and allows for the management of config/settings data that is available to all other cogs e.g. the setting of a per-server log channel that other cogs can read from. Not to say that *all* cogs will depend on it, inter-cog dependancies will be described in their docstrings at the top of each file. 

The bot must be able to write files to disk in order to save its database files. This likely won't be a problem on Windows but make sure it has write permissions for its directory on Linux. If you're not sure, run it and see if it crashes. :D

Soon the global `config.py` will be replaced entirely with a Config Manager cog (`configmgr.py`) that allows for per-server configuration so don't worry about that weird thing. 
