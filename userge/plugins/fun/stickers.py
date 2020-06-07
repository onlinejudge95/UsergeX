""" kang stickers """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import math
import random
import urllib.request
import asyncio
import textwrap

from PIL import Image, ImageDraw, ImageFont
from pyrogram.api.functions.messages import GetStickerSet
from pyrogram.api.types import InputStickerSetShortName
from pyrogram.errors.exceptions.bad_request_400 import YouBlockedUser

from userge import userge, Message, Config, pool


@userge.on_cmd("kang", about={
    'header': "kangs stickers or creates new ones",
    'usage': "Reply {tr}kang [emoji('s)] [pack number] to a sticker or "
             "an image to kang it to your userbot pack.",
    'examples': ["{tr}kang", "{tr}kang 🤔", "{tr}kang 2", "{tr}kang 🤔 2"]})
async def kang_(message: Message):
    """ kang a sticker """
    user = message.from_user
    if not user.username:
        user.username = user.first_name or user.id
    replied = message.reply_to_message
    photo = None
    emoji = None
    is_anim = False
    resize = False
    if replied and replied.media:
        if replied.photo:
            resize = True
        elif replied.document and "image" in replied.document.mime_type:
            resize = True
        elif replied.document and "tgsticker" in replied.document.mime_type:
            is_anim = True
        elif replied.sticker:
            emoji = replied.sticker.emoji
            is_anim = replied.sticker.is_animated
            if not replied.sticker.file_name.endswith('.tgs'):
                resize = True
        else:
            await message.edit("`Unsupported File!`")
            return
        await message.edit(f"`{random.choice(KANGING_STR)}`")
        photo = await userge.download_media(message=replied,
                                            file_name=Config.DOWN_PATH)
    else:
        await message.edit("`Nginx, can' proccess...`")
        return
    if photo:
        args = message.input_str.split()
        if not emoji:
            emoji = "🤔"
        pack = 1
        if len(args) == 2:
            emoji, pack = args
        elif len(args) == 1:
            if args[0].isnumeric():
                pack = int(args[0])
            else:
                emoji = args[0]
        packname = f"a{user.id}_{user.username}_{pack}"
        packnick = f"{user.first_name} Pt.{pack}"
        cmd = '/newpack'
        if resize:
            photo = resize_photo(photo)
        if is_anim:
            packname = f"a{user.id}_by_{user.username}_anim{pack}"
            packnick = f"{user.first_name} Anim.{pack}"
            cmd = '/newanimated'

        @pool.run_in_thread
        def get_response():
            response = urllib.request.urlopen(
                urllib.request.Request(f'http://t.me/addstickers/{packname}'))
            return response.read().decode("utf8").split('\n')
        htmlstr = await get_response()
        if ("  A <strong>Telegram</strong> user has created "
                "the <strong>Sticker&nbsp;Set</strong>.") not in htmlstr:
            async with userge.conversation('Stickers') as conv:
                try:
                    await conv.send_message('/addsticker')
                except YouBlockedUser:
                    await message.edit('first **unblock** @Stickers')
                    return
                await conv.get_response(mark_read=True)
                await conv.send_message(packname)
                msg = await conv.get_response(mark_read=True)
                limit = "50" if is_anim else "120"
                while limit in msg.text:
                    pack += 1
                    packname = f"a{user.id}_{user.username}_{pack}"
                    packnick = f"{user.first_name} Pt.{pack}"
                    await message.edit("`Creating new branch: " + str(pack))
                    await conv.send_message(packname)
                    msg = await conv.get_response(mark_read=True)
                    if msg.text == "Invalid branch selected.":
                        await conv.send_message(cmd)
                        await conv.get_response(mark_read=True)
                        await conv.send_message(packnick)
                        await conv.get_response(mark_read=True)
                        await conv.send_document(photo)
                        await conv.get_response(mark_read=True)
                        await conv.send_message(emoji)
                        await conv.get_response(mark_read=True)
                        await conv.send_message("/publish")
                        if is_anim:
                            await conv.get_response(mark_read=True)
                            await conv.send_message(f"<{packnick}>")
                        await conv.get_response(mark_read=True)
                        await conv.send_message("/skip")
                        await conv.get_response(mark_read=True)
                        await conv.send_message(packname)
                        await conv.get_response(mark_read=True)
                        await message.edit(
                            f"`Build finished on new branch` !\n"
                            f"**Changelogs:** [here](t.me/addstickers/{packname})")
                        return
                await conv.send_document(photo)
                rsp = await conv.get_response(mark_read=True)
                if "Sorry, the file type is invalid." in rsp.text:
                    await message.edit("`Failed to add sticker, use` @Stickers "
                                       "`bot to add the sticker manually.`")
                    return
                await conv.send_message(emoji)
                await conv.get_response(mark_read=True)
                await conv.send_message('/done')
                await conv.get_response(mark_read=True)
        else:
            await message.edit("`Brewing a new Pack...`")
            async with userge.conversation('Stickers') as conv:
                try:
                    await conv.send_message(cmd)
                except YouBlockedUser:
                    await message.edit('first **unblock** @Stickers')
                    return
                await conv.get_response(mark_read=True)
                await conv.send_message(packnick)
                await conv.get_response(mark_read=True)
                await conv.send_document(photo)
                rsp = await conv.get_response(mark_read=True)
                if "Sorry, the file type is invalid." in rsp.text:
                    await args.edit("`Failed to add sticker, use` @Stickers "
                                    "`bot to add the sticker manually.`")
                    return
                await conv.send_message(emoji)
                await conv.get_response(mark_read=True)
                await conv.send_message("/publish")
                if is_anim:
                    await conv.get_response(mark_read=True)
                    await conv.send_message(f"<{packnick}>")
                await conv.get_response(mark_read=True)
                await conv.send_message("/skip")
                await conv.get_response(mark_read=True)
                await conv.send_message(packname)
                await conv.get_response(mark_read=True)
        await message.edit(f"`Build finished successfully!`\n"
                           f"**Changelogs:** [here](t.me/addstickers/{packname})")
        os.remove(photo)


@userge.on_cmd("stkrinfo", about={
    'header': "get sticker pack info",
    'usage': "reply {tr}stkrinfo to any sticker"})
async def sticker_pack_info_(message: Message):
    """ get sticker pack info """
    replied = message.reply_to_message
    if not replied:
        await message.edit("`I can't fetch info from nothing, can I ?!`")
        return
    if not replied.sticker:
        await message.edit("`Reply to a sticker to get the pack details`")
        return
    await message.edit("`Fetching details of the sticker pack, please wait..`")
    get_stickerset = await userge.send(
        GetStickerSet(
            stickerset=InputStickerSetShortName(
                short_name=replied.sticker.set_name)))
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)
    out_str = f"**Title:** `{get_stickerset.set.title}\n`" \
        f"**Short Name:** `{get_stickerset.set.short_name}`\n" \
        f"**Archived:** `{get_stickerset.set.archived}`\n" \
        f"**Official:** `{get_stickerset.set.official}`\n" \
        f"**Masks:** `{get_stickerset.set.masks}`\n" \
        f"**Animated:** `{get_stickerset.set.animated}`\n" \
        f"**Stickers:** `{get_stickerset.set.count}`\n" \
        f"**Emojis:**\n{' '.join(pack_emojis)}"
    await message.edit(out_str)


def resize_photo(photo: str) -> str:
    """ Resize the given photo to 512x512 """
    image = Image.open(photo)
    maxsize = (512, 512)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        image = image.resize(sizenew)
    else:
        image.thumbnail(maxsize)
    os.remove(photo)
    photo = os.path.join(Config.DOWN_PATH, "sticker.png")
    if os.path.exists(photo):
        os.remove(photo)
    image.save(photo, "PNG")
    return photo


KANGING_STR = (
    "Build starting...",
    "Overclocking..",
    "Underclocking..",
    "Build started under commit: **Merge branch into new pack**",
    "Build started under commit: **Rewrite to improve performance**")



@userge.on_cmd("q", about={
    'header': "Quote a message",
    'usage': "{tr}q [text or reply to msg]"})
async def quotecmd(message: Message):
    """quotecmd"""
    asyncio.get_event_loop().create_task(message.delete())
    args = message.input_str
    replied = message.reply_to_message
    async with userge.conversation('QuotLyBot') as conv:
        try:
            if replied and not args:
                await conv.forward_message(replied)
            else:
                if not args:
                    await message.err('input not found!')
                    return
                await conv.send_message(args)
        except YouBlockedUser:
            await message.edit('first **unblock** @QuotLyBot')
            return
        quote = await conv.get_response(mark_read=True)
        if not quote.sticker:
            await message.err('something went wrong!')
        else:
            message_id = replied.message_id if replied else None
            await userge.send_sticker(chat_id=message.chat.id,
                                      sticker=quote.sticker.file_id,
                                      file_ref=quote.sticker.file_ref,
                                      reply_to_message_id=message_id)


@userge.on_cmd("plet", about={
    'header': "Get a Random RGB Sticker",
    'description': "Generates A RGB Sticker with provided text",
    'usage': "{tr}plet [text | reply]",
    'examples': "{tr}plet Fucek"})
async def sticklet(message: Message):
    R = random.randint(0, 256)
    G = random.randint(0, 256)
    B = random.randint(0, 256)

    sticktext = message.input_or_reply_str
    if not sticktext:
        await message.edit("**Bruh** ~`I need some text to make sticklet`")
        return
    await message.delete()

    if message.reply_to_message:
        reply_to = message.reply_to_message.message_id
    else:
        reply_to = message.message_id

    # https://docs.python.org/3/library/textwrap.html#textwrap.wrap

    sticktext = textwrap.wrap(sticktext, width=10)
    sticktext = '\n'.join(sticktext)

    image = Image.new("RGBA", (512, 512), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    fontsize = 230

    font_file = await get_font_file()
    font = ImageFont.truetype(font_file, size=fontsize)

    while draw.multiline_textsize(sticktext, font=font) > (512, 512):
        fontsize -= 3
        font = ImageFont.truetype(font_file, size=fontsize)

    width, height = draw.multiline_textsize(sticktext, font=font)
    draw.multiline_text(
        ((512 - width) / 2, (512 - height) / 2), sticktext, font=font, fill=(R, G, B))

    image_name = "rgb_sticklet.webp"
    image.save(image_name, "WebP")

    await userge.send_sticker(
        chat_id=message.chat.id, sticker=image_name, reply_to_message_id=reply_to)

    # cleanup
    try:
        os.remove(font_file)
        os.remove(image_name)
    except Exception:
        pass


async def get_font_file():
    font_file_message_s = await userge.get_history("@FontsRes")
    font_file_message = random.choice(font_file_message_s)
    return await userge.download_media(font_file_message)
