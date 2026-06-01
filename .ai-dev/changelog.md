## 2026-06-01 变更记录
- 变更: 修复LLM生成错误user_id的bug
- 原因: 浏览器实测发现LLM在tool_call中使用错误的user_id
- 影响: base_agent.py修改，user_id强制覆盖
- 优先级: P0
