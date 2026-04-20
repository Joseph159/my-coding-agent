import json
import os
import subprocess
from typing import Any


def get_tools_schema() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "run_bash",
                "description": "Execute a safe bash command in current project.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Bash command to run.",
                        }
                    },
                    "required": ["command"],
                    "additionalProperties": False,
                },
            },
        }
    ]


def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(item in command for item in dangerous):
        return "Error: Dangerous command blocked"
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
    except (FileNotFoundError, OSError) as error:
        return f"Error: {error}"

    output = (result.stdout + result.stderr).strip()
    return output[:50000] if output else "(no output)"


def execute_tool(name: str, arguments: str) -> str:
    parsed_args = json.loads(arguments or "{}")
    if name == "run_bash":
        return run_bash(parsed_args.get("command", ""))
    return json.dumps({"error": f"Unknown tool: {name}"}, ensure_ascii=False)
