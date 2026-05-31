from kefu_z.llm_client import LLMClient
from kefu_z.mcp_client import MCPClient
from kefu_z.conversation_memory import ConversationMemory
from kefu_z.dialog_state import DialogStateManager
from kefu_z.config import Config
import structlog

logger = structlog.get_logger(__name__)


class EmotionAnalyzer:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def analyze(self, message: str) -> str:
        prompt = f"""分析以下用户消息的情感状态，只返回一个词：neutral（中性）、happy（开心）、angry（愤怒）、confused（困惑）。

用户消息：{message}

情感："""
        try:
            result = self.llm.chat([{"role": "user", "content": prompt}], temperature=0.1)
            emotion = result.strip().lower()
            valid = ["neutral", "happy", "angry", "confused"]
            for v in valid:
                if v in emotion:
                    return v
            return "neutral"
        except Exception as e:
            logger.error("emotion_analysis_failed", error=str(e))
            return "neutral"


class RouterAgent:
    VALID_AGENTS = ["presale", "product", "order", "coupon", "aftersale", "chitchat", "human"]

    def __init__(self, llm: LLMClient, config: Config):
        self.llm = llm
        self.config = config
        self.emotion_analyzer = EmotionAnalyzer(llm)

    def route(self, message: str, session_id: str, state_mgr: DialogStateManager) -> tuple:
        emotion = self.emotion_analyzer.analyze(message)
        state_mgr.set_emotion(session_id, emotion)
        logger.info("emotion_detected", session_id=session_id, emotion=emotion)

        if emotion == "angry":
            logger.info("angry_user_suggest_human", session_id=session_id)
            return "human", 0.9, emotion

        prompt = f"""你是一个电商客服意图路由器。根据用户消息判断应该由哪个专业客服处理。

可选Agent：
- presale: 售前咨询、产品推荐、购买建议
- product: 产品知识、规格参数、使用方法
- order: 订单查询、物流追踪、订单状态
- coupon: 优惠券查询、优惠码验证、促销活动
- aftersale: 退款、换货、维修、售后投诉
- chitchat: 闲聊、打招呼、无关问题
- human: 需要人工客服处理的复杂问题

用户消息：{message}

请返回JSON格式：{{"agent": "agent名称", "confidence": 0.0-1.0, "reason": "路由原因"}}"""

        result = self.llm.chat_json([{"role": "user", "content": prompt}])
        agent = result.get("agent", "chitchat").lower()
        confidence = result.get("confidence", 0.0)
        reason = result.get("reason", "")

        if agent not in self.VALID_AGENTS or confidence < self.config.router_confidence_threshold:
            agent = "chitchat"
            confidence = 0.5
            reason = "低置信度降级到闲聊"

        logger.info("route_result", session_id=session_id, agent=agent, confidence=confidence, reason=reason, emotion=emotion)
        return agent, confidence, emotion
