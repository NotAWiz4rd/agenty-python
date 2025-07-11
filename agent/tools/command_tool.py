# command_line_tool.py

import json
import os
import shlex
import subprocess
import threading
import time

from tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Global process storage for persistent processes
# ------------------------------------------------------------------
active_processes = {}
process_counter = 0

# ------------------------------------------------------------------
# Blacklist of blocked commands
# ------------------------------------------------------------------
BLOCKED_COMMANDS = {
    "rm", "shutdown", "reboot", "halt", "poweroff", "mkfs", "dd", "init", "telinit", "kill", "killall", "passwd",
    "whoami"
}

# ------------------------------------------------------------------
# Input schema for the command_line_tool
# ------------------------------------------------------------------
CommandLineInputSchema = {
    "type": "object",
    "properties": {
        "command": {
            "type": "string",
            "description": "The shell command to execute (e.g., 'ls', 'echo', 'cat', etc.)."
        },
        "args": {
            "type": "string",
            "description": "Additional arguments for the command."
        },
        "keep_alive": {
            "type": "boolean",
            "description": "If true, keeps the process running and returns a process ID for later interaction."
        },
        "process_action": {
            "type": "string",
            "description": "Action to perform on a process ('list', 'status', 'output', 'input').",
        },
        "process_id": {
            "type": "integer",
            "description": "Process ID for process operations (list, status, output, input). Required for process_action operations."
        },
        "input_text": {
            "type": "string",
            "description": "Text to send to a running process's stdin. You need to specify process_id and process_action=input.",
        }
    },
    "required": []
}


def command_line_tool(input_data: dict) -> str:
    """
    Command line tool that supports:
    - Regular command execution (wait for completion)
    - Persistent processes (keep_alive=True)
    - Interactive input to running processes
    """
    global active_processes, process_counter

    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    # Handle process management actions or input to existing process
    process_action = input_data.get("process_action")
    process_id = input_data.get("process_id")
    input_text = input_data.get("input_text")

    # If we have input_text and process_id but no explicit action, assume "input"
    if input_text and process_id and not process_action:
        input_data["process_action"] = "input"
        return handle_process_action(input_data)
    elif process_action:
        return handle_process_action(input_data)

    command = input_data.get("command", "")
    args = input_data.get("args", "")
    keep_alive = input_data.get("keep_alive", False)

    if not command and not process_action:
        raise ValueError("Command must be provided")

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
    """Execute command and wait for completion"""
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
    """
    action = input_data.get("process_action")
    process_id = input_data.get("process_id")

    if action == "list":
        return list_processes()
    if action == "status" and process_id:
        return get_process_status(process_id)
    if action == "output" and process_id:
        return get_process_output(process_id)
    if action == "input" and process_id:
        return send_input_to_process(process_id, input_data.get("input_text", ""))
    return json.dumps({"success": False, "error": "Invalid action or missing process_id"})


def list_processes():
    """List all active processes and cleanup dead ones"""
    if not active_processes:
        return json.dumps({
            "success": True,
            "processes": [],
            "message": "No active processes"
        })

    processes = []

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

    return json.dumps({
        "success": True,
        "processes": processes,
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

    output_lines = process_info["output_buffer"]
    debug_color = "\033[36m"  # Cyan
    reset_color = "\033[0m"  # Reset to default
    for line in output_lines:
        print(f"{debug_color}{line}{reset_color}")

    return json.dumps({
        "success": True,
        "process_id": process_id,
        "stdout": process_info["output_buffer"],
        "stderr": process_info["error_buffer"],
        "command": process_info["command"],
        "status": "running" if is_running else "finished",
        "return_code": process.returncode if not is_running else None
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
            process_info["output_buffer"] = []  # Clear output buffer after sending input
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
# ToolDefinition instance
# ------------------------------------------------------------------
CommandLineToolDefinition = ToolDefinition(
    name="command_line_tool",
    description="A command-line tool for safely executing. It can run commands to completion or start persistent background processes. Dangerous commands are blocked for security.",
    input_schema=CommandLineInputSchema,
    function=command_line_tool
)
