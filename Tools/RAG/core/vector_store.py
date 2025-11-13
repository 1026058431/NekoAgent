"""
向量存储管理器模块
负责管理ChromaDB向量存储
"""

import os
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma


class VectorStoreManager:
    """向量存储管理器类"""
    
    def __init__(self, 
                 embedding_function: Optional[Embeddings] = None,
                 persist_directory: str = "./chroma_db",
                 collection_name: str = "rag_collection"):
        """
        初始化向量存储管理器
        
        Args:
            embedding_function: 嵌入函数，None表示使用ChromaDB默认
            persist_directory: 持久化目录
            collection_name: 集合名称
        """
        self.embedding_function = embedding_function
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.vector_store = None
        
        # 确保目录存在
        os.makedirs(persist_directory, exist_ok=True)
    
    def initialize_store(self, documents: Optional[List[Document]] = None) -> Chroma:
        """
        初始化向量存储
        
        Args:
            documents: 初始文档列表，可选
            
        Returns:
            Chroma向量存储实例
        """
        try:
            if documents:
                print(f"📚 初始化向量存储，添加 {len(documents)} 个文档...")
                self.vector_store = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embedding_function,
                    persist_directory=self.persist_directory,
                    collection_name=self.collection_name
                )
            else:
                print("📚 加载现有向量存储...")
                self.vector_store = Chroma(
                    embedding_function=self.embedding_function,
                    persist_directory=self.persist_directory,
                    collection_name=self.collection_name
                )
            
            print(f"✅ 向量存储初始化完成")
            return self.vector_store
            
        except Exception as e:
            raise Exception(f"向量存储初始化失败: {str(e)}")
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        向向量存储添加文档
        
        Args:
            documents: 要添加的文档列表
            
        Returns:
            添加的文档ID列表
        """
        if not self.vector_store:
            self.initialize_store()
        
        if not documents:
            return []
        
        try:
            print(f"📝 向向量存储添加 {len(documents)} 个文档...")
            
            # 添加文档
            doc_ids = self.vector_store.add_documents(documents)
            
            print(f"✅ 成功添加 {len(doc_ids)} 个文档")
            return doc_ids
            
        except Exception as e:
            raise Exception(f"添加文档失败: {str(e)}")
    
    def search(self, 
               query: str, 
               k: int = 3, 
               filter: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        相似性搜索
        
        Args:
            query: 查询文本
            k: 返回的文档数量
            filter: 元数据过滤器
            
        Returns:
            相似文档列表
        """
        if not self.vector_store:
            self.initialize_store()
        
        try:
            results = self.vector_store.similarity_search(
                query=query,
                k=k,
                filter=filter
            )
            
            return results
            
        except Exception as e:
            raise Exception(f"搜索失败: {str(e)}")
    
    def search_with_score(self, 
                         query: str, 
                         k: int = 3, 
                         filter: Optional[Dict[str, Any]] = None) -> List[tuple]:
        """
        带相似度分数的搜索
        
        Args:
            query: 查询文本
            k: 返回的文档数量
            filter: 元数据过滤器
            
        Returns:
            (文档, 分数) 元组列表
        """
        if not self.vector_store:
            self.initialize_store()
        
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter
            )
            
            return results
            
        except Exception as e:
            raise Exception(f"带分数搜索失败: {str(e)}")
    
    def delete_documents(self, ids: List[str]) -> bool:
        """
        删除指定ID的文档
        
        Args:
            ids: 要删除的文档ID列表
            
        Returns:
            是否成功删除
        """
        if not self.vector_store:
            raise Exception("向量存储未初始化")
        
        try:
            self.vector_store.delete(ids=ids)
            print(f"🗑️ 成功删除 {len(ids)} 个文档")
            return True
            
        except Exception as e:
            raise Exception(f"删除文档失败: {str(e)}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        获取集合信息
        
        Returns:
            集合信息字典
        """
        if not self.vector_store:
            self.initialize_store()
        
        try:
            # 获取集合统计信息
            collection = self.vector_store._collection
            count = collection.count()
            
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory,
                "embedding_function": "自定义" if self.embedding_function else "ChromaDB默认"
            }
            
        except Exception as e:
            return {
                "collection_name": self.collection_name,
                "error": str(e)
            }
    
    def clear_collection(self) -> bool:
        """
        清空集合
        
        Returns:
            是否成功清空
        """
        if not self.vector_store:
            raise Exception("向量存储未初始化")
        
        try:
            # 获取所有文档ID并删除
            collection = self.vector_store._collection
            results = collection.get()
            
            if results and "ids" in results:
                self.vector_store.delete(ids=results["ids"])
                print("🗑️ 成功清空集合")
            else:
                print("ℹ️ 集合已经是空的")
            
            return True
            
        except Exception as e:
            raise Exception(f"清空集合失败: {str(e)}")
    
    def close(self):
        """
        关闭向量存储，释放资源
        
        注意：ChromaDB会自动管理连接，此方法主要用于测试清理
        """
        if self.vector_store:
            # ChromaDB会自动清理，这里主要是为了测试
            self.vector_store = None
            print("🔒 向量存储已关闭")


# 测试函数
def test_vector_store():
    """测试向量存储管理器"""
    print("🧪 测试向量存储管理器...")
    
    # 创建测试数据
    from langchain_core.documents import Document
    
    test_documents = [
        Document(
            page_content="机器学习是人工智能的一个分支",
            metadata={"source": "test1", "type": "definition"}
        ),
        Document(
            page_content="深度学习是机器学习的一个子领域",
            metadata={"source": "test2", "type": "definition"}
        ),
        Document(
            page_content="自然语言处理是AI的重要应用领域",
            metadata={"source": "test3", "type": "application"}
        )
    ]
    
    # 测试1: 初始化向量存储
    print("\n📚 测试向量存储初始化...")
    try:
        # 使用临时目录进行测试
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            store_manager = VectorStoreManager(
                persist_directory=temp_dir,
                collection_name="test_collection"
            )
            
            # 初始化并添加文档
            store_manager.initialize_store(test_documents)
            
            info = store_manager.get_collection_info()
            print(f"   集合信息: {info}")
            
    except Exception as e:
        print(f"   ⚠️ 向量存储初始化测试失败: {str(e)}")
        print("   可能是ChromaDB依赖问题，跳过详细测试")
        return
    
    # 测试2: 搜索功能
    print("\n🔍 测试搜索功能...")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            store_manager = VectorStoreManager(
                persist_directory=temp_dir,
                collection_name="test_collection"
            )
            store_manager.initialize_store(test_documents)
            
            # 基本搜索
            results = store_manager.search("机器学习", k=2)
            print(f"   基本搜索: 找到 {len(results)} 个相关文档")
            
            # 带分数搜索
            scored_results = store_manager.search_with_score("深度学习", k=2)
            print(f"   带分数搜索: 找到 {len(scored_results)} 个相关文档")
            if scored_results:
                print(f"   最高分数: {scored_results[0][1]:.4f}")
            
    except Exception as e:
        print(f"   ⚠️ 搜索功能测试失败: {str(e)}")
    
    # 测试3: 元数据过滤
    print("\n🎯 测试元数据过滤...")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            store_manager = VectorStoreManager(
                persist_directory=temp_dir,
                collection_name="test_collection"
            )
            store_manager.initialize_store(test_documents)
            
            # 使用元数据过滤
            filtered_results = store_manager.search(
                "人工智能", 
                k=3, 
                filter={"type": "definition"}
            )
            print(f"   过滤搜索: 找到 {len(filtered_results)} 个定义类文档")
            
    except Exception as e:
        print(f"   ⚠️ 元数据过滤测试失败: {str(e)}")
    
    # 测试4: 文档管理
    print("\n📝 测试文档管理...")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            store_manager = VectorStoreManager(
                persist_directory=temp_dir,
                collection_name="test_collection"
            )
            
            # 先初始化空集合
            store_manager.initialize_store()
            
            # 添加文档
            doc_ids = store_manager.add_documents(test_documents)
            print(f"   添加文档: 成功添加 {len(doc_ids)} 个文档")
            
            # 获取集合信息
            info = store_manager.get_collection_info()
            print(f"   集合状态: {info['document_count']} 个文档")
            
    except Exception as e:
        print(f"   ⚠️ 文档管理测试失败: {str(e)}")
    
    print("\n🎯 向量存储管理器测试完成")


if __name__ == "__main__":
    test_vector_store()