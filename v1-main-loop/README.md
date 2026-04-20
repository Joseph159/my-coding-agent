# v1-main-loop

最小可执行 agent loop 示例，包含：

- `LoopState`：保存消息列表、循环轮次、流转原因
- `Transition`：流转枚举（当前仅 `tool_result`）
- 主循环：读取用户输入 -> 构建 query -> 进入 loop
- `run_bash` 工具：无输出时返回 `"(no output)"`

## 运行

```bash
cd v1-main-loop
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
# 或非交互方式
python main.py --query "帮我回显这句话"
```
