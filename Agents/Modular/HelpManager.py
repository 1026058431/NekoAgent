# 🐱 帮助管理器 - HelpManager.py
# 统一的帮助信息管理系统

class HelpManager:
    """帮助管理器 - 统一管理所有帮助信息"""
    
    def __init__(self, agent_instance=None):
        """
        初始化帮助管理器
        
        Args:
            agent_instance: Agent实例（可选）
        """
        self.agent = agent_instance
    
    def get_full_help(self) -> str:
        """
        获取完整的帮助信息
        
        Returns:
            完整的帮助文本
        """
        return """🐱 NekoAgent 命令帮助 🐱

🎯 基础命令
  help              - 显示此帮助信息
  reset             - 安全重置当前对话线程
  q / quit / exit   - 退出程序
  s / show / state  - 显示当前状态
  h / his / history - 显示历史状态

🔧 模型管理
  model / switch / switch_model  - 交互式模型选择
  (支持: deepseek, ollama, qwen, qwen3_mini)

🎭 角色管理  
  role / switch_role  - 交互式角色选择
  (支持: Neko 及其他可用角色)

📊 线程管理
  thread            - 交互式线程管理
  /thread           - 显示当前线程
  /thread switch    - 切换到默认线程
  /thread switch <名> - 切换到自定义线程
  /thread list      - 显示线程列表
  /thread reset     - 安全重置当前线程
  /thread help      - 显示线程管理帮助

💫 其他功能
  /<命令>           - 执行斜杠命令
  直接输入          - 与Neko对话

📝 使用示例:
  model             # 切换模型
  role              # 切换角色  
  /thread list      # 查看线程列表
  help model        # 查看模型相关帮助
"""
    
    def get_category_help(self, category: str) -> str:
        """
        获取分类帮助信息
        
        Args:
            category: 帮助类别
            
        Returns:
            分类帮助文本
        """
        category = category.lower()
        
        if category in ["model", "models"]:
            return self._get_model_help()
        elif category in ["role", "roles"]:
            return self._get_role_help()
        elif category in ["thread", "threads"]:
            return self._get_thread_help()
        elif category in ["tool", "tools"]:
            return self._get_tool_help()
        elif category in ["basic", "base"]:
            return self._get_basic_help()
        else:
            return f"❌ 未知帮助类别: {category}\n\n{self.get_full_help()}"
    
    def get_command_help(self, command: str) -> str:
        """
        获取具体命令的帮助信息
        
        Args:
            command: 命令名称
            
        Returns:
            命令帮助文本
        """
        command = command.lower()
        
        # 基础命令
        if command in ["help"]:
            return "📋 help [类别] - 显示帮助信息，可指定类别"
        elif command in ["reset"]:
            return "🔄 reset - 安全重置当前对话线程，清除历史"
        elif command in ["q", "quit", "exit"]:
            return "🚪 q/quit/exit - 退出程序"
        elif command in ["s", "show", "state"]:
            return "📊 s/show/state - 显示当前Agent状态"
        elif command in ["h", "his", "history"]:
            return "📜 h/his/history - 显示历史状态记录"
        
        # 模型命令
        elif command in ["model", "switch", "switch_model"]:
            return self._get_model_help()
        
        # 角色命令
        elif command in ["role", "switch_role"]:
            return self._get_role_help()
        
        # 线程命令
        elif command == "thread":
            return self._get_thread_help()
        
        else:
            return f"❌ 未知命令: {command}\n\n{self.get_full_help()}"
    
    def _get_basic_help(self) -> str:
        """获取基础命令帮助"""
        return """🎯 基础命令帮助

help              - 显示完整帮助信息
help [类别]       - 显示指定类别帮助
reset             - 安全重置当前对话线程
q / quit / exit   - 退出程序
s / show / state  - 显示当前状态
h / his / history - 显示历史状态

📝 示例:
  help            # 显示完整帮助
  help model      # 显示模型相关帮助
  reset           # 重置当前对话
"""
    
    def _get_model_help(self) -> str:
        """获取模型管理帮助"""
        available_models = ["deepseek", "ollama", "qwen", "qwen3_mini"]
        return f"""🔧 模型管理帮助

model / switch / switch_model  - 交互式模型选择

📋 可用模型:
  {'  '.join(available_models)}

💡 功能说明:
  • 支持运行时动态切换模型
  • 保持对话上下文不变
  • 自动重新创建Agent实例

📝 使用示例:
  model           # 进入交互式模型选择
  switch_model    # 同上
"""
    
    def _get_role_help(self) -> str:
        """获取角色管理帮助"""
        available_roles = ["Neko"]  # 可以从agent实例获取
        if self.agent:
            try:
                available_roles = self.agent.list_available_roles()
            except:
                pass
        
        return f"""🎭 角色管理帮助

role / switch_role  - 交互式角色选择

📋 可用角色:
  {'  '.join(available_roles)}

💡 功能说明:
  • 支持运行时动态切换角色
  • 每个角色有独立的系统提示
  • 自动更新Thread ID以匹配新角色

📝 使用示例:
  role            # 进入交互式角色选择
  switch_role     # 同上
"""
    
    def _get_thread_help(self) -> str:
        """获取线程管理帮助"""
        return """📊 线程管理帮助

thread            - 交互式线程管理界面
/thread           - 显示当前线程信息
/thread switch    - 切换到默认线程
/thread switch <名> - 切换到自定义线程
/thread list      - 显示最近活跃线程列表
/thread reset     - 安全重置当前线程
/thread help      - 显示线程管理帮助

💡 功能说明:
  • 每个线程独立存储对话历史
  • 支持自定义线程名称
  • 安全重置不会丢失数据备份

📝 使用示例:
  thread          # 进入交互式线程管理
  /thread list    # 查看线程列表
  /thread switch work # 切换到'work'线程
"""
    
    def _get_tool_help(self) -> str:
        """获取工具使用帮助"""
        return """🛠️ 工具使用帮助

NekoAgent 集成了丰富的工具系统:

📁 文件操作工具
  • 沙盒内文件读写、移动、删除
  • 自动备份和安全检查
  • 目录浏览和清理

🌐 网络工具
  • HTTP请求功能
  • 自定义payload发送
  • MCP服务器连接

📚 RAG工具
  • 知识库检索和查询
  • 支持多种嵌入模型
  • 知识库刷新和管理

📝 模板工具
  • 报告模板管理
  • 模板创建和使用

💡 工具会自动在需要时调用，无需手动操作
"""


def create_help_manager(agent_instance=None):
    """
    创建帮助管理器实例
    
    Args:
        agent_instance: Agent实例（可选）
        
    Returns:
        HelpManager实例
    """
    return HelpManager(agent_instance)


# 测试函数
def test_help_manager():
    """测试帮助管理器"""
    print("🧪 测试HelpManager...")
    
    help_manager = HelpManager()
    
    # 测试完整帮助
    print("\n📋 完整帮助:")
    print(help_manager.get_full_help())
    
    # 测试分类帮助
    print("\n🔧 模型帮助:")
    print(help_manager.get_category_help("model"))
    
    print("\n🎭 角色帮助:")
    print(help_manager.get_category_help("role"))
    
    print("\n📊 线程帮助:")
    print(help_manager.get_category_help("thread"))
    
    # 测试命令帮助
    print("\n📝 命令帮助:")
    print(help_manager.get_command_help("reset"))
    print(help_manager.get_command_help("model"))
    
    print("✅ HelpManager测试完成")


if __name__ == "__main__":
    test_help_manager()