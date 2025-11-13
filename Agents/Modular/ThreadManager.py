# 🐱 线程管理模块 - ThreadManager.py
# 从Agent.py中分离的线程管理功能

import sqlite3
from typing import List, Optional


class ThreadManager:
    """线程管理类 - 负责所有线程相关的操作"""
    
    def __init__(self, agent_instance):
        """
        初始化线程管理器
        
        Args:
            agent_instance: Agent实例，用于访问配置和检查点
        """
        self.agent = agent_instance
        self.config = agent_instance.config
        self.checkpointer = agent_instance.checkpointer
        self.role_name = agent_instance.role_name
        self.user_id = agent_instance.user_id
    
    def show_current_thread(self) -> str:
        """显示当前线程信息"""
        thread_id = self.config["configurable"]["thread_id"]
        return f"📝 当前线程: {thread_id} (角色: {self.role_name}, 用户: {self.user_id})"
    
    def safe_delete_thread(self) -> bool:
        """安全删除当前线程（需要确认）"""
        thread_id = self.config["configurable"]["thread_id"]
        print(f"\n⚠️  警告: 即将删除线程: {thread_id}")
        print("⚠️  此操作将永久删除该线程的所有对话历史！")
        
        confirm = input("\n确定要删除吗？(输入'确认删除'继续): ").strip()
        if confirm == "确认删除":
            try:
                self.checkpointer.delete_thread(thread_id=thread_id)
                print("✅  线程已删除")
                return True
            except Exception as e:
                print(f"❌  删除失败: {e}")
                return False
        else:
            print("❌  操作已取消")
            return False
    
    def switch_thread(self, custom_suffix: str = "") -> str:
        """
        切换到指定线程
        
        Args:
            custom_suffix: 自定义后缀，为空时使用默认线程名
            
        Returns:
            新的线程ID
        """
        # 生成标准线程ID
        if custom_suffix:
            # 清理自定义后缀中的非法字符
            clean_suffix = "".join(c for c in custom_suffix if c.isalnum() or c in "-_")
            if not clean_suffix:
                clean_suffix = "custom"
            new_thread_id = f"Agent-{self.role_name}-User-{self.user_id}-{clean_suffix}"
        else:
            # 默认线程名
            new_thread_id = f"Agent-{self.role_name}-User-{self.user_id}"
        
        print(f"🔄  正在切换到线程: {new_thread_id}")
        
        # 更新配置
        old_thread_id = self.config["configurable"]["thread_id"]
        self.config["configurable"]["thread_id"] = new_thread_id
        
        # 重新创建agent以应用新线程
        self.agent.agent = self.agent._create_agent()
        
        print(f"✅  已切换到线程: {new_thread_id}")
        
        # 显示线程切换前后的对比
        if old_thread_id != new_thread_id:
            print(f"📊  线程变更: {old_thread_id} → {new_thread_id}")
        
        return new_thread_id
    
    def list_recent_threads(self, limit: int = 10) -> List[str]:
        """
        列出最近活跃的线程
        
        Args:
            limit: 返回的线程数量限制
            
        Returns:
            线程ID列表
        """
        try:
            # 从SQLite数据库查询活跃线程
            if hasattr(self.checkpointer, 'conn') and self.checkpointer.conn:
                cursor = self.checkpointer.conn.cursor()
                
                # 查询最近有活动的线程
                query = """
                SELECT DISTINCT thread_id 
                FROM checkpoints 
                ORDER BY checkpoint 
                LIMIT ?
                """
                
                cursor.execute(query, (limit,))
                threads = [row[0] for row in cursor.fetchall()]
                
                return threads
            else:
                # 如果无法查询数据库，返回当前线程
                return [self.config["configurable"]["thread_id"]]
                
        except Exception as e:
            print(f"⚠️  查询线程列表失败: {e}")
            # 返回当前线程作为备选
            return [self.config["configurable"]["thread_id"]]
    
    def get_thread_info(self, thread_id: str) -> Optional[dict]:
        """
        获取线程详细信息
        
        Args:
            thread_id: 线程ID
            
        Returns:
            线程信息字典，包含角色、用户等信息
        """
        try:
            # 解析线程ID格式: Agent-{角色}-User-{用户ID}-{自定义后缀}
            parts = thread_id.split("-")
            
            if len(parts) >= 4 and parts[0] == "Agent" and parts[2] == "User":
                info = {
                    "thread_id": thread_id,
                    "role": parts[1],
                    "user_id": parts[3],
                    "custom_suffix": "-".join(parts[4:]) if len(parts) > 4 else ""
                }
                return info
            else:
                # 非标准格式
                return {
                    "thread_id": thread_id,
                    "role": "未知",
                    "user_id": "未知", 
                    "custom_suffix": ""
                }
                
        except Exception as e:
            print(f"⚠️  解析线程信息失败: {e}")
            return None
    
    def validate_thread_id(self, thread_id: str) -> bool:
        """
        验证线程ID格式是否合法
        
        Args:
            thread_id: 要验证的线程ID
            
        Returns:
            是否合法
        """
        # 基本格式检查
        if not thread_id or len(thread_id) > 100:
            return False
            
        # 允许的字符: 字母、数字、下划线、连字符
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        
        return all(char in allowed_chars for char in thread_id)


# 线程管理相关的工具函数
def create_thread_manager(agent_instance):
    """
    创建线程管理器实例
    
    Args:
        agent_instance: Agent实例
        
    Returns:
        ThreadManager实例
    """
    return ThreadManager(agent_instance)