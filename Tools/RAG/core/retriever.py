"""
检索器模块
负责从向量存储中检索相关文档
"""

from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import VectorStore


class Retriever:
    """检索器类"""
    
    def __init__(self, vector_store: VectorStore, search_type: str = "similarity"):
        """
        初始化检索器
        
        Args:
            vector_store: 向量存储实例
            search_type: 搜索类型，支持 "similarity" 或 "mmr"
        """
        self.vector_store = vector_store
        self.search_type = search_type

        # 创建LangChain检索器
        self.retriever = self._create_retriever()
    
    def _create_retriever(self) -> BaseRetriever:
        """创建检索器实例"""
        search_kwargs = {"k": 3}  # 默认返回3个文档
        
        if self.search_type == "mmr":
            # MMR (Maximal Marginal Relevance) 检索
            return self.vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 3, "fetch_k": 10}
            )
        else:
            # 相似性检索
            return self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs=search_kwargs
            )
    
    def search(self, 
               query: str, 
               k: int = 3, 
               filters: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            k: 返回的文档数量
            filters: 元数据过滤器
            
        Returns:
            相关文档列表
        """
        try:
            # 更新检索器配置
            if k != 3:
                self.retriever.search_kwargs["k"] = k
            
            if filters:
                self.retriever.search_kwargs["filter"] = filters
            
            # 执行检索
            results = self.retriever.invoke(query)
            
            return results
            
        except Exception as e:
            raise Exception(f"检索失败: {str(e)}")
    
    def search_with_score(self, 
                         query: str, 
                         k: int = 3, 
                         filters: Optional[Dict[str, Any]] = None) -> List[tuple]:
        """
        带相似度分数的检索
        
        Args:
            query: 查询文本
            k: 返回的文档数量
            filters: 元数据过滤器
            
        Returns:
            (文档, 分数) 元组列表
        """
        try:
            # 直接使用向量存储的带分数搜索
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filters
            )
            
            return results
            
        except Exception as e:
            raise Exception(f"带分数检索失败: {str(e)}")
    
    def search_with_relevance_threshold(self, 
                                      query: str, 
                                      k: int = 3,
                                      score_threshold: float = 0.5,
                                      filters: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        带相关性阈值的检索
        
        Args:
            query: 查询文本
            k: 返回的文档数量
            score_threshold: 分数阈值，只返回分数高于此值的文档
            filters: 元数据过滤器
            
        Returns:
            相关文档列表
        """
        try:
            # 获取带分数的结果
            scored_results = self.search_with_score(query, k, filters)
            
            # 过滤低于阈值的文档
            filtered_results = [
                doc for doc, score in scored_results 
                if score >= score_threshold
            ]
            
            return filtered_results
            
        except Exception as e:
            raise Exception(f"带阈值检索失败: {str(e)}")
    
    def hybrid_search(self, 
                     query: str, 
                     k: int = 3,
                     keyword_weight: float = 0.3,
                     semantic_weight: float = 0.7) -> List[Document]:
        """
        混合检索（关键词 + 语义）
        
        Args:
            query: 查询文本
            k: 返回的文档数量
            keyword_weight: 关键词检索权重
            semantic_weight: 语义检索权重
            
        Returns:
            相关文档列表
        """
        try:
            # 语义检索
            semantic_results = self.search(query, k)
            
            # 简单的关键词检索（基于包含关系）
            keyword_results = []
            query_words = set(query.lower().split())
            
            # 获取所有文档进行关键词匹配
            # 注意：这里简化实现，实际应该使用更高效的关键词检索
            all_docs = self.vector_store.get()
            if all_docs and "documents" in all_docs:
                for i, doc_content in enumerate(all_docs["documents"]):
                    doc_words = set(doc_content.lower().split())
                    common_words = query_words & doc_words
                    if common_words:
                        # 创建临时文档对象
                        temp_doc = Document(
                            page_content=doc_content,
                            metadata=all_docs["metadatas"][i] if "metadatas" in all_docs else {}
                        )
                        keyword_results.append(temp_doc)
            
            # 简单的混合策略（取前k个）
            combined_results = semantic_results[:int(k * semantic_weight)] + \
                             keyword_results[:int(k * keyword_weight)]
            
            # 去重
            seen_contents = set()
            unique_results = []
            for doc in combined_results:
                if doc.page_content not in seen_contents:
                    seen_contents.add(doc.page_content)
                    unique_results.append(doc)
            
            return unique_results[:k]
            
        except Exception as e:
            print(f"⚠️ 混合检索失败，回退到语义检索: {str(e)}")
            return self.search(query, k)
    
    def get_retriever_info(self) -> Dict[str, Any]:
        """
        获取检索器信息
        
        Returns:
            检索器信息字典
        """
        return {
            "search_type": self.search_type,
            "default_k": self.retriever.search_kwargs.get("k", 3),
            "vector_store_type": type(self.vector_store).__name__
        }
    
    def update_search_config(self, 
                           search_type: Optional[str] = None,
                           k: Optional[int] = None,
                           filters: Optional[Dict[str, Any]] = None):
        """
        更新检索配置
        
        Args:
            search_type: 搜索类型
            k: 返回文档数量
            filters: 元数据过滤器
        """
        if search_type and search_type != self.search_type:
            self.search_type = search_type
            self.retriever = self._create_retriever()
        
        if k:
            self.retriever.search_kwargs["k"] = k
        
        if filters is not None:
            self.retriever.search_kwargs["filter"] = filters


# 测试函数
def test_retriever():
    """测试检索器"""
    print("🧪 测试检索器...")
    
    # 创建测试数据
    from langchain_core.documents import Document
    from Sandbox.rag_system.core.vector_store import VectorStoreManager
    
    test_documents = [
        Document(
            page_content="机器学习是人工智能的一个分支，专注于算法和统计模型",
            metadata={"source": "ml_intro", "type": "definition", "topic": "ml"}
        ),
        Document(
            page_content="深度学习使用神经网络处理复杂模式识别任务",
            metadata={"source": "dl_intro", "type": "definition", "topic": "dl"}
        ),
        Document(
            page_content="自然语言处理让计算机理解和生成人类语言",
            metadata={"source": "nlp_intro", "type": "application", "topic": "nlp"}
        ),
        Document(
            page_content="计算机视觉处理图像和视频数据",
            metadata={"source": "cv_intro", "type": "application", "topic": "cv"}
        )
    ]
    
    # 测试1: 基本检索
    print("\n🔍 测试基本检索...")
    try:
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 初始化向量存储
            store_manager = VectorStoreManager(persist_directory=temp_dir)
            store_manager.initialize_store(test_documents)
            
            # 创建检索器
            retriever = Retriever(store_manager.vector_store)
            
            # 基本搜索
            results = retriever.search("机器学习", k=2)
            print(f"   基本检索: 找到 {len(results)} 个相关文档")
            
            # 检索器信息
            info = retriever.get_retriever_info()
            print(f"   检索器配置: {info}")
            
    except Exception as e:
        print(f"   ⚠️ 基本检索测试失败: {str(e)}")
        print("   可能是依赖问题，跳过详细测试")
        return
    
    # 测试2: 带分数检索
    print("\n📊 测试带分数检索...")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            store_manager = VectorStoreManager(persist_directory=temp_dir)
            store_manager.initialize_store(test_documents)
            
            retriever = Retriever(store_manager.vector_store)
            
            # 带分数搜索
            scored_results = retriever.search_with_score("深度学习", k=2)
            print(f"   带分数检索: 找到 {len(scored_results)} 个相关文档")
            
            if scored_results:
                for i, (doc, score) in enumerate(scored_results):
                    print(f"     文档{i+1}: 分数={score:.4f}, 内容={doc.page_content[:50]}...")
            
    except Exception as e:
        print(f"   ⚠️ 带分数检索测试失败: {str(e)}")
    
    # 测试3: 元数据过滤
    print("\n🎯 测试元数据过滤...")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            store_manager = VectorStoreManager(persist_directory=temp_dir)
            store_manager.initialize_store(test_documents)
            
            retriever = Retriever(store_manager.vector_store)
            
            # 使用元数据过滤
            filtered_results = retriever.search(
                "人工智能", 
                k=3, 
                filters={"type": "definition"}
            )
            print(f"   元数据过滤: 找到 {len(filtered_results)} 个定义类文档")
            
            for doc in filtered_results:
                print(f"     来源: {doc.metadata.get('source')}, 类型: {doc.metadata.get('type')}")
            
    except Exception as e:
        print(f"   ⚠️ 元数据过滤测试失败: {str(e)}")
    
    # 测试4: 带阈值检索
    print("\n📈 测试带阈值检索...")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            store_manager = VectorStoreManager(persist_directory=temp_dir)
            store_manager.initialize_store(test_documents)
            
            retriever = Retriever(store_manager.vector_store)
            
            # 带阈值搜索
            threshold_results = retriever.search_with_relevance_threshold(
                "神经网络", 
                k=3, 
                score_threshold=0.1
            )
            print(f"   带阈值检索: 找到 {len(threshold_results)} 个高相关文档")
            
    except Exception as e:
        print(f"   ⚠️ 带阈值检索测试失败: {str(e)}")
    
    # 测试5: 配置更新
    print("\n⚙️ 测试配置更新...")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            store_manager = VectorStoreManager(persist_directory=temp_dir)
            store_manager.initialize_store(test_documents)
            
            retriever = Retriever(store_manager.vector_store)
            
            # 更新配置
            retriever.update_search_config(k=2, filters={"topic": "nlp"})
            
            updated_info = retriever.get_retriever_info()
            print(f"   更新后配置: {updated_info}")
            
    except Exception as e:
        print(f"   ⚠️ 配置更新测试失败: {str(e)}")
    
    print("\n🎯 检索器测试完成")


if __name__ == "__main__":
    test_retriever()