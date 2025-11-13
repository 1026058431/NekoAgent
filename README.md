# 🐱 NekoAgent - 多角色AI助手框架

## 🌟 项目简介

NekoAgent是一个基于Langchain的多角色AI助手框架，支持多种AI模型和角色切换，提供完整的工具生态系统。

### 💫 核心特性

- **🎭 多角色支持** - 预置多种AI角色，支持自定义角色
- **🤖 多模型切换** - DeepSeek、Ollama、Qwen等模型支持
- **🛠️ 完整工具生态** - 文件操作、Web请求、RAG、MCP等
- **⚙️ 模块化架构** - 清晰的代码结构，易于扩展和维护
- **🧵 线程管理** - 多会话线程支持，保持对话上下文

## 🎯 快速开始

### 环境要求
- Python 3.10+
- 支持的AI模型API密钥或本地部署

### 安装步骤

1. **克隆项目**
```bash
git clone <项目地址>
cd NekoAgent
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
创建 `.env` 文件并配置模型API密钥：
```env
DEEPSEEK_API_KEY=your_deepseek_key
OLLAMA_BASE_URL=http://localhost:11434
```

4. **启动应用**
```bash
python -m Agents.Agent
```

## 🎭 角色系统

### 预置角色

#### 🤖 **AI** - 理性专业助手
- 基于事实和逻辑的推理
- 标准化、结构化的回答
- 专注于问题解决

#### 🐱 **Neko** - 温暖陪伴助手  
- 人性化的交流方式
- 温暖耐心的指导态度
- 展现真实的思考和情感

#### 👤 **UserSim** - 用户模拟助手
- 从用户视角体验系统
- 模拟真实用户行为
- 提供用户反馈和建议

### 角色切换

在交互界面中使用命令切换角色：
```
/role          # 显示角色选择菜单
/role switch AI    # 切换到AI角色
/role switch Neko  # 切换到Neko角色
```

## 🤖 模型支持

### 支持的模型
- **DeepSeek** - 在线API模型
- **Ollama** - 本地部署模型
- **Qwen** - 通过Ollama本地部署的通义千问系列模型

### 模型切换

在交互界面中使用命令切换模型：
```
/model          # 显示模型选择菜单
/model switch deepseek  # 切换到DeepSeek
/model switch ollama    # 切换到Ollama
```

## 🛠️ 工具系统

### 核心工具类别

- **📁 文件操作** - 读取、写入、移动、删除文件
- **🌐 Web请求** - HTTP客户端、Payload发送
- **🔍 RAG系统** - 知识库检索和问答
- **🔧 MCP工具** - 模型上下文协议工具管理
- **📊 报告生成** - 模板化报告生成

### 文件操作权限说明

#### 📖 读取权限
- **允许**：读取项目范围内的所有文件
- **路径**：相对于项目根目录的相对路径
- **示例**：`read_file("Sandbox/test.txt")`、`read_file("Agents/Agent.py")`

#### ✏️ 写入权限
- **限制**：只能在 `Sandbox/` 目录下写入文件
- **路径**：必须以 `Sandbox/` 开头
- **示例**：`write_file("Sandbox/test.txt", "内容")` ✅
- **错误**：`write_file("Agents/test.py", "内容")` ❌

#### 📂 目录浏览
- **允许**：浏览项目范围内的目录结构
- **路径**：相对于项目根目录的相对路径
- **示例**：`list_dir_tree("Sandbox")`、`list_dir_tree("Tools")`

#### 🗑️ 删除权限
- **限制**：只能在 `Sandbox/` 目录下删除文件
- **路径**：必须以 `Sandbox/` 开头
- **示例**：`delete_file("Sandbox/temp.txt")` ✅
- **错误**：`delete_file("Agents/temp.py")` ❌

#### 📦 移动权限
- **限制**：只能在 `Sandbox/` 目录内移动文件
- **路径**：源路径和目标路径都必须以 `Sandbox/` 开头
- **示例**：`move_file("Sandbox/old.txt", "Sandbox/new.txt")` ✅
- **错误**：`move_file("Sandbox/file.txt", "Agents/file.txt")` ❌

### 工具使用示例

```python
# 文件操作 - 正确示例
read_file("Sandbox/test.txt")                    # ✅ 读取沙盒文件
write_file("Sandbox/new_file.txt", "内容")       # ✅ 写入沙盒文件
list_dir_tree("Tools")                          # ✅ 浏览工具目录

# 文件操作 - 错误示例
write_file("Agents/test.py", "内容")             # ❌ 不能在项目目录写入
delete_file("Config/config.yaml")               # ❌ 不能删除配置文件
move_file("Sandbox/file.txt", "Data/file.txt")  # ❌ 不能移出沙盒
```

## 🔍 RAG知识库系统

### 功能特性

- **📚 多格式支持** - 支持PDF、TXT、Markdown等文档格式
- **🧠 智能检索** - 基于语义相似度的文档检索
- **🔄 动态更新** - 支持知识库的实时刷新和更新
- **🔧 配置灵活** - 支持多种嵌入模型和向量存储

### 使用方法

```python
# 基础检索
rag_search("查询问题", k=5)

# 智能问答
rag_query("问题", use_generator=True)

# 系统信息
rag_system_info()

# 刷新知识库
rag_refresh()
```

### 配置选项

- **嵌入模型**：支持OpenAI、Ollama等嵌入模型
- **检索数量**：可配置返回文档数量
- **生成答案**：可选是否使用生成器生成答案

### ⚠️ 重要依赖说明

#### RAG生成器模型依赖

**当前RAG生成器使用硬编码的Ollama模型**：

- **生成器默认模型**：`gpt-oss:20b`
- **嵌入模型默认**：`qwen3-embedding`

**使用前需要确保以下模型已下载**：

```bash
# 下载生成器使用的模型
ollama pull gpt-oss:20b

# 下载嵌入模型
ollama pull qwen3-embedding
```

#### 模型依赖关系

| 功能 | 默认模型 | 依赖说明 |
|------|----------|----------|
| RAG生成器 | `gpt-oss:20b` | 用于生成答案，需要手动下载 |
| Ollama嵌入 | `qwen3-embedding` | 用于语义检索，需要手动下载 |
| 默认嵌入 | ChromaDB内置 | 无需额外下载 |

#### 使用建议

1. **如果不想下载额外模型**：
   - 使用默认的ChromaDB内置嵌入
   - 禁用生成器功能（`use_generator=False`）

2. **如果需要更好的中文理解**：
   - 下载 `qwen3-embedding` 用于语义检索
   - 下载 `gpt-oss:20b` 或 `qwen3:30b` 用于生成答案

3. **模型不存在时的处理**：
   - 生成器会回退到默认提示
   - 嵌入模型会回退到ChromaDB内置

## 🔧 MCP工具系统

### 内置MCP服务器

NekoAgent内置了完整的MCP（Model Context Protocol）服务器 `SecureMCPServer`，支持动态工具创建和管理。

### 启动MCP服务器

```bash
# 启动内置MCP服务器
python -m Tools.MCP.mcp_server_http

# 默认地址：http://127.0.0.1:8000
# 可选参数：--port 端口号 --host 绑定地址
```

### MCP工具管理

#### 连接MCP服务器
```python
# 连接到MCP服务器
connect_mcp_server("http://127.0.0.1:8000")

# 获取服务器信息
get_mcp_server_info()

# 列出可用工具
list_mcp_tools()
```

#### 创建自定义MCP工具

**重要提示：创建MCP工具前必须先获取工具模板！**

```python
# 1. 获取MCP工具模板要求
# 使用 get_mcp_tools_path_info() 查看模板要求
# 或调用MCP服务器中的 get_mcp_template 工具

# 2. 创建符合模板的工具
create_mcp_tool(
    tool_name="my_tool",
    tool_code="""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mcp.server.fastmcp import FastMCP

# 创建MCP实例
mcp = FastMCP("my_tool")

@mcp.tool()
async def my_tool_function(text: str) -> str:
    \"\"\"工具描述\"\"\"
    return f"处理结果: {text}"

def register_tools(mcp_instance):
    \"\"\"注册工具到MCP服务器\"\"\"
    mcp_instance.add_tool(my_tool_function, name="my_tool_function")

print(f"🐱 MCP工具 'my_tool' 加载完成")
""",
    description="我的自定义工具"
)
```

#### MCP工具模板要求

MCP工具必须遵循特定的格式才能正确加载：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🐱 MCP工具模板

必须包含 register_tools 函数，使用 @mcp.tool() 装饰器
"""

from mcp.server.fastmcp import FastMCP

# 创建MCP实例
mcp = FastMCP("tool_name")


@mcp.tool()
async def tool_function(param1: str, param2: int = 0) -> dict:
    """
    工具功能描述
    
    Args:
        param1: 参数1说明
        param2: 参数2说明，默认值
        
    Returns:
        dict: 返回结果
    """
    try:
        # 工具实现逻辑
        result = {
            "success": True,
            "result": f"处理完成: {param1}, {param2}"
        }
        return result
        
    except Exception:
        return {"error": "操作失败"}


# 🎯 必须包含的注册函数
def register_tools(mcp_instance):
    """注册工具到MCP服务器"""
    mcp_instance.add_tool(tool_function, name="tool_function")


print(f"🐱 MCP工具 'tool_name' 加载完成")
```

#### 工具安全检查

```python
# 在创建工具前进行安全检查
scan_mcp_tool_security(tool_code)

# 列出本地工具文件
list_mcp_tools_local()

# 删除工具文件
delete_mcp_tool("tool_name")
```

### MCP工具调用

```python
# 调用MCP工具
call_mcp_tool(
    tool_name="echo",
    tool_args={"text": "Hello World"}
)

# 注意：所有参数必须通过tool_args字典传递
```

## ⚙️ 配置管理

### 配置文件
项目使用 `Config/agent_config.yaml` 进行配置管理：

```yaml
agent:
  middleware:
    summarization:
      enabled: true
    context_editing:
      enabled: true
    approval:
      enabled: true
  
  checkpointer:
    default: "SQLite"
    
  performance:
    recursion_limit: 300
    stream_mode: "messages"
```

### 中间件配置
- **总结中间件** - 自动总结长对话
- **上下文编辑** - 清理工具调用历史
- **审批中间件** - 敏感操作审批机制

## 🧵 线程管理

### 线程操作

```
/thread          # 显示当前线程
/thread list     # 列出最近线程
/thread switch   # 切换到默认线程
/thread reset    # 安全重置当前线程
```

### 线程特性
- 每个线程保持独立的对话上下文
- 支持自定义线程名称
- 线程间快速切换
- 安全删除机制

## 🚀 高级功能

### 自定义角色
在 `Sandbox/Prompt/` 目录下创建角色文件：

```yaml
# Role_MyRole.yaml
# 🎭 MyRole - 自定义角色

## 角色设定
我是一个自定义AI助手...

## 核心特点
- 特点1
- 特点2
- 特点3
```

### 报告模板系统

- 预置多种报告模板
- 支持自定义模板
- 模板化内容生成

## 📁 项目结构

```
NekoAgent/
├── Agents/           # Agent核心系统
├── Config/           # 配置管理
├── Data/             # 数据存储
├── Tools/            # 工具生态系统
│   ├── MCP/          # MCP工具系统
│   └── RAG/          # RAG知识库系统
├── Sandbox/          # 沙盒环境
│   └── Prompt/       # 角色提示词
└── requirements.txt  # 依赖列表
```

## 🔧 开发指南

### 添加新工具
在 `Tools/` 目录下创建工具模块：

```python
# Tools/MyTool/my_tool.py
from langchain.tools import tool

@tool
def my_custom_tool(input: str) -> str:
    """工具描述"""
    return "处理结果"
```

### 添加新角色
在 `Sandbox/Prompt/` 目录创建YAML文件：

```yaml
# Role_NewRole.yaml
# 🎭 NewRole - 新角色

## 角色设定
我是一个新的AI助手角色...
```

## 🐛 故障排除

### 常见问题

1. **模型连接失败**
   - 检查API密钥配置
   - 验证网络连接
   - 确认模型服务状态

2. **工具调用错误**
   - 检查文件权限
   - 验证工具配置
   - 查看错误日志

3. **角色切换无效**
   - 确认角色文件存在
   - 检查文件路径配置
   - 验证YAML格式

4. **MCP工具创建失败**
   - 确认工具格式符合模板要求
   - 检查是否包含register_tools函数
   - 使用安全检查功能

5. **文件操作权限错误**
   - 写入操作必须在Sandbox目录下
   - 删除操作必须在Sandbox目录下
   - 移动操作必须在Sandbox目录内

6. **RAG生成器失败**
   - 确认Ollama服务已启动
   - 检查 `gpt-oss:20b` 模型是否已下载
   - 检查 `qwen3-embedding` 模型是否已下载（如果使用Ollama嵌入）

### 日志查看

项目日志位于 `Agents/Modular/agent.log`

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境设置

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

MIT License

## 🙏 致谢

感谢所有贡献者和用户的支持！

---

**🐱 NekoAgent - 在专业服务中展现温暖陪伴！**