from kefu_z.agents.base_agent import BaseAgent
from kefu_z.agents.handoff import HandoffRequest


PRODUCT_PROMPT = """你是电商产品知识客服，擅长解答产品规格、使用方法等问题。

你的职责：
1. 解答产品规格参数问题
2. 说明产品使用方法和注意事项
3. 对比不同产品的技术参数

工作方式：
- 使用search_products搜索相关产品
- 使用get_product_detail获取产品详细规格
- 如果用户想购买，使用[HANDOFF:presale]转交售前客服
- 最多进行5轮工具调用

注意：
- 回答要准确、专业
- 参数数据以系统查询结果为准，不要编造"""


class ProductAgent(BaseAgent):
    def __init__(self, llm, mcp, memory, state_mgr, config):
        super().__init__(
            name="product",
            llm=llm,
            mcp=mcp,
            memory=memory,
            state_mgr=state_mgr,
            config=config,
            tool_names=["search_products", "get_product_detail"],
            system_prompt=PRODUCT_PROMPT,
        )

    def process(self, message: str, session_id: str) -> str | HandoffRequest:
        return self._react_loop(message, session_id)
