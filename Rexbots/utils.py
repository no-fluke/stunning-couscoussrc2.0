# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official

import os
import time
import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional
import re
from datetime import datetime
import pickle

logger = logging.getLogger(__name__)

# Cooldown storage
download_cooldowns: Dict[int, float] = {}
batch_cooldowns: Dict[int, float] = {}
COOLDOWN_FILE = "cooldowns.pkl"

def save_cooldowns():
    """Save cooldowns to file"""
    try:
        with open(COOLDOWN_FILE, 'wb') as f:
            pickle.dump({"download": download_cooldowns, "batch": batch_cooldowns}, f)
    except Exception as e:
        logger.error(f"Error saving cooldowns: {e}")

def load_cooldowns():
    """Load cooldowns from file"""
    global download_cooldowns, batch_cooldowns
    try:
        if os.path.exists(COOLDOWN_FILE):
            with open(COOLDOWN_FILE, 'rb') as f:
                data = pickle.load(f)
                download_cooldowns = data.get("download", {})
                batch_cooldowns = data.get("batch", {})
    except Exception as e:
        logger.error(f"Error loading cooldowns: {e}")

def create_download_directory(user_id: int, message_id: Optional[int] = None) -> Path:
    """Create download directory for user if it doesn't exist"""
    try:
        from config import DOWNLOAD_PATH
        
        # Create main user directory
        user_dir = Path(DOWNLOAD_PATH) / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(str(user_dir), 0o755)
        
        if message_id:
            # Also create temporary directory for batch
            temp_dir = Path("downloads") / str(message_id)
            temp_dir.mkdir(parents=True, exist_ok=True)
            os.chmod(str(temp_dir), 0o755)
            logger.info(f"Created directories: {user_dir}, {temp_dir}")
            return temp_dir
        else:
            logger.info(f"Created user directory: {user_dir}")
            return user_dir
    except Exception as e:
        logger.error(f"Failed to create directory for user {user_id}: {e}")
        raise

def safe_filename(filename: str) -> str:
    """Sanitize filename to remove invalid characters"""
    if not filename:
        return f"file_{int(time.time())}.bin"
    
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    
    # Remove any non-printable characters
    filename = ''.join(char for char in filename if char.isprintable())
    
    # Limit length to avoid path issues
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200 - len(ext)] + ext
    
    return filename.strip()

def is_on_cooldown(user_id: int, cooldown_type: str = "download") -> Optional[float]:
    """Check if user is on cooldown, returns seconds remaining or None"""
    from config import COOLDOWN_SECONDS
    
    cooldown_dict = download_cooldowns if cooldown_type == "download" else batch_cooldowns
    
    if user_id in cooldown_dict:
        elapsed = time.time() - cooldown_dict[user_id]
        if elapsed < COOLDOWN_SECONDS:
            return COOLDOWN_SECONDS - elapsed
    return None

def set_cooldown(user_id: int, cooldown_type: str = "download"):
    """Set cooldown for user"""
    cooldown_dict = download_cooldowns if cooldown_type == "download" else batch_cooldowns
    cooldown_dict[user_id] = time.time()
    save_cooldowns()

def remove_cooldown(user_id: int, cooldown_type: str = "download"):
    """Remove cooldown for user"""
    cooldown_dict = download_cooldowns if cooldown_type == "download" else batch_cooldowns
    if user_id in cooldown_dict:
        del cooldown_dict[user_id]
        save_cooldowns()

async def cleanup_temp_directory(temp_dir: str, max_age_hours: int = 1):
    """Clean up old temporary files and directories"""
    try:
        if not os.path.exists(temp_dir):
            return
        
        current_time = time.time()
        # Check if directory is older than max_age_hours
        if current_time - os.path.getmtime(temp_dir) > max_age_hours * 3600:
            try:
                import shutil
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up old temp directory: {temp_dir}")
            except Exception as e:
                logger.error(f"Failed to clean up {temp_dir}: {e}")
    except Exception as e:
        logger.error(f"Error in temp cleanup: {e}")

def get_file_size(path: str) -> str:
    """Convert file size to human readable format"""
    try:
        size = os.path.getsize(path)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    except:
        return "0 B"

def check_file_size(file_size: int) -> bool:
    """Check if file size is within limits"""
    from config import MAX_DOWNLOAD_SIZE
    return file_size <= MAX_DOWNLOAD_SIZE

# Load cooldowns on startup
load_cooldowns()

# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official
