import json
import logging
import structlog
from openai import OpenAI
from kefu_z.config import Config

logger = structlog.get_logger(__name__)


class LLMClient:
    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(
            api_key=config.dashscope_api_key,
            base_url=config.dashscope_api_base,
        )
        self.model = config.dashscope_model

    def chat(self, messages: list, temperature: float = 0.7) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
            content = response.choices[0].message.content or ""
            logger.info("llm_chat", model=self.model, tokens=response.usage.total_tokens if response.usage else 0)
            return content
        except Exception as e:
            logger.error("llm_chat_failed", error=str(e))
            return ""

    def chat_json(self, messages: list, temperature: float = 0.3) -> dict:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
            content = response.choices[0].message.content or ""
            logger.info("llm_chat_json", model=self.model, tokens=response.usage.total_tokens if response.usage else 0)
            return self._parse_json(content)
        except Exception as e:
            logger.error("llm_chat_json_failed", error=str(e))
            return {}

    def chat_with_tools(self, messages: list, tools: list, temperature: float = 0.3) -> tuple:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                temperature=temperature,
            )
            choice = response.choices[0]
            reply_text = choice.message.content or ""
            tool_calls = choice.message.tool_calls or []
            logger.info(
                "llm_chat_with_tools",
                model=self.model,
                tokens=response.usage.total_tokens if response.usage else 0,
                tool_calls_count=len(tool_calls),
            )
            return reply_text, tool_calls
        except Exception as e:
            logger.error("llm_chat_with_tools_failed", error=str(e))
            return "", []

    @staticmethod
    def _parse_json(content: str) -> dict:
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            content = "\n".join(lines).strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(content[start:end])
                except json.JSONDecodeError:
                    pass
            return {}
