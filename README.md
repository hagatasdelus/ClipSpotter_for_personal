# ClipSpotter For Personal

## Overview
Discord Bot showing clips of a particular streamer or game on Twitch.<br>
ClipSpotter for personal hosting and use.

## Usage
Create a .env in the root directory of the project and describe it with reference to the following.
```plaintext:.env
DISCORD_ACCESS_TOKEN=
TWITCH_CLIENT_ID=
TWITCH_CLIENT_SECRET=

DATABASE_NAME=clipspotter-data.sqlite
DATABASE_URL=sqlite+aiosqlite:///./${DATABASE_NAME}
```
Build and launch it yourself using Docker and invite the guilds that want to use this bot.<br>

If you want to make the data persistent, touch the file clipspotter-data.sqlite on the host and add the following to the volumes element in compose.yaml
```
- . /${DATABASE_NAME}:/app/${DATABASE_NAME}
```
