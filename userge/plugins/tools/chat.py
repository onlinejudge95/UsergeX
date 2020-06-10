# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from userge import userge, Message


@userge.on_cmd("ids", about={
    'header': "display ids",
    'usage': "reply {tr}ids any message, file or just send this command"})
async def getids(message: Message):
    out_str = f"💁 Current Chat ID: `{message.chat.id}`"
    if message.reply_to_message:
        if message.reply_to_message.from_user:
            out_str += f"\n🙋‍♂️ From User ID: `{message.reply_to_message.from_user.id}`"
        file_id = None
        if message.reply_to_message.media:
            if message.reply_to_message.audio:
                file_id = message.reply_to_message.audio.file_id
            elif message.reply_to_message.document:
                file_id = message.reply_to_message.document.file_id
            elif message.reply_to_message.photo:
                file_id = message.reply_to_message.photo.file_id
            elif message.reply_to_message.sticker:
                file_id = message.reply_to_message.sticker.file_id
            elif message.reply_to_message.voice:
                file_id = message.reply_to_message.voice.file_id
            elif message.reply_to_message.video_note:
                file_id = message.reply_to_message.video_note.file_id
            elif message.reply_to_message.video:
                file_id = message.reply_to_message.video.file_id
            if file_id is not None:
                out_str += f"\n📄 File ID: `{file_id}`"
    await message.edit(out_str)


@userge.on_cmd("del", about={'header': "delete replied message"})
async def del_msg(message: Message):
    msg_ids = [message.message_id]
    if message.reply_to_message:
        msg_ids.append(message.reply_to_message.message_id)
    await userge.delete_messages(message.chat.id, msg_ids)


@userge.on_cmd("admins", about={
    'header': "View or mention admins in chat",
    'flags': {
        '-m': "mention all admins",
        '-mc': "only mention creator",
        '-id': "show ids"},
    'usage': "{tr}admins [any flag] [chatid]"})
async def mentionadmins(message: Message):
    mentions = "🛡 **Admin List** 🛡\n"
    chat_id = message.filtered_input_str
    flags = message.flags
    men_admins = '-m' in flags
    men_creator = '-mc' in flags
    show_id = '-id' in flags
    if not chat_id:
        chat_id = message.chat.id
    try:
        async for x in userge.iter_chat_members(chat_id=chat_id, filter="administrators"):
            status = x.status
            u_id = x.user.id
            username = x.user.username or None
            full_name = (await userge.get_user_dict(u_id))['flname']
            if status == "creator":
                if men_admins or men_creator:
                    mentions += f"\n 👑 [{full_name}](tg://user?id={u_id})"
                elif username:
                    mentions += f"\n 👑 [{full_name}](https://t.me/{username})"
                else:
                    mentions += f"\n 👑 {full_name}"
                if show_id:
                    mentions += f" `{u_id}`"
            elif status == "administrator":
                if men_admins:
                    mentions += f"\n ⚜ [{full_name}](tg://user?id={u_id})"
                elif username:
                    mentions += f"\n ⚜ [{full_name}](https://t.me/{username})"
                else:
                    mentions += f"\n ⚜ {full_name}"
                if show_id:
                    mentions += f" `{u_id}`"
    except Exception as e:
        mentions += " " + str(e) + "\n"
    await message.delete()
    await userge.send_message(
        chat_id=message.chat.id, text=mentions,  disable_web_page_preview=True)


@userge.on_cmd("sd (?:(\\d+)?\\s?(.+))", about={
    'header': "make self-destructable messages",
    'usage': "{tr}sd [test]\n{tr}sd [timeout in seconds] [text]"})
async def selfdestruct(message: Message):
    seconds = int(message.matches[0].group(1) or 0)
    text = str(message.matches[0].group(2))
    await message.edit(text=text, del_in=seconds)


@userge.on_cmd("json", about={
    'header': "message object to json",
    'usage': "reply {tr}json to any message"})
async def jsonify(message: Message):
    the_real_message = str(message.reply_to_message) if message.reply_to_message \
        else str(message)
    await message.edit_or_send_as_file(text=the_real_message,
                                       filename="json.txt",
                                       caption="Message debug")
