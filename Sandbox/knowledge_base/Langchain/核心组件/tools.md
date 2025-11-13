# LangChain 工具

## 工具概述

工具是智能体用来与外部世界交互的函数。它们允许智能体执行搜索、计算、数据检索等操作。

## 创建工具

### 基础工具创建

```python
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

@tool
def calculate_math(expression: str) -> str:
    """Calculate mathematical expressions."""
    return str(eval(expression))
```

### 带上下文的工具

```python
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime

@dataclass
class Context:
    user_id: str

@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Retrieve user information based on user ID."""
    user_id = runtime.context.user_id
    return "Florida" if user_id == "1" else "SF"
```

### 异步工具

```python
import asyncio
from langchain.tools import tool

@tool
async def async_search(query: str) -> str:
    """Asynchronously search for information."""
    await asyncio.sleep(1)  # 模拟异步操作
    return f"Async search results for: {query}"
```

## 工具类型

### 1. 内置工具

LangChain 提供了许多内置工具：

```python
from langchain.tools import DuckDuckGoSearchRun, WikipediaQueryRun

search_tool = DuckDuckGoSearchRun()
wiki_tool = WikipediaQueryRun()
```

### 2. 自定义工具

创建特定于应用程序的工具：

```python
@tool
def database_query(sql: str) -> str:
    """Execute SQL query on database."""
    # 实现数据库查询逻辑
    return "Query results"

@tool
def api_call(endpoint: str, data: dict) -> str:
    """Make API call to external service."""
    # 实现API调用逻辑
    return "API response"
```

### 3. 多参数工具

```python
@tool
def complex_tool(param1: str, param2: int, param3: bool = False) -> str:
    """
    A complex tool with multiple parameters.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        param3: Description of param3
    """
    return f"Result: {param1}, {param2}, {param3}"
```
## 工具集成模式

### 1. 外部API集成

```python
import requests

@tool
def external_api_call(api_endpoint: str, payload: dict) -> str:
    """Call external API and return response."""
    try:
        response = requests.post(api_endpoint, json=payload, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"API call failed: {str(e)}"
```

### 2. 数据库集成

```python
import sqlite3

@tool
def database_operation(query_type: str, data: dict) -> str:
    """Perform database operations."""
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    try:
        if query_type == "insert":
            cursor.execute("INSERT INTO users VALUES (?, ?)", (data['name'], data['email']))
            conn.commit()
            return "Insert successful"
        elif query_type == "select":
            cursor.execute("SELECT * FROM users WHERE name = ?", (data['name'],))
            result = cursor.fetchall()
            return str(result)
    finally:
        conn.close()
```

### 3. 文件系统集成

```python
import os
import json

@tool
def file_operation(operation: str, filename: str, content: str = "") -> str:
    """Perform file system operations."""
    try:
        if operation == "read":
            with open(filename, 'r') as f:
                return f.read()
        elif operation == "write":
            with open(filename, 'w') as f:
                f.write(content)
            return "Write successful"
        elif operation == "list":
            files = os.listdir('.')
            return json.dumps(files)
    except Exception as e:
        return f"File operation failed: {str(e)}"
```

## 工具性能优化

### 1. 异步工具

```python
import asyncio
import aiohttp

@tool
async def async_api_call(url: str) -> str:
    """Make asynchronous API call."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```

### 2. 并行处理

```python
import concurrent.futures

@tool
def parallel_processing(tasks: List[str]) -> str:
    """Process tasks in parallel."""
    def process_task(task):
        return f"Processed: {task}"
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(process_task, tasks))
    
    return "\n".join(results)
```

### 3. 缓存策略

```python
from functools import lru_cache
from datetime import datetime, timedelta

class TimeBasedCache:
    def __init__(self, ttl_seconds=300):
        self.ttl = ttl_seconds
        self._cache = {}
    
    def get(self, key):
        if key in self._cache:
            value, timestamp = self._cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key, value):
        self._cache[key] = (value, datetime.now())

cache = TimeBasedCache()

@tool
def cached_expensive_operation(query: str) -> str:
    """Expensive operation with time-based caching."""
    cached_result = cache.get(query)
    if cached_result:
        return f"Cached: {cached_result}"
    
    # 模拟耗时操作
    result = f"Expensive result for: {query}"
    cache.set(query, result)
    return result
```
## 工具测试和验证

### 单元测试

```python
import unittest

class TestTools(unittest.TestCase):
    def test_weather_tool(self):
        result = get_weather("Paris")
        self.assertIn("Paris", result)
    
    def test_math_tool(self):
        result = calculate_math("2 + 2")
        self.assertEqual(result, "4")

if __name__ == "__main__":
    unittest.main()
```

### 集成测试

```python
def test_tool_in_agent():
    """Test tool functionality within an agent."""
    agent = create_agent(
        model="claude-sonnet-4-5-20250929",
        tools=[get_weather, calculate_math],
        system_prompt="Test agent"
    )
    
    response = agent.invoke({
        "messages": [{"role": "user", "content": "What's 5 * 5?"}]
    })
    
    assert "25" in str(response)
    print("Tool integration test passed!")
```

## 工具部署和监控

### 1. 日志记录

```python
import logging

logger = logging.getLogger(__name__)

@tool
def logged_tool(input_data: str) -> str:
    """A tool with comprehensive logging."""
    logger.info(f"Tool called with input: {input_data}")
    
    try:
        result = process_data(input_data)
        logger.info(f"Tool completed successfully")
        return result
    except Exception as e:
        logger.error(f"Tool failed: {str(e)}")
        return f"Error: {str(e)}"
```

### 2. 指标收集

```python
from prometheus_client import Counter, Histogram

TOOL_CALLS = Counter('tool_calls_total', 'Total tool calls', ['tool_name'])
TOOL_DURATION = Histogram('tool_duration_seconds', 'Tool execution duration', ['tool_name'])

@tool
def monitored_tool(input_data: str) -> str:
    """A tool with metrics collection."""
    TOOL_CALLS.labels(tool_name='monitored_tool').inc()
    
    with TOOL_DURATION.labels(tool_name='monitored_tool').time():
        result = process_data(input_data)
    
    return result
```

### 3. 健康检查

```python
@tool
def health_check() -> str:
    """Check the health of external dependencies."""
    checks = []
    
    # 检查数据库连接
    try:
        conn = sqlite3.connect('app.db')
        conn.close()
        checks.append("Database: OK")
    except Exception as e:
        checks.append(f"Database: FAILED - {str(e)}")
    
    # 检查API端点
    try:
        response = requests.get('https://api.example.com/health', timeout=5)
        if response.status_code == 200:
            checks.append("API: OK")
        else:
            checks.append(f"API: FAILED - Status {response.status_code}")
    except Exception as e:
        checks.append(f"API: FAILED - {str(e)}")
    
    return "\n".join(checks)
```

## 最佳实践

### 1. 错误处理

```python
@tool
def robust_tool(input_data: str) -> str:
    """A tool with comprehensive error handling."""
    try:
        # 输入验证
        if not input_data or len(input_data) > 1000:
            return "Error: Invalid input"
        
        # 业务逻辑
        result = process_data(input_data)
        
        # 输出验证
        if not result:
            return "Error: No result generated"
            
        return result
        
    except ValueError as e:
        return f"Validation error: {str(e)}"
    except ConnectionError as e:
        return f"Connection error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
```

### 2. 性能优化

```python
import time

@tool
def optimized_tool(input_data: str) -> str:
    """A tool with performance optimizations."""
    start_time = time.time()
    
    # 预处理
    processed_input = input_data.strip().lower()
    
    # 缓存检查
    cached_result = cache.get(processed_input)
    if cached_result:
        return cached_result
    
    # 业务逻辑
    result = expensive_operation(processed_input)
    
    # 缓存结果
    cache.set(processed_input, result)
    
    execution_time = time.time() - start_time
    logger.info(f"Tool execution time: {execution_time:.2f}s")
    
    return result
```

### 3. 安全性

```python
import re

@tool
def safe_tool(input_data: str) -> str:
    """A tool with security measures."""
    # 输入清理
    cleaned_input = re.sub(r'[^a-zA-Z0-9\s]', '', input_data)
    
    # 长度限制
    if len(cleaned_input) > 100:
        return "Error: Input too long"
    
    # SQL注入防护
    if any(keyword in cleaned_input.upper() for keyword in ['DROP', 'DELETE', 'UPDATE']):
        return "Error: Suspicious input detected"
    
    return process_safe_data(cleaned_input)
```
## 实际应用示例

### 1. 完整智能体示例

```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Search results for: {query}"

@tool
def calculate_math(expression: str) -> str:
    """Calculate mathematical expressions."""
    return str(eval(expression))

@tool
def get_time() -> str:
    """Get current time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 创建智能体
agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[search_web, calculate_math, get_time],
    system_prompt="You are a helpful assistant with access to various tools."
)

# 使用智能体
response = agent.invoke({
    "messages": [{"role": "user", "content": "What's 15 * 25 and what time is it?"}]
})
print(response)
```

### 2. 企业级工具示例

```python
import requests
import json
from typing import Dict, Any

@tool
def customer_lookup(customer_id: str) -> str:
    """Look up customer information by ID."""
    try:
        response = requests.get(
            f"https://api.company.com/customers/{customer_id}",
            headers={"Authorization": "Bearer YOUR_API_KEY"},
            timeout=10
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        return f"Customer lookup failed: {str(e)}"

@tool
def order_status(order_id: str) -> str:
    """Check order status by order ID."""
    try:
        response = requests.get(
            f"https://api.company.com/orders/{order_id}",
            headers={"Authorization": "Bearer YOUR_API_KEY"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return f"Order {order_id}: {data['status']}"
    except Exception as e:
        return f"Order status check failed: {str(e)}"

@tool
def inventory_check(product_id: str) -> str:
    """Check product inventory levels."""
    try:
        response = requests.get(
            f"https://api.company.com/inventory/{product_id}",
            headers={"Authorization": "Bearer YOUR_API_KEY"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return f"Product {product_id}: {data['quantity']} in stock"
    except Exception as e:
        return f"Inventory check failed: {str(e)}"
```

## 故障排除

### 常见问题

1. **工具不被调用**
   - 检查工具描述是否清晰
   - 验证工具参数类型是否正确
   - 确保智能体有足够的上下文

2. **工具执行失败**
   - 添加适当的错误处理
   - 检查外部依赖是否可用
   - 验证输入数据格式

3. **性能问题**
   - 实现缓存机制
   - 使用异步工具
   - 优化工具逻辑

### 调试技巧

```python
# 启用调试日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 工具调用跟踪
@tool
def debug_tool(input_data: str) -> str:
    """A tool with debug information."""
    print(f"Tool called with: {input_data}")
    result = process_data(input_data)
    print(f"Tool returned: {result}")
    return result
```

## 总结

LangChain 工具提供了强大的扩展能力，让智能体能够与外部系统交互。通过合理的设计和优化，可以创建出高效、可靠的工具系统。

### 关键要点

- ✅ **清晰的文档**: 工具描述要准确清晰
- ✅ **错误处理**: 完善的异常处理机制
- ✅ **性能优化**: 缓存、异步、并行处理
- ✅ **安全性**: 输入验证和清理
- ✅ **监控**: 日志记录和指标收集
- ✅ **测试**: 单元测试和集成测试

### 下一步

- 探索 LangGraph 进行复杂工作流编排
- 学习记忆管理以保持对话状态
- 了解结构化输出以处理复杂数据
- 研究多智能体协作模式

---

*专业 AI 工具开发指南* 🛠️
---
**原始文档URL**: https://docs.langchain.com/oss/python/langchain/tools