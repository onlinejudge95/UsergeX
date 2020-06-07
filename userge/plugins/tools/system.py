# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.
import time
import asyncio
import shutil
import os
import wget
import speedtest

from datetime import datetime
from userge.utils import humanbytes
from pyrogram.errors.exceptions import FileIdInvalid, FileReferenceEmpty
from pyrogram.errors.exceptions.bad_request_400 import BadRequest

from userge import userge, Message, Config, versions

LOG = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)

#LOGO_STICKER_ID, LOGO_STICKER_REF = None, None


@userge.on_cmd("alive", about={'header': "This command is just for fun"})
async def alive(message: Message):
    await message.delete()
    #try:
    #    if LOGO_STICKER_ID:
    #        await sendit(LOGO_STICKER_ID, message)
    #    else:
    #        await refresh_id()
    #         await sendit(LOGO_STICKER_ID, message)
    #except (FileIdInvalid, FileReferenceEmpty, BadRequest):
    #    await refresh_id()
    #    await sendit(LOGO_STICKER_ID, message)
    output = f"""
**UsergeX is Up and Running**

• **Python**   : `v{versions.__python_version__}`
• **Pyrogram** : `v{versions.__pyro_version__}`
• **Userge**   : `{versions.__usergex__}`
"""
    await userge.send_message(message.chat.id, output, disable_web_page_preview=True)


#async def refresh_id():
#    global LOGO_STICKER_ID, LOGO_STICKER_REF
#    sticker = (await userge.get_messages('theUserge', 8)).sticker
#    LOGO_STICKER_ID = sticker.file_id
#    LOGO_STICKER_REF = sticker.file_ref


#async def sendit(fileid, message):
#    await userge.send_sticker(message.chat.id, fileid, file_ref=LOGO_STICKER_REF)

@userge.on_cmd("repo", about={'header': "get repo link and details"})
async def see_repo(message: Message):
    """see repo"""
    output = f"[🔥UsergeX🔥]({Config.UPSTREAM_REPO}) repository"
    await message.edit(output)


@userge.on_cmd(
    "ping", about={'header': "check how long it takes to ping your userbot"}, group=-1)
async def pingme(message: Message):
    start = datetime.now()
    await message.edit('`Pong!`')
    end = datetime.now()
    m_s = (end - start).microseconds / 1000
    await message.edit(f"**Pong!**\n`{m_s} ms`")


@userge.on_cmd('restart', about={
    'header': "Restarts the bot and reload all plugins",
    'flags': {
        '-h': "restart heroku dyno",
        '-t': "clean temp loaded plugins",
        '-d': "clean working folder"},
    'usage': "{tr}restart [flag | flags]",
    'examples': "{tr}restart -t -d"}, del_pre=True)
async def restart_cmd_handler(message: Message):
    await message.edit("Restarting Userge Services", log=__name__)
    LOG.info("USERGE Services - Restart initiated")
    if 't' in message.flags:
        shutil.rmtree(Config.TMP_PATH, ignore_errors=True)
    if 'd' in message.flags:
        shutil.rmtree(Config.DOWN_PATH, ignore_errors=True)
    if Config.HEROKU_APP and 'h' in message.flags:
        await message.edit(
            '`Heroku app found, trying to restart dyno...\nthis will take upto 30 sec`', del_in=3)
        Config.HEROKU_APP.restart()
        time.sleep(30)
    else:
        await message.edit("finalizing...", del_in=1)
        asyncio.get_event_loop().create_task(userge.restart())




@userge.on_cmd("speedtest", about={'header': "test your server speed"})
async def speedtst(message: Message):
    await message.edit("`Running speed test . . .`")
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        await message.try_to_edit("`Performing download test . . .`")
        test.download()
        await message.try_to_edit("`Performing upload test . . .`")
        test.upload()
        test.results.share()
        result = test.results.dict()
    except Exception as e:
        await message.err(text=e)
        return
    path = wget.download(result['share'])
    output = f"""**--Started at {result['timestamp']}--

Client:

ISP: `{result['client']['isp']}`
Country: `{result['client']['country']}`

Server:

Name: `{result['server']['name']}`
Country: `{result['server']['country']}, {result['server']['cc']}`
Sponsor: `{result['server']['sponsor']}`
Latency: `{result['server']['latency']}`

Ping: `{result['ping']}`
Sent: `{humanbytes(result['bytes_sent'])}`
Received: `{humanbytes(result['bytes_received'])}`
Download: `{humanbytes(result['download'] / 8)}/s`
Upload: `{humanbytes(result['upload'] / 8)}/s`**"""
    msg = await userge.send_photo(chat_id=message.chat.id,
                                  photo=path,
                                  caption=output)
    await CHANNEL.fwd_msg(msg)
    os.remove(path)
    await message.delete()

