from kefu_z.agents.base_agent import BaseAgent
from kefu_z.agents.handoff import HandoffRequest


AFTERSALE_PROMPT = """你是电商售后服务客服，擅长处理退款、换货、维修等售后问题。

你的职责：
1. 查询售后申请进度
2. 帮助用户创建售后申请
3. 解答售后政策问题

工作方式：
- 使用query_aftersale查询售后进度（需要order_id）
- 使用create_aftersale创建售后申请（需要order_id、user_id、type、reason）
- 如果问题复杂无法解决，使用[HANDOFF:human]转交人工客服
- 最多进行5轮工具调用

售后类型：
- refund: 退款
- exchange: 换货
- repair: 维修

重要规则：
- 创建售后申请前，必须先确认用户意图，向用户展示即将提交的信息并征求确认
- 确认格式："您确认要为订单#{order_id}申请{type}吗？原因：{reason}。请回复'确认'继续。"
- 只有用户明确确认后才调用create_aftersale
- 如果用户取消，则不执行操作

注意：
- 态度要耐心、体贴
- 售后问题要优先处理"""


class AftersaleAgent(BaseAgent):
    def __init__(self, llm, mcp, memory, state_mgr, config):
        super().__init__(
            name="aftersale",
            llm=llm,
            mcp=mcp,
            memory=memory,
            state_mgr=state_mgr,
            config=config,
            tool_names=["query_aftersale", "create_aftersale", "get_order_detail", "query_orders"],
            system_prompt=AFTERSALE_PROMPT,
        )

    def process(self, message: str, session_id: str) -> str | HandoffRequest:
        state = self.state_mgr.get_or_create(session_id)

        if state.pending_confirmation:
            if message.strip() in ["确认", "确认", "是", "yes", "ok", "好的"]:
                action = state.pending_confirmation
                self.state_mgr.clear_pending_confirmation(session_id)
                result = self.mcp.call("create_aftersale", action["params"])
                if "error" in result:
                    reply = f"抱歉，售后申请提交失败：{result['error']}"
                else:
                    reply = f"售后申请已成功提交！申请ID：{result.get('id', 'N/A')}，状态：{result.get('status', 'pending')}。我们会尽快处理，请耐心等待。"
                self.memory.add_message(session_id, "user", message)
                self.memory.add_message(session_id, "assistant", reply)
                return reply
            else:
                self.state_mgr.clear_pending_confirmation(session_id)
                reply = "好的，已取消售后申请。还有其他我可以帮助的吗？"
                self.memory.add_message(session_id, "user", message)
                self.memory.add_message(session_id, "assistant", reply)
                return reply

        return self._react_loop(message, session_id)
