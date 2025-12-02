import motor.motor_asyncio
from config import DB_URI, DB_NAME

dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database['users']
link_data = database['links']

default_verify = {
    'is_verified': False,           # user currently allowed to access files?
    'verified_time': 0,             # last time any verification was completed
    'verify_token': "",             # token currently expected from user
    'link': "",                     # optional link
    'current_step': 0,              # 0 = never verified, 1 = after first verify, 2 = after second verify
    'verify1_expiry': 0,            # timestamp when first verification expires
    'verify2_expiry': 0,            # timestamp when second verification expires
    'gap_expiry': 0                 # timestamp until which user is in gap between 1 and 2
}

default_link = {
    'file_id': "",                  # unique file identifier
    'image': "",                    # custom verification image for this file (empty = use VERIFY_IMAGE)
    'batch_image': "",              # image for batch links (empty = use VERIFY_IMAGE)
    'created_at': 0
}

def new_user(id):
    return {
        '_id': id,
        'verify_status': {
            'is_verified': False,
            'verified_time': 0,
            'verify_token': "",
            'link': "",
            'current_step': 0,
            'verify1_expiry': 0,
            'verify2_expiry': 0,
            'gap_expiry': 0
        }
    }

async def present_user(user_id: int):
    found = await user_data.find_one({'_id': user_id})
    return bool(found)

async def add_user(user_id: int):
    user = new_user(user_id)
    await user_data.insert_one(user)
    return

async def db_verify_status(user_id):
    user = await user_data.find_one({'_id': user_id})
    if user:
        verify = user.get('verify_status', default_verify)
        for key in default_verify.keys():
            if key not in verify:
                verify[key] = default_verify[key]
        return verify
    return default_verify

async def db_update_verify_status(user_id, verify):
    await user_data.update_one({'_id': user_id}, {'$set': {'verify_status': verify}})

async def db_get_link(file_id: str):
    link = await link_data.find_one({'file_id': file_id})
    if link:
        return link
    return default_link.copy()

async def db_save_link(file_id: str, image: str = "", batch_image: str = ""):
    existing = await link_data.find_one({'file_id': file_id})
    update_data = {}
    if image:
        update_data['image'] = image
    if batch_image:
        update_data['batch_image'] = batch_image
    
    if update_data:
        if existing:
            await link_data.update_one({'file_id': file_id}, {'$set': update_data})
        else:
            update_data['file_id'] = file_id
            update_data['created_at'] = 0
            await link_data.insert_one(update_data)

async def full_userbase():
    user_docs = user_data.find()
    user_ids = [doc['_id'] async for doc in user_docs]
    return user_ids

async def del_user(user_id: int):
    await user_data.delete_one({'_id': user_id})
    return
