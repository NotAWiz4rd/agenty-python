# command_line_tool.py

import json
import subprocess
import shlex
import os
import threading
import time
import atexit
import signal
from contextlib import contextmanager
from agent.tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Global process storage for persistent processes
# ------------------------------------------------------------------
active_processes = {}
process_counter = 0
AUTO_CLEANUP_ENABLED = True
CLEANUP_THREAD = None
CLEANUP_INTERVAL = 60  # seconds

# ------------------------------------------------------------------
# Blacklist of blocked commands
# ------------------------------------------------------------------
BLOCKED_COMMANDS = {
    "rm", "shutdown", "reboot", "halt", "poweroff", "mkfs", "dd", "init", "telinit", "kill", "killall", "passwd", "whoami"
}

# ------------------------------------------------------------------
# Input schema for the command_line_tool
# ------------------------------------------------------------------
CommandLineInputSchema = {
    "type": "object",
    "properties": {
        "command": {
            "type": "string",
            "description": "The shell command to execute (e.g., 'ls', 'echo', 'cat', etc.)"
        },
        "args": {
            "type": "string",
            "description": "Additional arguments for the command"
        },
        "keep_alive": {
            "type": "boolean",
            "description": "If true, keeps the process running and returns a process ID for later interaction"
        },
        "process_action": {
            "type": "string",
            "description": "Action to perform on a process: 'list', 'kill', 'status', 'output', 'input', 'cleanup', 'cleanup_all', 'cleanup_status', 'cleanup_restart'"
        },
        "process_id": {
            "type": "integer",
            "description": "Process ID for process_action operations"
        },
        "input_text": {
            "type": "string",
            "description": "Text to send to a running process's stdin"
        }
    },
    "required": []
}

def command_line_tool(input_data: dict) -> str:
    """
    Command line tool that supports:
    - Regular command execution (wait for completion)
    - Persistent processes (keep_alive=True)
    - Process management (list, kill, status, output)
    - Interactive input to running processes
    """
    global active_processes, process_counter

    # Ensure auto-cleanup is running
    ensure_auto_cleanup_running()

    # Debug: write to a file instead of stdout so we can see it
    with open('/tmp/debug_command_tool.log', 'a') as f:
        f.write(f"command_line_tool called with: {input_data}\n")
        f.write(f"Type of input_data: {type(input_data)}\n")

    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    # Handle process management actions or input to existing process
    process_action = input_data.get("process_action")
    process_id = input_data.get("process_id")
    input_text = input_data.get("input_text")
    
    with open('/tmp/debug_command_tool.log', 'a') as f:
        f.write(f"Extracted: process_action='{process_action}', process_id={process_id}, input_text='{input_text}'\n")
    
    # If we have input_text and process_id but no explicit action, assume "input"
    if input_text and process_id and not process_action:
        input_data["process_action"] = "input"
        return handle_process_action(input_data)
    elif process_action:
        return handle_process_action(input_data)

    command = input_data.get("command", "")
    args = input_data.get("args", "")
    keep_alive = input_data.get("keep_alive", False)

    # If no command provided and no process action, this is an error
    if not command and not process_action:
        raise ValueError("Either command or process_action must be provided")

    # Build the full command for display
    cmd_parts = shlex.split(command)
    if args:
        cmd_parts.extend(shlex.split(args))

    full_command = " ".join(cmd_parts)

    # Blacklist check
    base_cmd = cmd_parts[0]
    if base_cmd in BLOCKED_COMMANDS:
        error_msg = f"Command '{base_cmd}' is not allowed for security reasons."
        return json.dumps({
            "success": False,
            "error": error_msg
        })

    try:
        if keep_alive:
            return start_persistent_process(cmd_parts, full_command)
        else:
            return execute_command_and_wait(cmd_parts, full_command)
    except Exception as e:
        error_msg = str(e)
        return json.dumps({
            "success": False,
            "error": error_msg,
            "command_attempted": full_command
        })


def execute_command_and_wait(cmd_parts, full_command):
    """Execute command and wait for completion (original behavior)"""
    process = subprocess.Popen(
        cmd_parts,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.getcwd()
    )
    stdout, stderr = process.communicate()

    result = {
        "success": process.returncode == 0,
        "stdout": stdout.strip(),
        "stderr": stderr.strip(),
        "returncode": process.returncode,
        "command_executed": full_command
    }
    return json.dumps(result)


def start_persistent_process(cmd_parts, full_command):
    """Start a persistent process that keeps running"""
    global process_counter

    try:
        process = subprocess.Popen(
            cmd_parts,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
            cwd=os.getcwd(),
            bufsize=0  # Unbuffered for real-time interaction
        )

        process_counter += 1
        process_id = process_counter

        # Store process info
        active_processes[process_id] = {
            "process": process,
            "command": full_command,
            "start_time": time.time(),
            "output_buffer": [],
            "error_buffer": []
        }

        # Start background threads to capture output
        start_output_capture(process_id)

        # Give the process a moment to start
        time.sleep(0.1)
        
        # Check if process is still running after startup
        if process.poll() is not None:
            return json.dumps({
                "success": False,
                "error": f"Process {process_id} exited immediately with code {process.returncode}",
                "command": full_command
            })

        result = {
            "success": True,
            "process_id": process_id,
            "command_executed": full_command,
            "status": "running",
            "message": f"Process started with ID {process_id}. Use process_action to interact with it."
        }
        return json.dumps(result)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to start process: {str(e)}",
            "command": full_command
        })


def start_output_capture(process_id):
    """Start background threads to capture stdout and stderr"""
    process_info = active_processes[process_id]
    process = process_info["process"]

    def capture_stdout():
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            process_info["output_buffer"].append(line.rstrip())
            if len(process_info["output_buffer"]) > 1000:  # Limit buffer size
                process_info["output_buffer"] = process_info["output_buffer"][-500:]

    def capture_stderr():
        for line in iter(process.stderr.readline, ''):
            if not line:
                break
            process_info["error_buffer"].append(line.rstrip())
            if len(process_info["error_buffer"]) > 1000:  # Limit buffer size
                process_info["error_buffer"] = process_info["error_buffer"][-500:]

    threading.Thread(target=capture_stdout, daemon=True).start()
    threading.Thread(target=capture_stderr, daemon=True).start()


def handle_process_action(input_data):
    """
    Handles process management actions for processes started by this tool.

    Note:
    The 'kill' action here does NOT execute the dangerous shell command 'kill'.
    Instead, it safely terminates a process that was previously started and is tracked
    in ACTIVE_PROCESSES. The blacklist at the top of the file prevents users from
    running the actual 'kill' shell command. This function only manages internal process
    lifecycle and is safe to use.
    """
    action = input_data.get("process_action")
    process_id = input_data.get("process_id")

    if action == "list":
        return list_processes()
    elif action == "cleanup":
        return cleanup_dead_processes()
    elif action == "cleanup_all":
        return cleanup_all_processes()
    elif action == "cleanup_status":
        return get_cleanup_status()
    elif action == "cleanup_restart":
        return restart_auto_cleanup()
    elif action == "input" and process_id:
        input_text = input_data.get("input_text", "")
        return send_input_to_process(process_id, input_text)
    elif action in ["kill", "status", "output"] and process_id:
        if action == "kill":
            return kill_process(process_id)
        elif action == "status":
            return get_process_status(process_id)
        elif action == "output":
            return get_process_output(process_id)
    else:
        return json.dumps({
            "success": False,
            "error": f"Invalid process action '{action}' or missing process_id. Valid actions: list, cleanup, cleanup_all, cleanup_status, cleanup_restart, input, kill, status, output"
        })


def list_processes():
    """List all active processes and cleanup dead ones"""
    if not active_processes:
        return json.dumps({
            "success": True,
            "processes": [],
            "message": "No active processes"
        })

    processes = []
    dead_processes = []
    
    for pid, info in active_processes.items():
        process = info["process"]
        is_running = process.poll() is None

        processes.append({
            "process_id": pid,
            "command": info["command"],
            "status": "running" if is_running else "finished",
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(info["start_time"])),
            "return_code": process.returncode if not is_running else None
        })
        
        # Mark finished processes for cleanup (optional)
        if not is_running:
            dead_processes.append(pid)

    return json.dumps({
        "success": True,
        "processes": processes,
        "dead_processes": dead_processes
    })


def kill_process(process_id):
    """Kill a specific process"""
    if process_id not in active_processes:
        return json.dumps({
            "success": False,
            "error": f"Process {process_id} not found"
        })

    process_info = active_processes[process_id]
    process = process_info["process"]

    if process.poll() is not None:
        return json.dumps({
            "success": False,
            "error": f"Process {process_id} is already finished"
        })

    try:
        process.terminate()
        return json.dumps({
            "success": True,
            "message": f"Process {process_id} terminated"
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to terminate process {process_id}: {str(e)}"
        })


def get_process_status(process_id):
    """Get status of a specific process"""
    if process_id not in active_processes:
        return json.dumps({
            "success": False,
            "error": f"Process {process_id} not found"
        })

    process_info = active_processes[process_id]
    process = process_info["process"]
    is_running = process.poll() is None

    return json.dumps({
        "success": True,
        "process_id": process_id,
        "command": process_info["command"],
        "status": "running" if is_running else "finished",
        "return_code": process.returncode if not is_running else None,
        "start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(process_info["start_time"])),
        "output_lines": len(process_info["output_buffer"]),
        "error_lines": len(process_info["error_buffer"])
    })


def get_process_output(process_id):
    """Get output from a specific process"""
    if process_id not in active_processes:
        return json.dumps({
            "success": False,
            "error": f"Process {process_id} not found"
        })

    process_info = active_processes[process_id]
    process = process_info["process"]

    # Check if process is still running
    is_running = process.poll() is None

    return json.dumps({
        "success": True,
        "process_id": process_id,
        "stdout": process_info["output_buffer"],
        "stderr": process_info["error_buffer"],
        "command": process_info["command"],
        "status": "running" if is_running else "finished",
        "return_code": process.returncode if not is_running else None
    })


def cleanup_dead_processes():
    """Remove finished processes from the active list"""
    global active_processes
    
    dead_processes = []
    for pid, info in list(active_processes.items()):
        process = info["process"]
        if process.poll() is not None:
            dead_processes.append(pid)
            del active_processes[pid]
    
    return json.dumps({
        "success": True,
        "message": f"Cleaned up {len(dead_processes)} dead processes",
        "cleaned_processes": dead_processes
    })


def send_input_to_process(process_id, input_text):
    """Send input to a running process with timeout"""
    if process_id not in active_processes:
        return json.dumps({
            "success": False,
            "error": f"Process {process_id} not found"
        })

    process_info = active_processes[process_id]
    process = process_info["process"]

    if process.poll() is not None:
        return json.dumps({
            "success": False,
            "error": f"Process {process_id} is not running"
        })

    try:
        # Use a timeout mechanism to prevent hanging
        def send_input():
            try:
                process.stdin.write(input_text + "\n")
                process.stdin.flush()
                return True
            except Exception as e:
                return str(e)

        # Create a thread to send input with timeout
        result = [None]
        def target():
            result[0] = send_input()

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=10)  # 10 second timeout

        if thread.is_alive():
            return json.dumps({
                "success": False,
                "error": f"Timeout: Failed to send input to process {process_id} within 10 seconds"
            })

        if result[0] is True:
            return json.dumps({
                "success": True,
                "message": f"Input sent to process {process_id}",
                "input_sent": input_text
            })
        else:
            return json.dumps({
                "success": False,
                "error": f"Failed to send input to process {process_id}: {result[0]}"
            })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to send input to process {process_id}: {str(e)}"
        })


# ------------------------------------------------------------------
# Automatic Cleanup Functions
# ------------------------------------------------------------------

def auto_cleanup_processes():
    """Background thread function that automatically cleans up dead processes"""
    global AUTO_CLEANUP_ENABLED
    
    while AUTO_CLEANUP_ENABLED:
        try:
            if active_processes:
                # Clean up dead processes
                dead_processes = []
                for pid, info in list(active_processes.items()):
                    process = info["process"]
                    if process.poll() is not None:
                        dead_processes.append(pid)
                        # Close file handles
                        try:
                            process.stdout.close()
                            process.stderr.close()
                            process.stdin.close()
                        except:
                            pass
                        del active_processes[pid]
                
                if dead_processes and len(dead_processes) > 0:
                    with open('/tmp/debug_command_tool.log', 'a') as f:
                        f.write(f"Auto-cleanup: Removed {len(dead_processes)} dead processes: {dead_processes}\n")
                        
            time.sleep(CLEANUP_INTERVAL)
        except Exception as e:
            with open('/tmp/debug_command_tool.log', 'a') as f:
                f.write(f"Auto-cleanup error: {str(e)}\n")
        

def start_auto_cleanup():
    """Start the automatic cleanup thread with improved error handling"""
    global CLEANUP_THREAD, AUTO_CLEANUP_ENABLED
    
    try:
        # Stop any existing thread first
        if CLEANUP_THREAD is not None and CLEANUP_THREAD.is_alive():
            AUTO_CLEANUP_ENABLED = False
            time.sleep(0.1)  # Give thread time to stop
        
        # Start new thread
        AUTO_CLEANUP_ENABLED = True
        CLEANUP_THREAD = threading.Thread(target=auto_cleanup_processes, daemon=True, name="AutoCleanup")
        CLEANUP_THREAD.start()
        
        # Verify thread started successfully
        time.sleep(0.1)
        if CLEANUP_THREAD.is_alive():
            with open('/tmp/debug_command_tool.log', 'a') as f:
                f.write(f"Auto-cleanup thread started successfully (Thread ID: {CLEANUP_THREAD.ident})\n")
            return True
        else:
            with open('/tmp/debug_command_tool.log', 'a') as f:
                f.write("Auto-cleanup thread failed to start\n")
            return False
    except Exception as e:
        with open('/tmp/debug_command_tool.log', 'a') as f:
            f.write(f"Error starting auto-cleanup thread: {str(e)}\n")
        return False


def stop_auto_cleanup():
    """Stop the automatic cleanup thread"""
    global AUTO_CLEANUP_ENABLED
    AUTO_CLEANUP_ENABLED = False
    with open('/tmp/debug_command_tool.log', 'a') as f:
        f.write("Auto-cleanup thread stopped\n")


def emergency_cleanup():
    """Emergency cleanup function called on program exit"""
    global active_processes
    
    if active_processes:
        with open('/tmp/debug_command_tool.log', 'a') as f:
            f.write(f"Emergency cleanup: Terminating {len(active_processes)} processes\n")
        
        for pid, info in list(active_processes.items()):
            process = info["process"]
            try:
                if process.poll() is None:  # Still running
                    process.terminate()
                    time.sleep(0.1)
                    if process.poll() is None:  # Still running after terminate
                        process.kill()
                # Close file handles
                process.stdout.close()
                process.stderr.close()
                process.stdin.close()
            except Exception as e:
                with open('/tmp/debug_command_tool.log', 'a') as f:
                    f.write(f"Error cleaning up process {pid}: {str(e)}\n")
        
        active_processes.clear()
        stop_auto_cleanup()


@contextmanager
def process_manager():
    """Context manager for automatic process cleanup"""
    start_auto_cleanup()
    try:
        yield
    finally:
        emergency_cleanup()


def cleanup_all_processes():
    """Manually cleanup all processes - can be called via process_action"""
    emergency_cleanup()
    return json.dumps({
        "success": True,
        "message": "All processes have been cleaned up",
        "action": "cleanup_all"
    })


def get_cleanup_status():
    """Get status of automatic cleanup system"""
    global AUTO_CLEANUP_ENABLED, CLEANUP_THREAD
    
    thread_status = "running" if CLEANUP_THREAD and CLEANUP_THREAD.is_alive() else "stopped"
    thread_name = CLEANUP_THREAD.name if CLEANUP_THREAD else "None"
    thread_id = CLEANUP_THREAD.ident if CLEANUP_THREAD and CLEANUP_THREAD.is_alive() else None
    
    return json.dumps({
        "success": True,
        "auto_cleanup_enabled": AUTO_CLEANUP_ENABLED,
        "cleanup_thread_status": thread_status,
        "cleanup_thread_name": thread_name,
        "cleanup_thread_id": thread_id,
        "cleanup_interval": CLEANUP_INTERVAL,
        "active_processes_count": len(active_processes)
    })


def restart_auto_cleanup():
    """Restart the automatic cleanup thread"""
    stop_auto_cleanup()
    time.sleep(0.2)  # Give thread time to stop
    success = start_auto_cleanup()
    
    return json.dumps({
        "success": success,
        "message": "Auto-cleanup thread restart attempted",
        "result": "started" if success else "failed"
    })


def ensure_auto_cleanup_running():
    """Ensure auto-cleanup is running, start it if not"""
    global CLEANUP_THREAD, AUTO_CLEANUP_ENABLED
    
    if not AUTO_CLEANUP_ENABLED or CLEANUP_THREAD is None or not CLEANUP_THREAD.is_alive():
        with open('/tmp/debug_command_tool.log', 'a') as f:
            f.write("Auto-cleanup not running, attempting to start...\n")
        return start_auto_cleanup()
    return True


# Register cleanup functions
atexit.register(emergency_cleanup)

# Handle signals for graceful shutdown
def signal_handler(signum, frame):
    emergency_cleanup()
    exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Start auto-cleanup immediately when module is loaded
start_auto_cleanup()

# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
CommandLineToolDefinition = ToolDefinition(
    name="command_line_tool",
    description="A command-line tool for safely executing and managing processes. It can run commands to completion or start persistent background processes, manage them (list, kill, check status, retrieve output, send input, and clean up), and automatically removes dead processes every 30 seconds or on program exit. Dangerous commands are blocked for security.",
    input_schema=CommandLineInputSchema,
    function=command_line_tool
)