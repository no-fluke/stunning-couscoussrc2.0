USER_BATCH = {}

def start_batch(user_id):
    USER_BATCH[user_id] = []

def add_to_batch(user_id, message):
    USER_BATCH.setdefault(user_id, []).append(message)

def get_batch(user_id):
    return USER_BATCH.get(user_id, [])

def clear_batch(user_id):
    USER_BATCH.pop(user_id, None)
