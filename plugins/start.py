from bot import Bot
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import VERIFY_IMAGE, SHORTENER_API_KEY
from helper_func import is_subscribed, encode, decode, get_verify_image, delete_old_verification_message
from database.database import present_user, add_user, db_verify_status, db_update_verify_status, db_get_link
from shortzy import Shortzy
import asyncio

async def send_verification_message(message, caption_text, verify_image, reply_markup):
    """Send verification message with or without image and return the sent message"""
    if verify_image and isinstance(verify_image, str) and verify_image.strip():
        try:
            print(f"[DEBUG] Attempting to send image: {verify_image}")
            sent_msg = await message.reply_photo(
                photo=verify_image,
                caption=caption_text,
                reply_markup=reply_markup,
                quote=True
            )
            print(f"[DEBUG] Image sent successfully!")
            return sent_msg
        except Exception as e:
            print(f"[DEBUG] Failed to send image: {e}")
            sent_msg = await message.reply(caption_text, reply_markup=reply_markup, quote=True)
            return sent_msg
    else:
        print(f"[DEBUG] No valid image provided, sending text only. Image value: {verify_image}")
        sent_msg = await message.reply(caption_text, reply_markup=reply_markup, quote=True)
        return sent_msg

@Bot.on_message(filters.command("start") & filters.private)
async def start(bot: Bot, message: Message):
    user_id = message.from_user.id
    
    full_start_link = f"https://telegram.me/{bot.username}?start={message.command[1]}" if len(message.command) > 1 else f"https://telegram.me/{bot.username}?start="
    
    if not await present_user(user_id):
        await add_user(user_id)
    
    verify_status = await db_verify_status(user_id)
    
    await delete_old_verification_message(bot, user_id, verify_status)
    
    verify_status['last_entry_link'] = full_start_link
    await db_update_verify_status(user_id, verify_status)
    
    # Check if user has a payload
    if len(message.command) > 1:
        payload = message.command[1]
        
        # Decode and process the payload
        try:
            decoded_payload = await decode(payload)
            print(f"[DEBUG] Decoded payload: {decoded_payload}")
            
            # Parse payload type
            if decoded_payload.startswith("verify_"):
                # Token verification
                token = decoded_payload.replace("verify_", "")
                if token == verify_status.get('verify_token', ''):
                    verify_status['is_verified'] = True
                    verify_status['current_step'] = 2
                    verify_status['verify_token'] = ""
                    await db_update_verify_status(user_id, verify_status)
                    
                    reply_markup = InlineKeyboardMarkup([[
                        InlineKeyboardButton("✓ Done", url=verify_status['last_entry_link'])
                    ]])
                    
                    await message.reply_text(
                        "✅ Verification completed!\n\nClick 'Done' to access your files.",
                        reply_markup=reply_markup
                    )
                else:
                    await message.reply_text("❌ Invalid verification token!")
            else:
                # File/batch link payload
                await process_file_payload(bot, message, decoded_payload)
                
        except Exception as e:
            print(f"[DEBUG] Error decoding payload: {e}")
            await message.reply_text("Please use the link shared with you.")
    else:
        # No payload - send welcome message
        await message.reply_text(
            "👋 Welcome to RG Files Bot!\n\n"
            "Send or forward files to generate shareable links."
        )

async def process_file_payload(bot: Bot, message: Message, payload: str):
    """Process file/batch link payloads"""
    user_id = message.from_user.id
    verify_status = await db_verify_status(user_id)
    
    parts = payload.split("-")
    
    if parts[0] == "get" and len(parts) == 2:
        # Single file link
        file_id = f"get-{parts[1]}"
        link_data = await db_get_link(file_id)
        verify_image = await get_verify_image(file_id)
        
        # Create verification link
        token = f"verify_{user_id}_{datetime.now().timestamp()}"
        verify_status['verify_token'] = token
        await db_update_verify_status(user_id, verify_status)
        
        # Create shortener link for verification
        shortener = Shortzy(api_key=SHORTENER_API_KEY, url=f"https://telegram.me/{bot.username}?start={await encode(token)}")
        verify_link = shortener.shorten()
        
        caption = f"🔒 Verification Required\n\nClick below to verify and access the file:\n{verify_link}"
        
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("✓ Done", url=verify_status['last_entry_link'])
        ]])
        
        sent_msg = await send_verification_message(message, caption, verify_image, reply_markup)
        verify_status['verification_message_id'] = sent_msg.id
        await db_update_verify_status(user_id, verify_status)
        
    elif parts[0] == "batch" and len(parts) == 3:
        # Batch file link
        file_id = f"batch-{parts[1]}-{parts[2]}"
        verify_image = await get_verify_image(file_id)
        
        token = f"verify_{user_id}_{datetime.now().timestamp()}"
        verify_status['verify_token'] = token
        await db_update_verify_status(user_id, verify_status)
        
        shortener = Shortzy(api_key=SHORTENER_API_KEY, url=f"https://telegram.me/{bot.username}?start={await encode(token)}")
        verify_link = shortener.shorten()
        
        caption = f"🔒 Batch Verification Required\n\nClick below to verify:\n{verify_link}"
        
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("✓ Done", url=verify_status['last_entry_link'])
        ]])
        
        sent_msg = await send_verification_message(message, caption, verify_image, reply_markup)
        verify_status['verification_message_id'] = sent_msg.id
        await db_update_verify_status(user_id, verify_status)
