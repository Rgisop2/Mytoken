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
            # If image fails, send text only
            print(f"[DEBUG] Failed to send image: {e}")
            sent_msg = await message.reply(caption_text, reply_markup=reply_markup, quote=True)
            return sent_msg
    else:
        print(f"[DEBUG] No valid image provided, sending text only. Image value: {verify_image}")
        sent_msg = await message.reply(caption_text, reply_markup=reply_markup, quote=True)
        return sent_msg
