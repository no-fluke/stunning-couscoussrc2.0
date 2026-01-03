import time

USER_COOLDOWN = {}
COOLDOWN_SECONDS = 30  # SAFE FOR TELEGRAM

def check_cooldown(user_id: int):
    now = time.time()
    last = USER_COOLDOWN.get(user_id, 0)

    remaining = COOLDOWN_SECONDS - (now - last)
    if remaining > 0:
        return False, int(remaining)

    USER_COOLDOWN[user_id] = now
    return True, 0
