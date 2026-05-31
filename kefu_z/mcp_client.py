import json
import structlog
import httpx
from kefu_z.config import Config

logger = structlog.get_logger(__name__)


class MCPClient:
    TOOL_MAP = {
        "search_products": {
            "method": "GET",
            "path": "/api/products/search",
            "param_map": {"query": "query", "category": "category"},
        },
        "get_product_detail": {
            "method": "GET",
            "path": "/api/products/{product_id}",
            "path_params": ["product_id"],
            "param_map": {},
        },
        "query_orders": {
            "method": "GET",
            "path": "/api/orders",
            "param_map": {"user_id": "userId", "status": "status"},
        },
        "get_order_detail": {
            "method": "GET",
            "path": "/api/orders/{order_id}",
            "path_params": ["order_id"],
            "param_map": {},
        },
        "query_coupons": {
            "method": "GET",
            "path": "/api/coupons",
            "param_map": {"user_id": "userId"},
        },
        "check_coupon": {
            "method": "GET",
            "path": "/api/coupons/{code}",
            "path_params": ["code"],
            "param_map": {},
        },
        "create_aftersale": {
            "method": "POST",
            "path": "/api/aftersale",
            "param_map": {},
        },
        "query_aftersale": {
            "method": "GET",
            "path": "/api/aftersale",
            "param_map": {"user_id": "userId", "order_id": "orderId"},
        },
    }

    def __init__(self, config: Config):
        self.base_url = config.mock_api_base.rstrip("/")
        self.client = httpx.Client(timeout=10.0)

    def call(self, tool_name: str, params: dict) -> dict:
        if tool_name not in self.TOOL_MAP:
            logger.error("mcp_unknown_tool", tool_name=tool_name)
            return {"error": f"Unknown tool: {tool_name}"}

        mapping = self.TOOL_MAP[tool_name]
        method = mapping["method"]
        path = mapping["path"]
        param_map = mapping.get("param_map", {})
        path_params = mapping.get("path_params", [])

        for pp in path_params:
            if pp in params:
                path = path.replace(f"{{{pp}}}", str(params[pp]))

        url = f"{self.base_url}{path}"

        try:
            if method == "GET":
                query_params = {}
                for src_key, dst_key in param_map.items():
                    if src_key in params and params[src_key] is not None:
                        query_params[dst_key] = params[src_key]
                logger.info("mcp_call", tool=tool_name, method=method, url=url, params=query_params)
                resp = self.client.get(url, params=query_params)
            elif method == "POST":
                logger.info("mcp_call", tool=tool_name, method=method, url=url, body=params)
                resp = self.client.post(url, json=params)
            elif method == "PUT":
                logger.info("mcp_call", tool=tool_name, method=method, url=url, body=params)
                resp = self.client.put(url, json=params)
            else:
                return {"error": f"Unsupported method: {method}"}

            if resp.status_code == 404:
                logger.warning("mcp_not_found", tool=tool_name, url=url)
                return {"error": "Resource not found"}
            resp.raise_for_status()
            result = resp.json()
            logger.info("mcp_call_success", tool=tool_name, status=resp.status_code)
            return result
        except httpx.HTTPStatusError as e:
            logger.error("mcp_http_error", tool=tool_name, status=e.response.status_code)
            return {"error": f"HTTP {e.response.status_code}", "detail": str(e)}
        except Exception as e:
            logger.error("mcp_call_failed", tool=tool_name, error=str(e))
            return {"error": "MCP call failed", "detail": str(e)}

    def get_tools_definition(self) -> list:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_products",
                    "description": "搜索商品，根据关键词或分类查找匹配的商品列表",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "搜索关键词"},
                            "category": {"type": "string", "description": "商品分类，如：手机、电脑、耳机"},
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_product_detail",
                    "description": "获取商品详细信息，包括规格参数、库存、价格等",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "integer", "description": "商品ID"},
                        },
                        "required": ["product_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "query_orders",
                    "description": "查询用户订单列表，可按状态筛选",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "integer", "description": "用户ID"},
                            "status": {"type": "string", "description": "订单状态筛选：pending/paid/shipped/delivered/cancelled"},
                        },
                        "required": ["user_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_order_detail",
                    "description": "获取订单详情，包括物流信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {"type": "integer", "description": "订单ID"},
                        },
                        "required": ["order_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "query_coupons",
                    "description": "查询用户可用的优惠券列表",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "integer", "description": "用户ID"},
                        },
                        "required": ["user_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "check_coupon",
                    "description": "验证优惠码是否有效",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "优惠码"},
                        },
                        "required": ["code"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "create_aftersale",
                    "description": "创建售后申请（退款/换货/维修），需要用户确认",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {"type": "integer", "description": "订单ID"},
                            "user_id": {"type": "integer", "description": "用户ID"},
                            "type": {"type": "string", "enum": ["refund", "exchange", "repair"], "description": "售后类型"},
                            "reason": {"type": "string", "description": "申请原因"},
                        },
                        "required": ["order_id", "user_id", "type", "reason"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "query_aftersale",
                    "description": "查询售后申请进度",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {"type": "integer", "description": "订单ID"},
                        },
                        "required": ["order_id"],
                    },
                },
            },
        ]
