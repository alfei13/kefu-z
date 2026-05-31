import pytest
from kefu_z.config import Config
from kefu_z.llm_client import LLMClient
from kefu_z.mcp_client import MCPClient
from kefu_z.conversation_memory import ConversationMemory
from kefu_z.dialog_state import DialogStateManager, DialogState
from kefu_z.agents.handoff import HandoffRequest
from kefu_z.agents.router_agent import RouterAgent, EmotionAnalyzer
from kefu_z.agents.presale_agent import PresaleAgent
from kefu_z.agents.chitchat_agent import ChitchatAgent
from kefu_z.agents.human_handoff_agent import HumanHandoffAgent
from kefu_z.gateway import Orchestrator


class TestConfig:
    def test_config_defaults(self):
        config = Config()
        assert config.dashscope_model == "qwen-plus"
        assert config.gradio_server_name == "127.0.0.1"
        assert config.max_react_rounds == 5
        assert config.max_handoff_rounds == 3
        assert config.router_confidence_threshold == 0.5


class TestConversationMemory:
    def test_add_and_get_messages(self):
        mem = ConversationMemory()
        mem.add_message("s1", "user", "hello")
        mem.add_message("s1", "assistant", "hi")
        msgs = mem.get_messages("s1")
        assert len(msgs) == 2
        assert msgs[0]["content"] == "hello"

    def test_recent_messages(self):
        mem = ConversationMemory(max_messages=5)
        for i in range(10):
            mem.add_message("s1", "user", f"msg{i}")
        recent = mem.get_recent_messages("s1", n=3)
        assert len(recent) == 3
        assert recent[-1]["content"] == "msg9"

    def test_context(self):
        mem = ConversationMemory()
        mem.set_context("s1", "user_id", 1)
        assert mem.get_context("s1", "user_id") == 1

    def test_clear_session(self):
        mem = ConversationMemory()
        mem.add_message("s1", "user", "hello")
        mem.clear_session("s1")
        assert len(mem.get_messages("s1")) == 0


class TestDialogStateManager:
    def test_create_state(self):
        mgr = DialogStateManager()
        state = mgr.get_or_create("s1", 1)
        assert state.user_id == 1
        assert state.dialog_phase == "greeting"

    def test_slots(self):
        mgr = DialogStateManager()
        mgr.get_or_create("s1", 1)
        mgr.set_slot("s1", "order_id", 123)
        assert mgr.get_slot("s1", "order_id") == 123
        missing = mgr.get_missing_slots("s1", ["order_id", "type"])
        assert missing == ["type"]

    def test_handoff(self):
        mgr = DialogStateManager()
        mgr.get_or_create("s1", 1)
        mgr.add_handoff("s1", "presale", "order", "user asked about order")
        state = mgr.get_or_create("s1")
        assert state.current_agent == "order"
        assert len(state.handoff_history) == 1

    def test_emotion(self):
        mgr = DialogStateManager()
        mgr.get_or_create("s1", 1)
        mgr.set_emotion("s1", "angry")
        state = mgr.get_or_create("s1")
        assert state.emotion == "angry"

    def test_pending_confirmation(self):
        mgr = DialogStateManager()
        mgr.get_or_create("s1", 1)
        mgr.set_pending_confirmation("s1", {"action": "create_aftersale", "params": {}})
        state = mgr.get_or_create("s1")
        assert state.dialog_phase == "confirming"
        assert state.pending_confirmation is not None
        mgr.clear_pending_confirmation("s1")
        state = mgr.get_or_create("s1")
        assert state.pending_confirmation is None


class TestMCPClient:
    def test_tools_definition(self):
        config = Config()
        mcp = MCPClient(config)
        tools = mcp.get_tools_definition()
        assert len(tools) == 8
        names = [t["function"]["name"] for t in tools]
        assert "search_products" in names
        assert "create_aftersale" in names


class TestHandoffRequest:
    def test_handoff_creation(self):
        h = HandoffRequest(target_agent="order", reason="test", context={"k": "v"})
        assert h.target_agent == "order"
        assert h.reason == "test"
        assert h.context == {"k": "v"}


class TestOrchestrator:
    def test_init(self):
        config = Config()
        orch = Orchestrator(config)
        assert len(orch.agents) == 7
        assert "presale" in orch.agents
        assert "human" in orch.agents
