from kefu_z.agents.base_agent import BaseAgent
from kefu_z.agents.handoff import HandoffRequest


PRESALE_PROMPT = """你是电商售前咨询客服，擅长产品推荐和购买建议。

你的职责：
1. 根据用户需求推荐合适的产品
2. 比较不同产品的优劣
3. 提供购买建议和搭配推荐

工作方式：
- 使用search_products搜索相关产品
- 使用get_product_detail获取产品详情
- 如果用户问到订单、优惠券、售后等问题，使用[HANDOFF:order]、[HANDOFF:coupon]、[HANDOFF:aftersale]转交
- 最多进行5轮工具调用，收集足够信息后给出推荐

注意：
- 回答要专业、热情
- 如果搜索不到产品，建议用户换关键词
- 推荐时要说明理由"""


class PresaleAgent(BaseAgent):
    def __init__(self, llm, mcp, memory, state_mgr, config):
        super().__init__(
            name="presale",
            llm=llm,
            mcp=mcp,
            memory=memory,
            state_mgr=state_mgr,
            config=config,
            tool_names=["search_products", "get_product_detail"],
            system_prompt=PRESALE_PROMPT,
        )

    def process(self, message: str, session_id: str) -> str | HandoffRequest:
        return self._react_loop(message, session_id)
