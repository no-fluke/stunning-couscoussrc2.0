import time

def progress_bar(current, total, start, message):
    if total == 0:
        return

    diff = time.time() - start
    if diff < 1:
        return

    percent = current * 100 / total
    filled = int(percent // 5)
    bar = "█" * filled + "░" * (20 - filled)
    speed = (current / diff) / (1024 * 1024)

    try:
        message.edit(
            f"📥 **Downloading...**\n\n"
            f"`{bar}` {percent:.2f}%\n"
            f"⚡ `{speed:.2f} MB/s`"
        )
    except:
        pass
