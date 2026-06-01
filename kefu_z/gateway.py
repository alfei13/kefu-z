import structlog
from kefu_z.config import Config
from kefu_z.llm_client import LLMClient
from kefu_z.mcp_client import MCPClient
from kefu_z.conversation_memory import ConversationMemory
from kefu_z.dialog_state import DialogStateManager
from kefu_z.agents.router_agent import RouterAgent
from kefu_z.agents.presale_agent import PresaleAgent
from kefu_z.agents.product_agent import ProductAgent
from kefu_z.agents.order_agent import OrderAgent
from kefu_z.agents.coupon_agent import CouponAgent
from kefu_z.agents.aftersale_agent import AftersaleAgent
from kefu_z.agents.chitchat_agent import ChitchatAgent
from kefu_z.agents.human_handoff_agent import HumanHandoffAgent
from kefu_z.agents.handoff import HandoffRequest

logger = structlog.get_logger(__name__)


class Orchestrator:
    def __init__(self, config: Config):
        self.config = config
        self.llm = LLMClient(config)
        self.mcp = MCPClient(config)
        self.memory = ConversationMemory(
            ttl_seconds=config.session_ttl_seconds,
            max_messages=config.max_messages_per_session,
            max_sessions=config.max_sessions,
        )
        self.state_mgr = DialogStateManager()
        self.router = RouterAgent(self.llm, config)

        agent_kwargs = {
            "llm": self.llm,
            "mcp": self.mcp,
            "memory": self.memory,
            "state_mgr": self.state_mgr,
            "config": config,
        }
        self.agents = {
            "presale": PresaleAgent(**agent_kwargs),
            "product": ProductAgent(**agent_kwargs),
            "order": OrderAgent(**agent_kwargs),
            "coupon": CouponAgent(**agent_kwargs),
            "aftersale": AftersaleAgent(**agent_kwargs),
            "chitchat": ChitchatAgent(**agent_kwargs),
            "human": HumanHandoffAgent(**agent_kwargs),
        }

    def process(self, message: str, session_id: str, user_id: int = 0) -> str:
        logger.info("orchestrator_process", session_id=session_id, user_id=user_id, message=message[:50])

        state = self.state_mgr.get_or_create(session_id, user_id)
        self.state_mgr.increment_turn(session_id)

        if user_id:
            self.memory.set_context(session_id, "user_id", user_id)

        try:
            agent_name, confidence, emotion = self.router.route(message, session_id, self.state_mgr)
            logger.info("route_result", session_id=session_id, agent=agent_name, confidence=confidence, emotion=emotion)

            if state.current_agent and state.turn_count > 1 and emotion != "angry":
                current = state.current_agent
                if current in self.agents and current != "chitchat" and confidence < 0.9:
                    agent_name = current
                    logger.info("keep_current_agent", session_id=session_id, agent=current)

            reply = self._execute_with_handoff(message, session_id, agent_name)

            self.state_mgr.update_phase(session_id, "closing")
            logger.info("orchestrator_complete", session_id=session_id, agent=agent_name)

            return reply

        except Exception as e:
            logger.error("orchestrator_error", session_id=session_id, error=str(e))
            return "抱歉，系统出现异常，请稍后重试。如需帮助，可以说'转人工客服'。"

    def _execute_with_handoff(self, message: str, session_id: str, agent_name: str) -> str:
        max_handoffs = self.config.max_handoff_rounds
        current_agent = agent_name
        handoff_count = 0

        while handoff_count <= max_handoffs:
            if current_agent not in self.agents:
                current_agent = "chitchat"

            agent = self.agents[current_agent]
            state = self.state_mgr.get_or_create(session_id)
            state.current_agent = current_agent

            logger.info("agent_executing", agent=current_agent, session_id=session_id, handoff=handoff_count)

            result = agent.process(message, session_id)

            if isinstance(result, HandoffRequest):
                handoff_count += 1
                self.state_mgr.add_handoff(session_id, current_agent, result.target_agent, result.reason)
                logger.info(
                    "handoff",
                    session_id=session_id,
                    from_agent=current_agent,
                    to_agent=result.target_agent,
                    reason=result.reason,
                    handoff_count=handoff_count,
                )
                current_agent = result.target_agent
                if handoff_count >= max_handoffs:
                    logger.warning("max_handoffs_reached", session_id=session_id)
                    return "您的问题涉及多个方面，我已经尽力处理。如需进一步帮助，建议转接人工客服。"
                continue

            return result

        return "抱歉，处理过程中出现了问题，请重新描述您的需求。"
