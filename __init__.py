from datetime import datetime
import os
import traceback

from .server import AbletonCopilotServer


LOG_FILE_PATH = os.path.expanduser('~/Desktop/copilot_live.log')

def log_to_custom_file(msg: str, log_file_path: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log_line = f"[{timestamp}] {msg}\n"
    try:
        with open(log_file_path, 'a') as f:
            f.write(log_line)
    except Exception as e:
        print(f"Error writing to log file: {e}")


def create_instance(c_instance):
    """
    This function is called by Ableton Live when the script is loaded.
    It must return an instance of your main script class.
    """
    log_to_custom_file("AbletonCopilotServer initializing...", LOG_FILE_PATH)
    try:
        return AbletonCopilotServer(c_instance, LOG_FILE_PATH)
    except Exception as e:
        error_info = {
            'error_type': type(e).__name__,
            'error_msg': str(e),
            'stack_trace': traceback.format_exc()
        }
        log_to_custom_file(f"Failed to initialize AbletonCopilotServer:\n"
            f"Error Type: {error_info['error_type']}\n"
            f"Error Message: {error_info['error_msg']}\n"
            f"Stack Trace:\n{error_info['stack_trace']}\n", LOG_FILE_PATH)
