import json
from abc import ABC, abstractmethod
from kefu_z.llm_client import LLMClient
from kefu_z.mcp_client import MCPClient
from kefu_z.conversation_memory import ConversationMemory
from kefu_z.dialog_state import DialogStateManager
from kefu_z.agents.handoff import HandoffRequest
from kefu_z.config import Config
import structlog

logger = structlog.get_logger(__name__)


class BaseAgent(ABC):
    def __init__(
        self,
        name: str,
        llm: LLMClient,
        mcp: MCPClient,
        memory: ConversationMemory,
        state_mgr: DialogStateManager,
        config: Config,
        tool_names: list[str] | None = None,
        system_prompt: str = "",
    ):
        self.name = name
        self.llm = llm
        self.mcp = mcp
        self.memory = memory
        self.state_mgr = state_mgr
        self.config = config
        self.tool_names = tool_names or []
        self.system_prompt = system_prompt
        self._tools_def = None

    def _get_tools(self) -> list:
        if self._tools_def is None:
            all_tools = self.mcp.get_tools_definition()
            if self.tool_names:
                self._tools_def = [
                    t for t in all_tools
                    if t["function"]["name"] in self.tool_names
                ]
            else:
                self._tools_def = []
        return self._tools_def

    @abstractmethod
    def process(self, message: str, session_id: str) -> str | HandoffRequest:
        pass

    def _react_loop(self, message: str, session_id: str) -> str | HandoffRequest:
        tools = self._get_tools()
        history = self.memory.get_recent_messages(session_id, n=10)

        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        self.memory.add_message(session_id, "user", message)
        self.state_mgr.update_phase(session_id, "executing")

        max_rounds = self.config.max_react_rounds
        for round_num in range(max_rounds):
            logger.info(
                "react_round",
                agent=self.name,
                session_id=session_id,
                round=round_num + 1,
                max=max_rounds,
            )

            if tools:
                reply_text, tool_calls = self.llm.chat_with_tools(messages, tools)
            else:
                reply_text = self.llm.chat(messages)
                tool_calls = []

            handoff = self._check_handoff(reply_text, session_id)
            if handoff:
                return handoff

            if not tool_calls:
                self.memory.add_message(session_id, "assistant", reply_text)
                return reply_text

            messages.append({
                "role": "assistant",
                "content": reply_text,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tool_calls
                ],
            })

            for tc in tool_calls:
                tool_name = tc.function.name
                try:
                    tool_args = json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments
                except json.JSONDecodeError:
                    tool_args = {}

                state = self.state_mgr.get_or_create(session_id)
                if state.user_id and tool_name in ["query_orders", "query_coupons", "create_aftersale", "query_aftersale"]:
                    tool_args["user_id"] = state.user_id

                logger.info("tool_call", agent=self.name, tool=tool_name, args=tool_args)
                result = self.mcp.call(tool_name, tool_args)
                result_str = json.dumps(result, ensure_ascii=False)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_str,
                })

        final_reply = self.llm.chat(messages)
        self.memory.add_message(session_id, "assistant", final_reply)
        return final_reply

    def _check_handoff(self, text: str, session_id: str) -> HandoffRequest | None:
        handoff_markers = ["[HANDOFF:", "[转交:"]
        for marker in handoff_markers:
            if marker in text:
                try:
                    start = text.index(marker) + len(marker)
                    end = text.index("]", start)
                    target = text[start:end].strip().lower()
                    valid_targets = ["presale", "product", "order", "coupon", "aftersale", "chitchat", "human"]
                    if target in valid_targets:
                        logger.info("handoff_detected", agent=self.name, target=target, session_id=session_id)
                        return HandoffRequest(
                            target_agent=target,
                            reason=f"Agent {self.name} requested handoff to {target}",
                            context={"source_agent": self.name},
                            original_message=text,
                        )
                except (ValueError, IndexError):
                    pass
        return None

    def _simple_chat(self, message: str, session_id: str) -> str:
        history = self.memory.get_recent_messages(session_id, n=10)
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        self.memory.add_message(session_id, "user", message)
        reply = self.llm.chat(messages)
        self.memory.add_message(session_id, "assistant", reply)
        return reply
