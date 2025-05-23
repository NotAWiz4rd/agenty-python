import os
import pickle
import queue
import sys
import threading

from agent.util import log_error

# Global conversation context
_CONVERSATION_CONTEXT = None

# Message queue for API requests
_MESSAGE_QUEUE = queue.Queue()
_QUEUE_LOCK = threading.Lock()


def get_conversation_context():
    """Function to access the global conversation context"""
    global _CONVERSATION_CONTEXT
    return _CONVERSATION_CONTEXT


def set_conversation_context(context):
    """Function to set the global conversation context"""
    global _CONVERSATION_CONTEXT
    _CONVERSATION_CONTEXT = context


def add_to_message_queue(message):
    """Adds a message to the processing queue"""
    _MESSAGE_QUEUE.put(message)
    return True


def get_from_message_queue(block=False, timeout=None) -> tuple:
    """Gets a message from the queue if available"""
    try:
        message_data = _MESSAGE_QUEUE.get(block=block, timeout=timeout)
        return message_data, True
    except queue.Empty:
        return None, False


def has_pending_messages():
    """Checks if messages are available in the queue"""
    return not _MESSAGE_QUEUE.empty()


def cleanup_context():
    """Delete the conversation context file"""
    # Skip cleanup if we're restarting the program intentionally
    # or if we're exiting due to an error
    if getattr(sys, "is_restarting", False) or getattr(sys, "is_error_exit", False):
        if getattr(sys, "is_error_exit", False):
            print("Context preserved due to error exit.")
        return

    context_file = "conversation_context.pkl"
    if os.path.exists(context_file):
        try:
            os.remove(context_file)
            print(f"\nContext file '{context_file}' deleted.")
        except Exception as e:
            print(f"\nError deleting context file: {str(e)}")
            log_error(f"Error deleting context file: {str(e)}")


def load_conversation(save_file="conversation_context.pkl"):
    """Load conversation context from a file if it exists"""
    if os.path.exists(save_file):
        try:
            with open(save_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading conversation: {str(e)}")
    return None
