# 模型上下文协议 (MCP)

Model Context Protocol (MCP) 是一个开放协议，标准化了应用程序如何向LLM提供工具和上下文。LangChain智能体可以使用 `langchain-mcp-adapters` 库来使用MCP服务器上定义的工具。

## 安装

安装 `langchain-mcp-adapters` 库以在LangGraph中使用MCP工具：

```bash
pip install langchain-mcp-adapters
```

## 传输类型

MCP支持不同的传输机制用于客户端-服务器通信：

- **stdio** - 客户端将服务器作为子进程启动，通过标准输入/输出进行通信。适用于本地工具和简单设置。
- **Streamable HTTP** - 服务器作为独立进程运行，处理HTTP请求。支持远程连接和多个客户端。
- **Server-Sent Events (SSE)** - 流式HTTP的变体，针对实时流式通信进行了优化。

## 使用MCP工具

`langchain-mcp-adapters` 使智能体能够使用一个或多个MCP服务器上定义的工具。

### 访问多个MCP服务器

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

client = MultiServerMCPClient(
    {
        "math": {
            "transport": "stdio",  # 本地子进程通信
            "command": "python",   # 你的math_server.py文件的绝对路径
            "args": ["/path/to/math_server.py"],
        },
        "weather": {
            "transport": "streamable_http",  # 基于HTTP的远程服务器
            # 确保你的天气服务器在端口8000上启动
            "url": "http://localhost:8000/mcp",
        }
    }
)

tools = await client.get_tools()
agent = create_agent(
    "claude-sonnet-4-5-20250929",
    tools
)

math_response = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
)

weather_response = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
)
```

`MultiServerMCPClient` 默认是无状态的。每个工具调用都会创建一个新的MCP ClientSession，执行工具，然后进行清理。

## 自定义MCP服务器

要创建自己的MCP服务器，可以使用 `mcp` 库。该库提供了一种简单的方法来定义工具并将其作为服务器运行。

```bash
pip install mcp
```

使用以下参考实现来测试你的智能体与MCP工具服务器的交互。

### 数学服务器（stdio传输）

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 天气服务器（streamable HTTP传输）

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return "It's always sunny in New York"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

## 有状态工具使用

对于需要在工具调用之间维护上下文的有状态服务器，使用 `client.session()` 创建一个持久的ClientSession。

### 使用MCP ClientSession进行有状态工具使用

```python
from langchain_mcp_adapters.tools import load_mcp_tools

client = MultiServerMCPClient({...})

async with client.session("math") as session:
    tools = await load_mcp_tools(session)
```

## 附加资源

- [MCP文档](https://modelcontextprotocol.io/docs)
- [MCP传输文档](https://modelcontextprotocol.io/docs/transports)
- [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters)---

**原始文档URL**: https://docs.langchain.com/oss/python/langchain/mcp