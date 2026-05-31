from kefu_z.agents.base_agent import BaseAgent
from kefu_z.agents.handoff import HandoffRequest


HUMAN_HANDOFF_PROMPT = """你是人工客服转接助手。

当AI客服无法解决用户问题，或用户情绪激动需要人工服务时，你会介入。

你的职责：
1. 告知用户正在转接人工客服
2. 收集用户问题的简要描述
3. 安抚用户情绪

注意：
- 语气要温和、专业
- 表达对用户问题的重视
- 告知预计等待时间"""


class HumanHandoffAgent(BaseAgent):
    def __init__(self, llm, mcp, memory, state_mgr, config):
        super().__init__(
            name="human",
            llm=llm,
            mcp=mcp,
            memory=memory,
            state_mgr=state_mgr,
            config=config,
            tool_names=[],
            system_prompt=HUMAN_HANDOFF_PROMPT,
        )

    def process(self, message: str, session_id: str) -> str | HandoffRequest:
        state = self.state_mgr.get_or_create(session_id)
        emotion = state.emotion

        if emotion == "angry":
            reply = "我理解您的心情，对于给您带来的不便深表歉意。我正在为您转接人工客服，预计等待1-2分钟，请您稍候。人工客服会优先处理您的问题。"
        else:
            reply = self._simple_chat(message, session_id)
            if "转接人工" not in reply and "人工客服" not in reply:
                reply = "好的，我正在为您转接人工客服。请您简要描述一下您的问题，这样人工客服可以更快地帮助您。预计等待1-2分钟。"

        self.memory.add_message(session_id, "assistant", reply)
        return reply
