"""
嵌入管理器模块
负责管理嵌入模型，主要支持Ollama，ChromaDB使用内置Sentence Transformers
"""

from typing import List, Union, Optional
from langchain_core.embeddings import Embeddings
from langchain_community.embeddings import OllamaEmbeddings
# 加载.env文件 - 从项目根目录
from dotenv import load_dotenv
import os
from pathlib import Path
# 获取项目根目录路径
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"

# 加载.env文件
load_dotenv(env_path)

# 从环境变量获取Ollama基础URL，默认为localhost:11434
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

class EmbeddingManager:
    """嵌入管理器类"""
    
    def __init__(self, use_ollama: bool = False, model_name: str = "qwen3-embedding"):
        """
        初始化嵌入管理器
        
        Args:
            use_ollama: 是否使用Ollama嵌入模型，默认False（使用ChromaDB内置）
            model_name: Ollama模型名称
        """
        self.use_ollama = use_ollama
        self.model_name = model_name
        self.embeddings = self._init_embeddings()
    
    def _init_embeddings(self) -> Optional[Embeddings]:
        """初始化嵌入模型"""
        if self.use_ollama:
            try:
                print(f"🔧 初始化Ollama嵌入模型: {self.model_name}")
                return OllamaEmbeddings(
                    model=self.model_name,
                    base_url=OLLAMA_BASE_URL
                )
            except Exception as e:
                print(f"⚠️ Ollama嵌入模型初始化失败: {str(e)}")
                print("   将回退到ChromaDB内置嵌入")
                return None
        else:
            print("🔧 使用ChromaDB内置Sentence Transformers嵌入")
            return None
    
    def get_embedding_function(self) -> Optional[Embeddings]:
        """
        获取嵌入函数
        
        Returns:
            嵌入函数实例，None表示使用ChromaDB默认嵌入
        """
        return self.embeddings
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        嵌入文档列表（仅在使用Ollama时有效）
        
        Args:
            texts: 文本列表
            
        Returns:
            嵌入向量列表
            
        Raises:
            Exception: 未使用Ollama时调用此方法
        """
        if not self.use_ollama:
            raise Exception("当前使用ChromaDB内置嵌入，请直接使用vector_store")
        
        if not texts:
            return []
        
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            raise Exception(f"文档嵌入失败: {str(e)}")
    
    def embed_query(self, text: str) -> List[float]:
        """
        嵌入查询文本（仅在使用Ollama时有效）
        
        Args:
            text: 查询文本
            
        Returns:
            查询嵌入向量
            
        Raises:
            Exception: 未使用Ollama时调用此方法
        """
        if not self.use_ollama:
            raise Exception("当前使用ChromaDB内置嵌入，请直接使用vector_store")
        
        if not text:
            return []
        
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            raise Exception(f"查询嵌入失败: {str(e)}")
    
    def get_embedding_dimension(self) -> int:
        """获取嵌入维度"""
        if not self.use_ollama:
            # ChromaDB内置嵌入通常是384维
            return 384
        
        try:
            # 测试嵌入一个小文本以获取维度
            test_embedding = self.embed_query("test")
            return len(test_embedding)
        except Exception as e:
            print(f"⚠️ 无法获取嵌入维度: {str(e)}")
            return 0
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            "use_ollama": self.use_ollama,
            "model_name": self.model_name if self.use_ollama else "ChromaDB内置",
            "embedding_dimension": self.get_embedding_dimension()
        }
    
    def switch_to_ollama(self, model_name: str = "qwen3-embedding"):
        """
        切换到Ollama嵌入模型
        
        Args:
            model_name: Ollama模型名称
        """
        self.use_ollama = True
        self.model_name = model_name
        self.embeddings = self._init_embeddings()
        
        print(f"🔄 已切换到Ollama嵌入模型: {self.model_name}")
    
    def switch_to_chromadb(self):
        """切换到ChromaDB内置嵌入"""
        self.use_ollama = False
        self.embeddings = None
        
        print("🔄 已切换到ChromaDB内置嵌入")


# 测试函数
def test_embedding_manager():
    """测试嵌入管理器"""
    print("🧪 测试嵌入管理器...")
    
    # 测试1: 默认使用ChromaDB内置
    print("\n🔧 测试ChromaDB内置嵌入模式...")
    manager = EmbeddingManager(use_ollama=False)
    info = manager.get_model_info()
    
    print(f"   模型信息: {info}")
    print(f"   嵌入函数: {manager.get_embedding_function()}")
    
    # 测试2: Ollama嵌入模式
    print("\n🔧 测试Ollama嵌入模式...")
    try:
        manager = EmbeddingManager(use_ollama=True)
        info = manager.get_model_info()
        
        print(f"   模型信息: {info}")
        print(f"   嵌入函数: {manager.get_embedding_function() is not None}")
        
        # 测试文档嵌入
        test_texts = ["这是一个测试文档", "这是另一个测试文档"]
        embeddings = manager.embed_documents(test_texts)
        
        print(f"   文档嵌入测试: 成功嵌入 {len(embeddings)} 个文档")
        print(f"   嵌入维度: {len(embeddings[0]) if embeddings else 0}")
        
    except Exception as e:
        print(f"   ⚠️ Ollama测试失败: {str(e)}")
        print("   可能是Ollama服务未启动，跳过详细测试")
    
    # 测试3: 模型切换
    print("\n🔄 测试模型切换...")
    manager = EmbeddingManager(use_ollama=False)
    
    # 切换到Ollama
    try:
        manager.switch_to_ollama()
        info = manager.get_model_info()
        print(f"   切换到Ollama: {info}")
    except Exception as e:
        print(f"   ⚠️ 切换到Ollama失败: {str(e)}")
    
    # 切换回ChromaDB
    manager.switch_to_chromadb()
    info = manager.get_model_info()
    print(f"   切换回ChromaDB: {info}")
    
    # 测试4: 错误处理
    print("\n⚠️ 测试错误处理...")
    manager = EmbeddingManager(use_ollama=False)
    
    try:
        manager.embed_documents(["test"])
        print("   ❌ 错误处理测试失败: 应该抛出异常")
    except Exception as e:
        print(f"   ✅ 错误处理测试通过: {str(e)}")
    
    print("\n🎯 嵌入管理器测试完成")


if __name__ == "__main__":
    test_embedding_manager()