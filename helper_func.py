#(©)Codexbotz
#Recoded By @Codeflix_Bots

import base64
import re
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from config import FORCESUB_CHANNEL, FORCESUB_CHANNEL2, FORCESUB_CHANNEL3, ADMINS, VERIFY_IMAGE
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait
from shortzy import Shortzy
from datetime import datetime
from database.database import user_data, db_verify_status, db_update_verify_status, db_get_link

async def is_subscribed(filter, client, update):
    if not (FORCESUB_CHANNEL or FORCESUB_CHANNEL2 or FORCESUB_CHANNEL3):
        return True

    user_id = update.from_user.id

    if user_id in ADMINS:
        return True

    member_status = ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER

    for channel_id in [FORCESUB_CHANNEL, FORCESUB_CHANNEL2, FORCESUB_CHANNEL3]:
        if not channel_id:
            continue

        try:
            member = await client.get_chat_member(chat_id=channel_id, user_id=user_id)
        except UserNotParticipant:
            return False

        if member.status not in member_status:
            return False

    return True

async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = base64_bytes.decode("ascii").rstrip("=")
    return base64_string

async def decode(base64_string):
    base64_string = base64_string.rstrip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    string = string_bytes.decode("ascii")
    return string

async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages:total_messages+200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except:
            pass
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages

async def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        else:
            return 0
    elif message.forward_sender_name:
        return 0
    elif message.text:
        pattern = "https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern, message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        else:
            if channel_id == client.db_channel.username:
                return msg_id
    else:
        return 0

async def get_verify_status(user_id):
    verify = await db_verify_status(user_id)
    return verify

async def update_verify_status(user_id, verify_token="", is_verified=False, verified_time=0, link="", 
                              current_step=None, verify1_expiry=None, verify2_expiry=None, gap_expiry=None,
                              last_entry_link="", verification_message_id=0):
    current = await db_verify_status(user_id)
    current['verify_token'] = verify_token
    current['is_verified'] = is_verified
    current['verified_time'] = verified_time
    current['link'] = link
    
    # Update new fields if provided (backward compatible)
    if current_step is not None:
        current['current_step'] = current_step
    if verify1_expiry is not None:
        current['verify1_expiry'] = verify1_expiry
    if verify2_expiry is not None:
        current['verify2_expiry'] = verify2_expiry
    if gap_expiry is not None:
        current['gap_expiry'] = gap_expiry
    if last_entry_link:
        current['last_entry_link'] = last_entry_link
    if verification_message_id:
        current['verification_message_id'] = verification_message_id
    
    await db_update_verify_status(user_id, current)

async def get_shortlink(url, api, link):
    try:
        if not url or not api:
            # If shortlink config is missing, return the original link
            return link
        
        shortzy = Shortzy(api_key=api, base_site=url)
        short_link = await shortzy.convert(link)
        
        if short_link and isinstance(short_link, str) and len(short_link) > 0:
            return short_link
        else:
            # If shortlink conversion failed, return original link as fallback
            return link
    except Exception as e:
        print(f"[v0] Shortlink generation failed: {e}")
        return link

async def get_verify_image(file_id: str = "") -> str:
    """Get verification image - uses custom image if available, otherwise uses default VERIFY_IMAGE"""
    print(f"[DEBUG] get_verify_image called with file_id: {file_id}")
    if file_id:
        try:
            link = await db_get_link(file_id)
            print(f"[DEBUG] Database link data: {link}")
            if link:
                # Check for batch image first (for batch links)
                if file_id.startswith('batch-') and link.get('batch_image'):
                    print(f"[DEBUG] Found batch_image: {link.get('batch_image')}")
                    return link['batch_image']
                # Check for regular image (for single file links)
                elif link.get('image'):
                    print(f"[DEBUG] Found image: {link.get('image')}")
                    return link['image']
            print(f"[DEBUG] No custom image found in database")
        except Exception as e:
            print(f"[DEBUG] Error fetching verify image: {e}")
    print(f"[DEBUG] Returning default VERIFY_IMAGE: {VERIFY_IMAGE}")
    return VERIFY_IMAGE

def get_exp_time(seconds):
    periods = [('days', 86400), ('hours', 3600), ('mins', 60), ('secs', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name}'
    return result

def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time

async def delete_old_verification_message(client, user_id):
    """Delete previous verification message if it exists"""
    try:
        verify_status = await get_verify_status(user_id)
        old_msg_id = verify_status.get('verification_message_id', 0)
        
        if old_msg_id > 0:
            try:
                await client.delete_messages(chat_id=user_id, message_ids=old_msg_id)
                print(f"[DEBUG] Deleted old verification message {old_msg_id} for user {user_id}")
            except Exception as e:
                print(f"[DEBUG] Could not delete verification message: {e}")
    except Exception as e:
        print(f"[DEBUG] Error in delete_old_verification_message: {e}")

subscribed = filters.create(is_subscribed)
