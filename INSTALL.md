# 🐱 NekoAgent 安装指南

## 📋 系统要求

### 基础要求
- **Python**: 3.10 或更高版本
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **内存**: 至少 8GB RAM（推荐 16GB+）
- **存储**: 至少 10GB 可用空间

### 可选要求（用于本地模型）
- **GPU**: 支持 CUDA 的 NVIDIA GPU（可选，用于加速）
- **Ollama**: 用于本地模型部署

## 🚀 快速安装

### 1. 克隆项目
```bash
git clone <项目地址>
cd NekoAgent
```

### 2. 创建虚拟环境（推荐）
```bash
# 使用 conda
conda create -n nekoagent python=3.10
conda activate nekoagent

# 或使用 venv
python -m venv nekoenv
# Windows
nekoenv\Scripts\activate
# Linux/macOS
source nekoenv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt

# 国内推荐使用镜像源加速
pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/
```
### 4. 配置环境变量
创建 `.env` 文件：
```bash
# Windows
copy .env.example .env
# Linux/macOS
cp .env.example .env
```

编辑 `.env` 文件：
```env
# DeepSeek API配置（可选）
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Ollama配置（可选，用于本地模型）
OLLAMA_BASE_URL=http://localhost:11434

# 其他配置...
```

### 5. 启动应用
```bash
python -m Agents.Agent
```

## 🔧 详细安装步骤

### 步骤1：环境准备

#### 检查Python版本
```bash
python --version
# 应该显示 Python 3.10.x 或更高
```

#### 安装Git（如未安装）
- **Windows**: 下载并安装 [Git for Windows](https://gitforwindows.org/)
- **macOS**: `brew install git`
- **Ubuntu**: `sudo apt install git`

### 步骤2：获取项目代码

#### 方式1：Git克隆
```bash
git clone https://github.com/your-username/NekoAgent.git
cd NekoAgent
```

#### 方式2：下载ZIP
1. 访问项目GitHub页面
2. 点击 "Code" → "Download ZIP"
3. 解压到目标目录
4. 进入解压后的目录

### 步骤3：依赖安装

#### 基础依赖
项目使用 `requirements.txt` 管理依赖：
```bash
pip install -r requirements.txt
```

#### 依赖说明
主要依赖包包括：
- **langchain**: AI应用框架
- **langchain-community**: 社区工具和集成
- **langchain-core**: 核心组件
- **chromadb**: 向量数据库
- **fastapi**: Web框架
- **uvicorn**: ASGI服务器
- **python-dotenv**: 环境变量管理
- **requests**: HTTP客户端

#### 可选依赖
```bash
# 如果需要PDF处理
pip install pypdf

# 如果需要Excel处理
pip install openpyxl

# 如果需要图像处理
pip install pillow
```

### 步骤4：模型配置

#### 配置在线API模型（DeepSeek）
1. 注册 [DeepSeek](https://platform.deepseek.com/) 账号
2. 获取API密钥
3. 在 `.env` 文件中设置：
   ```env
   DEEPSEEK_API_KEY=your_actual_api_key
   ```

#### 配置本地模型（Ollama）
1. **安装Ollama**
   ```bash
   # Windows: 下载并安装 Ollama for Windows
   # macOS: brew install ollama
   # Linux: curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **启动Ollama服务**
   ```bash
   ollama serve
   ```

3. **下载所需模型**
   ```bash
   # 基础对话模型
   ollama pull qwen2.5:7b
   
   # RAG生成器模型（可选）
   ollama pull gpt-oss:20b
   
   # 嵌入模型（可选）
   ollama pull qwen3-embedding
   ```

4. **验证Ollama安装**
   ```bash
   ollama list
   # 应该显示已下载的模型
   ```

### 步骤5：环境变量配置

#### 创建.env文件
在项目根目录创建 `.env` 文件：

```env
# ===========================================
# 🐱 NekoAgent 环境配置
# ===========================================

# DeepSeek API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Ollama配置
OLLAMA_BASE_URL=http://localhost:11434

# 应用配置
LOG_LEVEL=INFO
MAX_RECURSION_LIMIT=300

# RAG配置
RAG_USE_GENERATOR=false
RAG_EMBEDDING_MODEL=chromadb
```

#### 环境变量说明

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | 无 | 可选 |
| `OLLAMA_BASE_URL` | Ollama服务地址 | `http://localhost:11434` | 可选 |
| `LOG_LEVEL` | 日志级别 | `INFO` | 可选 |
| `MAX_RECURSION_LIMIT` | 递归限制 | `300` | 可选 |

### 步骤6：验证安装

#### 运行测试
```bash
# 测试基础功能
python -c "from Agents.Agent import main; print('✅ 导入成功')"

# 测试配置加载
python -c "from Config.config_loader import load_config; print('✅ 配置加载成功')"
```

#### 检查目录结构
确保项目结构完整：
```
NekoAgent/
├── Agents/           # ✅ Agent核心系统
├── Config/           # ✅ 配置管理
├── Data/             # ✅ 数据存储
├── Tools/            # ✅ 工具生态系统
├── Sandbox/          # ✅ 沙盒环境
└── requirements.txt  # ✅ 依赖列表
```

## 🎯 首次运行

### 启动应用
```bash
python -m Agents.Agent
```

### 预期输出
```
🐱 NekoAgent 启动中...
✅ 配置加载成功
✅ 模型初始化完成
✅ 工具系统就绪
🎭 角色系统已加载: ['AI', 'Neko', 'UserSim']
🤖 可用模型: ['deepseek', 'ollama']

请输入命令开始交互:
> 
```

### 基础命令测试
```
/help          # 显示帮助信息
/role          # 显示角色选择
/model         # 显示模型选择
/thread        # 显示线程管理
```

## 🔍 故障排除

### 常见问题

#### 1. 导入错误
**问题**: `ModuleNotFoundError: No module named 'langchain'`
**解决**: 
```bash
pip install -r requirements.txt
```

#### 2. API密钥错误
**问题**: `AuthenticationError: Invalid API key`
**解决**:
- 检查 `.env` 文件中的API密钥
- 确认API密钥有效
- 检查网络连接

#### 3. Ollama连接失败
**问题**: `ConnectionError: Failed to connect to Ollama`
**解决**:
```bash
# 检查Ollama服务状态
ollama serve

# 验证服务运行
curl http://localhost:11434/api/tags
```

#### 4. 权限错误
**问题**: `PermissionError: [Errno 13] Permission denied`
**解决**:
- 确保对项目目录有读写权限
- 沙盒操作必须在 `Sandbox/` 目录下

#### 5. 内存不足
**问题**: `MemoryError` 或程序崩溃
**解决**:
- 关闭其他占用内存的程序
- 使用较小的模型
- 增加系统虚拟内存

### 日志查看

项目日志位于：`Agents/Modular/agent.log`

查看日志：
```bash
# Windows
type Agents\Modular\agent.log

# Linux/macOS
cat Agents/Modular/agent.log
```

## ⚙️ 高级配置

### 自定义角色
在 `Sandbox/Prompt/` 目录创建角色文件：

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

### 自定义工具
在 `Tools/` 目录下创建工具模块：

```python
# Tools/MyTool/my_tool.py
from langchain.tools import tool

@tool
def my_custom_tool(input: str) -> str:
    """工具描述"""
    return "处理结果"
```

### MCP工具开发
参考 `Tools/MCP/` 目录下的示例创建MCP工具。

## 🐳 Docker部署（可选）

### 使用Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  nekoagent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
    volumes:
      - ./Data:/app/Data
      - ./Sandbox:/app/Sandbox
```

### 构建和运行
```bash
docker-compose up -d
```

## 🔄 更新项目

### 获取最新代码
```bash
git pull origin main
```

### 更新依赖
```bash
pip install -r requirements.txt --upgrade
```

### 清理缓存
```bash
# 清理Python缓存
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# 清理ChromaDB缓存（可选）
rm -rf Data/chroma_db/
```

## 📞 获取帮助

如果遇到问题：

1. **查看文档**: 阅读 `README.md` 和本安装指南
2. **检查日志**: 查看 `Agents/Modular/agent.log`
3. **提交Issue**: 在项目GitHub页面提交问题
4. **社区支持**: 加入相关技术社区讨论

---

**🎉 恭喜！NekoAgent 安装完成！**

现在你可以开始使用这个强大的多角色AI助手框架了！

**🐱 享受与Neko的互动吧！**