from datetime import datetime

def log_message(level, message):
    """Standardized logging format with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")