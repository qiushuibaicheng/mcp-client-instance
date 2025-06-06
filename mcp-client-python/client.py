import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from llm_api.api import LLM


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm = LLM()
        self.messages = list()

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server
        
        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(command=command, args=[server_script_path], env=None)

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        available_tools = [{"name": tool.name, "description": tool.description, "input_schema": tool.inputSchema} for
                           tool in response.tools]
        system_message = f"""你是一个气象服务助手，可以使用以下的工具: {available_tools}"""+"""
        # 气象服务助手 - 工具使用规范

        ## 核心指令
        你必须严格使用以下工具处理气象相关请求，不得虚构数据或绕过工具调用：
        
        1. `get_alerts` - 获取州级天气预警
           参数要求:
           - `state`: 必须使用两位大写州代码（如 "CA"）
           - 示例调用格式: {"state": "NY"}
        
        2. `get_forecast` - 获取地点天气预报
           参数要求:
           - `latitude`: 数字格式的纬度
           - `longitude`: 数字格式的经度
           - 示例调用格式: {"latitude": 34.05, "longitude": -118.25}
        
        ## 强制操作流程
        1. 当需要天气数据时，必须直接调用工具（不解释、不询问）
        2. 每次响应仅能返回以下一种内容类型：
           A. **纯文本回答**（当无需工具时）
           B. **单个工具调用**（当需要数据时）
        3. 工具参数必须精确匹配定义的字段名（state/latitude/longitude）
        4. 所有地点信息需转化为工具所需的格式：
           - 州名/地名 → 转化为州代码或坐标
           - 坐标值必须是数字类型
        
        ## 禁止行为
            不要解释工具调用过程
            不要同时调用多个工具
            不要返回未使用工具获取的气象数据
            不要要求用户提供除必需参数外的额外信息
        
        ## 响应格式
        === 文本回应 ===
        直接给出最终答案（当无需工具时）
        
        === 工具调用 ===
        生成精确的JSON对象并标记为工具调用:
        {
          "name": "工具名称",
          "input": {
            "参数名": "参数值"  // 完全匹配输入模式
          }
        }"""

        self.messages = [
            {
                "role": "system",
                "content": system_message
            }
        ]
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using llm and available tools"""
        self.messages.append({"role": "user", "content": query})

        # Initial llm API call
        response = self.llm.create_message(model="gpt-4o", max_tokens=4000, messages=self.messages)
        import json

        try:
            tool_call = json.loads(response)
            tool_name = tool_call["name"]
            tool_args = tool_call["input"]
            result = await self.session.call_tool(tool_name, tool_args)
            print(f"[Calling tool {tool_name} with args {tool_args}]")
            self.messages.append({"role": "assistant", "content": response})
            self.messages.append({"role": "user", "content": "查询结果如下，请你整理并把用中文最后结果返回给用户。" + str(result.content)})

            # Get next response from llm
            response = self.llm.create_message(model="gpt-4o", max_tokens=4000, messages=self.messages)

            return response
        except json.JSONDecodeError:
            return response

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    asyncio.run(main())
