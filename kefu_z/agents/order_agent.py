from kefu_z.agents.base_agent import BaseAgent
from kefu_z.agents.handoff import HandoffRequest


ORDER_PROMPT = """你是电商订单查询客服，擅长查询订单状态和物流信息。

你的职责：
1. 查询用户订单列表
2. 查询订单详情和物流状态
3. 解答订单相关问题

工作方式：
- 使用query_orders查询用户订单（user_id会自动填充）
- 使用get_order_detail获取订单详情和物流信息
- 如果用户想退货/换货，使用[HANDOFF:aftersale]转交售后客服
- 如果用户问优惠券，使用[HANDOFF:coupon]转交
- 最多进行5轮工具调用

订单状态说明：
- pending: 待付款
- paid: 已付款
- shipped: 已发货
- delivered: 已送达
- cancelled: 已取消

注意：
- 物流信息包含快递公司和快递单号
- 回答要清晰、准确"""


class OrderAgent(BaseAgent):
    def __init__(self, llm, mcp, memory, state_mgr, config):
        super().__init__(
            name="order",
            llm=llm,
            mcp=mcp,
            memory=memory,
            state_mgr=state_mgr,
            config=config,
            tool_names=["query_orders", "get_order_detail"],
            system_prompt=ORDER_PROMPT,
        )

    def process(self, message: str, session_id: str) -> str | HandoffRequest:
        return self._react_loop(message, session_id)
