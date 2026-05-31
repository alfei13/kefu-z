# 知识管理

## 架构决策
- 选择Python自研Agent框架而非LangChain：MVP阶段轻量优先，避免重依赖
- 选择Gradio而非Streamlit：Gradio Chatbot组件更适合对话式UI
- 选择Spring Boot+H2做Mock：Java生态标准，内嵌数据库零安装
- MCP通过HTTP模拟而非gRPC：MVP阶段HTTP更简单，后续可升级
- 选择Handoff模式而非Swarm：客服场景适合接力式处理，去中心化不适合
- 选择ReAct循环而非单轮工具调用：支持多步推理，更智能
- user_id统一为Integer：修复V1中String/Integer不一致问题

## 调试经验
- DashScope API需要OpenAI兼容接口：api_base=https://dashscope.aliyuncs.com/compatible-mode/v1
- .env文件不能提交git，API Key只能从环境变量读取
- Gradio 5.x不支持type='messages'参数，使用tuple格式
- Gradio不支持show_copy_button参数（某些版本），需移除
- 服务器绑定127.0.0.1而非0.0.0.0，避免代理干扰
- curl冒烟测试需加--noproxy '*'绕过代理
- Java Mock服务需用JDK 17运行（JDK 26与Lombok不兼容）
- 端口7860可能被之前的Gradio进程占用，需先kill

## 项目约定
- Python代码遵循PEP8
- Agent类统一接口：继承BaseAgent + process(message, session_id) -> str | HandoffRequest
- 工具调用统一通过MCPClient.call(tool_name, params)
- 日志使用structlog，记录路由决策、工具调用、LLM响应
- Function Calling使用标准role:"tool"消息格式

## 已知陷阱
- DashScope function_calling返回格式与OpenAI略有不同，tool_calls中arguments可能是字符串
- H2内存数据库重启后数据丢失，需要在data.sql中初始化数据
- LLM返回的JSON可能被markdown代码块包裹，需要strip处理
- LLM返回的JSON字段可能是dict/list而非string，需要isinstance检查
- Gradio默认多线程，全局变量需要线程安全保护
