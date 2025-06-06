MCP Client with Custom LLM API

项目简介

这是一个基于MCP协议(Multi-agent Collaboration Protocol)的客户端实现，核心功能是通过自定义大语言模型(LLM)API处理自然语言查询，并智能调用后端工具服务。项目使用Python 3.10+开发，通过uv环境管理依赖。

核心特性
自定义LLM API支持

可配置任何兼容OpenAI格式的API

通过llm_api/config.json设置API密钥和url

支持GPT-4o、Claude等主流大模型
MCP协议客户端

支持Python/Node.js工具服务器

动态获取可用工具列表

安全的工具调用机制
智能工具调度

自动将自然语言查询转为工具调用

强制遵循工具调用规范

单次调用限制确保执行效率

快速开始
配置LLM API (llm_api/config.json):

"api_key": "your_actual_api_key",

  "url": "https://your-llm-api-endpoint/v1/chat/completions"

安装依赖:

pip install httpx mcp requests

运行示例:

启动工具服务器

python server.py

启动MCP客户端 (另开终端)

python client.py path/to/server.py

核心代码概览

MCP客户端实现 (client.py)

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.llm = LLM()  # 自定义LLM实例
        self.messages = []  # 对话上下文

    async def connect_to_server(self, server_script_path: str):
        # 连接MCP服务器并初始化工具
        ...

    async def process_query(self, query: str) -> str:
        # 处理用户查询，调用LLM和工具
        ...
        
    async def chat_loop(self):
        # 交互式聊天循环
        ...

LLM API集成 (llm_api/api.py)

class LLM:
    def create_message(self, model: str, max_tokens: int, messages: list):
        # 调用自定义LLM API
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
response = requests.post(self.url, headers=self.headers, json=payload)

        return response.json()["choices"][0]["message"]["content"]

工具服务器示例 (server.py)

@mcp.tool()
async def get_alerts(state: str) -> str:
    # 获取天气警报（示例工具）
    ...

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    # 获取天气预报（示例工具）
    ...

注：天气服务工具仅用于验证客户端功能，实际应用中可替换为任何实现MCP协议的工具服务。
