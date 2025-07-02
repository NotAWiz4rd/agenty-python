import os
import pickle
import queue
import sys

from util import log_error

# Global conversation context
conversation_context = None

# Message queue for messages that the agent needs to process
message_queue = queue.Queue()


def get_conversation_context():
    """Function to access the global conversation context"""
    global conversation_context
    return conversation_context


def set_conversation_context(context):
    """Function to set the global conversation context"""
    global conversation_context
    conversation_context = context


def add_to_message_queue(message):
    """Adds a message to the processing queue"""
    message_queue.put(message)
    return True


def get_all_from_message_queue() -> list[str]:
    """Gets all messages from the queue if available"""
    message_data = []
    while not message_queue.empty():
        message_data.append(message_queue.get())
    return message_data


def has_pending_messages():
    """Checks if messages are available in the queue"""
    return not message_queue.empty()


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
