#(©)Codeflix_Bots

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id
from database.database import db_save_link

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(text = "𝐅𝐨𝐫𝐰𝐚𝐫𝐝 𝐭𝐡𝐞 𝐅𝐢𝐫𝐬𝐭 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐟𝐫𝐨𝐦 𝐃𝐚𝐭𝐚𝐛𝐚𝐬𝐞 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 (with Quotes)..\n\n𝐨𝐫 𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐃𝐚𝐭𝐚𝐛𝐚𝐬𝐞 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐏𝐨𝐬𝐭 𝐥𝐢𝐧𝐤", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error\n\n𝐈𝐭𝐬 𝐧𝐨𝐭 𝐅𝐫𝐨𝐦 𝐃𝐚𝐭𝐚𝐛𝐚𝐬𝐞 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐃𝐮𝐝𝐞 𝐂𝐡𝐞𝐜𝐤 𝐀𝐠𝐚𝐢𝐧..!", quote = True)
            continue

    while True:
        try:
            second_message = await client.ask(text = "𝐅𝐨𝐫𝐰𝐚𝐫𝐝 𝐭𝐡𝐞 𝐋𝐚𝐬𝐭 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐟𝐫𝐨𝐦 𝐃𝐚𝐭𝐚𝐛𝐚𝐬𝐞 𝐂𝐡𝐚𝐧𝐧𝐞𝐥..! (with Quotes)..\n𝐨𝐫 𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐃𝐚𝐭𝐚𝐛𝐚𝐬𝐞 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐏𝐨𝐬𝐭 𝐥𝐢𝐧𝐤", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("❌ Error\n\n𝐈𝐭𝐬 𝐧𝐨𝐭 𝐅𝐫𝐨𝐦 𝐃𝐚𝐭𝐚𝐛𝐚𝐬𝐞 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐃𝐮𝐝𝐞 𝐂𝐡𝐞𝐜𝐤 𝐀𝐠𝐚𝐢𝐧..!", quote = True)
            continue

    try:
        image_choice = await client.ask(
            text="Do you want a custom verification image for this batch?\n\nReply: YES or NO",
            chat_id=message.from_user.id,
            filters=filters.text,
            timeout=60
        )
        batch_image = ""
        if image_choice.text.upper() in ["YES", "Y"]:
            try:
                image_msg = await client.ask(
                    text="Send the verification image URL:",
                    chat_id=message.from_user.id,
                    filters=filters.text,
                    timeout=60
                )
                batch_image = image_msg.text.strip()
            except:
                batch_image = ""
    except:
        batch_image = ""

    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://telegram.me/{client.username}?start={base64_string}"
    
    if batch_image:
        file_id = f"batch-{f_msg_id}-{s_msg_id}"
        await db_save_link(file_id, batch_image=batch_image)
    
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await second_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=reply_markup)


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(text = "𝐅𝐨𝐫𝐰𝐚𝐫𝐝 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐟𝐫𝐨𝐦 𝐃𝐚𝐭𝐚𝐛𝐚𝐬𝐞 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 (with Quotes)..\n\n𝐨𝐫 𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐃𝐚𝐭𝐚𝐛𝐚𝐬𝐞 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐏𝐨𝐬𝐭 𝐥𝐢𝐧𝐤", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error\n\n𝐈𝐭𝐬 𝐧𝐨𝐭 𝐅𝐫𝐨𝐦 𝐃𝐚𝐭𝐚𝐛𝐚𝐬𝐞 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐃𝐮𝐝𝐞 𝐂𝐡𝐞𝐜𝐤 𝐀𝐠𝐚𝐢𝐧..!", quote = True)
            continue

    custom_image = ""
    try:
        image_msg = await client.ask(
            text="Send a custom verification image URL (or type 'skip' to use default):",
            chat_id=message.from_user.id,
            filters=filters.text,
            timeout=60
        )
        if image_msg.text.lower() != "skip":
            custom_image = image_msg.text.strip()
    except:
        custom_image = ""

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://telegram.me/{client.username}?start={base64_string}"
    
    if custom_image:
        await db_save_link(f"get-{msg_id}", image=custom_image)
    
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await channel_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=reply_markup)
