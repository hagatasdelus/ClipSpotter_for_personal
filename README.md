# ClipSpotter For Personal

## Overview
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
Build and launch it yourself using Docker and invite the guilds that want to use this bot.
