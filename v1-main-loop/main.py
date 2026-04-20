import argparse
import sys

from openai import OpenAI

from loop_state import LoopState, Transition
from tools import execute_tool, get_tools_schema

MAX_TURNS = 10


def build_query(user_input: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": "You are a helpful agent. Prefer calling tools when possible.",
        },
        {"role": "user", "content": user_input},
    ]


def run_one_turn(state: LoopState, client: OpenAI) -> bool:
    response = client.chat.completions.create(
        model="qwen3-max",
        messages=state.messages,
        tools=get_tools_schema(),
        tool_choice="auto",
    )
    message = response.choices[0].message
    state.messages.append(message.model_dump())

    if not message.tool_calls:
        state.transition = None
        return False

    has_tool_result = False
    for tool_call in message.tool_calls:
        result = execute_tool(
            name=tool_call.function.name,
            arguments=tool_call.function.arguments,
        )
        print(f"$ {tool_call.function.name}: {tool_call.function.arguments}")
        print(result[:200])
        state.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": result,
            }
        )
        has_tool_result = True

    if not has_tool_result:
        state.transition = None
        return False

    state.turn += 1
    state.transition = Transition.TOOL_RESULT
    return True


def agent_loop(state: LoopState, client: OpenAI) -> None:
    while state.turn < MAX_TURNS and run_one_turn(state, client):
        pass


def read_user_input() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, help="User input query")
    args = parser.parse_args()
    if args.query:
        return args.query.strip()

    if sys.stdin.isatty():
        return input("请输入用户信息: ").strip()

    piped = sys.stdin.read().strip()
    if piped:
        return piped
    raise ValueError("未读取到用户输入，请使用 --query 或在交互终端中输入。")


def main() -> None:
    user_input = read_user_input()
    state = LoopState(messages=build_query(user_input))
    client = OpenAI()
    agent_loop(state=state, client=client)
    print(f"循环结束，总轮次: {state.turn}")


if __name__ == "__main__":
    main()
