from kefu_z.agents.base_agent import BaseAgent
from kefu_z.agents.handoff import HandoffRequest


CHITCHAT_PROMPT = """你是电商客服的闲聊助手，负责处理与购物无关的日常对话。

你的职责：
1. 友好地回应用户的闲聊
2. 在适当的时候引导用户了解商品和服务
3. 对于无法处理的问题，建议转接专业客服

工作方式：
- 直接对话，不需要调用任何工具
- 如果用户提到产品、订单、优惠券、售后等购物相关问题，使用[HANDOFF:presale]、[HANDOFF:order]等转交
- 保持友好、幽默的风格

注意：
- 回答要自然、亲切
- 不要编造商品信息"""


class ChitchatAgent(BaseAgent):
    def __init__(self, llm, mcp, memory, state_mgr, config):
        super().__init__(
            name="chitchat",
            llm=llm,
            mcp=mcp,
            memory=memory,
            state_mgr=state_mgr,
            config=config,
            tool_names=[],
            system_prompt=CHITCHAT_PROMPT,
        )

    def process(self, message: str, session_id: str) -> str | HandoffRequest:
        return self._simple_chat(message, session_id)
