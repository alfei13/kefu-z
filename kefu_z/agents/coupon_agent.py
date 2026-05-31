from kefu_z.agents.base_agent import BaseAgent
from kefu_z.agents.handoff import HandoffRequest


COUPON_PROMPT = """你是电商优惠券客服，擅长查询和验证优惠券。

你的职责：
1. 查询用户可用的优惠券
2. 验证优惠码是否有效
3. 说明优惠券使用规则

工作方式：
- 使用query_coupons查询用户优惠券（user_id会自动填充）
- 使用check_coupon验证优惠码
- 如果用户想下单，使用[HANDOFF:presale]转交售前客服
- 如果用户问订单，使用[HANDOFF:order]转交
- 最多进行5轮工具调用

优惠券类型说明：
- fixed: 固定金额减免
- percent: 百分比折扣

注意：
- 告知优惠券有效期和使用条件
- 已使用的优惠券不能重复使用"""


class CouponAgent(BaseAgent):
    def __init__(self, llm, mcp, memory, state_mgr, config):
        super().__init__(
            name="coupon",
            llm=llm,
            mcp=mcp,
            memory=memory,
            state_mgr=state_mgr,
            config=config,
            tool_names=["query_coupons", "check_coupon"],
            system_prompt=COUPON_PROMPT,
        )

    def process(self, message: str, session_id: str) -> str | HandoffRequest:
        return self._react_loop(message, session_id)
