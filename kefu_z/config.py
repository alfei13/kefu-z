import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    dashscope_api_key: str = ""
    dashscope_api_base: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    dashscope_model: str = "qwen-plus"
    mock_api_base: str = "http://localhost:8080"
    gradio_server_name: str = "127.0.0.1"
    gradio_server_port: int = 7860
    max_react_rounds: int = 5
    max_handoff_rounds: int = 3
    session_ttl_seconds: int = 3600
    max_messages_per_session: int = 100
    max_sessions: int = 1000
    router_confidence_threshold: float = 0.5

    def __post_init__(self):
        self.dashscope_api_key = os.getenv("DASHSCOPE_API_KEY", self.dashscope_api_key)
        self.mock_api_base = os.getenv("MOCK_API_BASE", self.mock_api_base)
        self.gradio_server_name = os.getenv("GRADIO_SERVER_NAME", self.gradio_server_name)
        self.gradio_server_port = int(os.getenv("GRADIO_SERVER_PORT", self.gradio_server_port))
