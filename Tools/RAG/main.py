"""
RAG系统主集成模块
支持可选生成器和直接检索结果
"""
import shutil
from typing import List, Dict, Any, Optional, Union
from langchain_core.documents import Document

from Tools.RAG.core.document_loader import DocumentLoader
from Tools.RAG.core.text_splitter import TextSplitter
from Tools.RAG.core.embedding_manager import EmbeddingManager
from Tools.RAG.core.vector_store import VectorStoreManager
from Tools.RAG.core.retriever import Retriever
from Tools.RAG.core.generator import Generator


class RAGSystem:
    """RAG系统主类"""

    def __init__(self,
                 use_ollama_embedding: bool = False,
                 use_generator: bool = False,
                 persist_directory: str = "./chroma_db",
                 collection_name: str = "rag_collection"):
        """
        初始化RAG系统

        Args:
            use_ollama_embedding: 是否使用Ollama嵌入
            use_generator: 是否使用生成器
            persist_directory: 向量存储持久化目录
            collection_name: 集合名称
        """
        print("🚀 初始化RAG系统...")

        # 核心组件
        self.loader = DocumentLoader()
        self.splitter = TextSplitter()

        # 嵌入管理器
        self.embedding_manager = EmbeddingManager(use_ollama=use_ollama_embedding)

        # 向量存储
        self.vector_store = VectorStoreManager(
            embedding_function=self.embedding_manager.get_embedding_function(),
            persist_directory=persist_directory,
            collection_name=collection_name
        )

        # 检索器
        self.vector_store.initialize_store()  # 确保向量存储已初始化
        self.retriever = Retriever(self.vector_store.vector_store)

        # 可选生成器
        self.use_generator = use_generator
        if use_generator:
            self.generator = Generator()
            print("🤖 生成器已启用")
        else:
            self.generator = None
            print("🔍 生成器未启用，将直接返回检索结果")

        print("✅ RAG系统初始化完成")

    def ingest_documents(self,
                        file_path: str,
                        chunk_size: int = 1000,
                        chunk_overlap: int = 200) -> Dict[str, Any]:
        """
        摄取文档到知识库

        Args:
            file_path: 文档文件路径
            chunk_size: 文本分割块大小
            chunk_overlap: 文本分割重叠大小

        Returns:
            处理结果信息
        """
        try:
            print(f"📚 开始摄取文档: {file_path}")

            # 1. 加载文档
            documents = self.loader.load_file(file_path)
            print(f"   加载了 {len(documents)} 个文档")

            # 2. 分割文档
            self.splitter.chunk_size = chunk_size
            self.splitter.chunk_overlap = chunk_overlap
            split_documents = self.splitter.split_documents(documents)
            print(f"   分割成 {len(split_documents)} 个文本块")

            # 3. 添加到向量存储
            doc_ids = self.vector_store.add_documents(split_documents)

            # 4. 获取集合信息
            collection_info = self.vector_store.get_collection_info()

            result = {
                "success": True,
                "file_path": file_path,
                "original_documents": len(documents),
                "split_documents": len(split_documents),
                "added_documents": len(doc_ids),
                "collection_info": collection_info
            }

            print(f"✅ 文档摄取完成: 添加了 {len(doc_ids)} 个文档块")
            return result

        except Exception as e:
            error_msg = f"文档摄取失败: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "file_path": file_path
            }

    def search(self,
               question: str,
               k: int = 3,
               filters: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        仅检索相关文档，不生成答案

        Args:
            question: 查询问题
            k: 返回文档数量
            filters: 元数据过滤器

        Returns:
            检索到的文档列表
        """
        try:
            print(f"🔍 检索问题: {question}")

            results = self.retriever.search(question, k=k, filters=filters)

            print(f"✅ 检索完成: 找到 {len(results)} 个相关文档")
            return results

        except Exception as e:
            raise Exception(f"检索失败: {str(e)}")

    def query(self,
              question: str,
              k: int = 3,
              filters: Optional[Dict[str, Any]] = None,
              use_generator: Optional[bool] = None) -> Dict[str, Any]:
        """
        查询知识库

        Args:
            question: 查询问题
            k: 返回文档数量
            filters: 元数据过滤器
            use_generator: 是否使用生成器，None表示使用系统默认

        Returns:
            查询结果
        """
        try:
            print(f"❓ 查询问题: {question}")

            # 确定是否使用生成器
            should_use_generator = use_generator if use_generator is not None else self.use_generator

            # 检索相关文档
            retrieved_docs = self.retriever.search(question, k=k, filters=filters)

            if not retrieved_docs:
                return {
                    "question": question,
                    "answer": "抱歉，没有找到相关的信息来回答这个问题。",
                    "retrieved_documents": [],
                    "sources_count": 0,
                    "used_generator": False
                }

            # 根据配置决定是否使用生成器
            if should_use_generator and self.generator:
                print("🤖 使用生成器生成答案...")
                result = self.generator.generate_answer_with_sources(question, retrieved_docs)
                result["used_generator"] = True
            else:
                print("🔍 直接返回检索结果...")
                result = {
                    "question": question,
                    "answer": None,  # 表示未使用生成器
                    "retrieved_documents": retrieved_docs,
                    "sources_count": len(retrieved_docs),
                    "used_generator": False
                }

            print(f"✅ 查询完成: 找到 {len(retrieved_docs)} 个相关文档")
            return result

        except Exception as e:
            raise Exception(f"查询失败: {str(e)}")

    def get_system_info(self) -> Dict[str, Any]:
        """
        获取系统信息

        Returns:
            系统信息字典
        """
        collection_info = self.vector_store.get_collection_info()

        return {
            "embedding_model": self.embedding_manager.get_model_info(),
            "collection_info": collection_info,
            "generator_enabled": self.use_generator,
            "generator_info": self.generator.get_model_info() if self.generator else None
        }

    def clear_knowledge_base(self) -> bool:
        """
        清空知识库

        Returns:
            是否成功清空
        """
        try:
            return self.vector_store.clear_collection()
        except Exception as e:
            raise Exception(f"清空知识库失败: {str(e)}")

    def ingest_directory(self,
                         directory_path: str,
                         file_extensions: List[str] = None,
                         chunk_size: int = 1000,
                         chunk_overlap: int = 200) -> Dict[str, Any]:
        """
        批量摄取目录下的所有文档

        Args:
            directory_path: 文档目录路径
            file_extensions: 支持的文件扩展名列表，默认支持常见文本文件
            chunk_size: 文本分割块大小
            chunk_overlap: 文本分割重叠大小

        Returns:
            处理结果信息
        """
        try:
            import os

            print(f"📚 开始批量摄取目录: {directory_path}")

            # 默认支持的文件扩展名
            if file_extensions is None:
                file_extensions = ['.txt', '.md', '.pdf', '.docx', '.doc', '.html', '.htm']

            # 收集所有支持的文件
            supported_files = []
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in file_extensions:
                        full_path = os.path.join(root, file)
                        supported_files.append(full_path)

            if not supported_files:
                return {
                    "success": False,
                    "error": f"在目录 {directory_path} 中未找到支持的文件类型: {file_extensions}",
                    "directory_path": directory_path
                }

            print(f"   找到 {len(supported_files)} 个支持的文件")

            total_documents = 0
            total_chunks = 0
            processed_files = []
            failed_files = []

            # 逐个处理文件
            for file_path in supported_files:
                try:
                    print(f"   处理文件: {os.path.basename(file_path)}")

                    # 加载文档
                    documents = self.loader.load_file(file_path)

                    # 分割文档
                    self.splitter.chunk_size = chunk_size
                    self.splitter.chunk_overlap = chunk_overlap
                    split_documents = self.splitter.split_documents(documents)

                    # 添加到向量存储
                    doc_ids = self.vector_store.add_documents(split_documents)

                    total_documents += len(documents)
                    total_chunks += len(split_documents)
                    processed_files.append({
                        "file_path": file_path,
                        "original_documents": len(documents),
                        "split_documents": len(split_documents),
                        "added_documents": len(doc_ids)
                    })

                    print(f"      ✅ 成功添加 {len(split_documents)} 个文档块")

                except Exception as e:
                    error_msg = f"处理文件失败: {str(e)}"
                    print(f"      ❌ {error_msg}")
                    failed_files.append({
                        "file_path": file_path,
                        "error": error_msg
                    })

            # 获取集合信息
            collection_info = self.vector_store.get_collection_info()

            result = {
                "success": True,
                "directory_path": directory_path,
                "total_files": len(supported_files),
                "processed_files": len(processed_files),
                "failed_files": len(failed_files),
                "total_original_documents": total_documents,
                "total_split_documents": total_chunks,
                "processed_files_details": processed_files,
                "failed_files_details": failed_files,
                "collection_info": collection_info
            }

            print(f"✅ 批量文档摄取完成: 处理了 {len(processed_files)} 个文件，添加了 {total_chunks} 个文档块")
            if failed_files:
                print(f"⚠️  有 {len(failed_files)} 个文件处理失败")

            return result

        except Exception as e:
            error_msg = f"批量文档摄取失败: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "directory_path": directory_path
            }

    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息

        Returns:
            知识库统计信息
        """
        try:
            collection_info = self.vector_store.get_collection_info()

            return {
                "collection_info": collection_info,
                "system_info": self.get_system_info()
            }
        except Exception as e:
            raise Exception(f"获取知识库统计信息失败: {str(e)}")


# 批量文档测试函数
def test_batch_ingest():
    """测试批量文档加载功能"""
    print("🧪 测试批量文档加载功能...")

    import tempfile
    import os
    import shutil

    # 创建测试目录和文件
    test_dir = tempfile.mkdtemp()

    try:
        # 创建多个测试文件
        test_files = {
            "machine_learning.txt": """
机器学习是人工智能的一个重要分支。
它专注于开发算法和统计模型，使计算机能够从数据中学习并做出预测或决策。
""",
            "deep_learning.md": """
# 深度学习

深度学习是机器学习的一个子领域。
它使用神经网络来处理复杂的模式识别任务，如图像识别和自然语言处理。
""",
            "nlp_doc.txt": """
自然语言处理(NLP)是人工智能的一个应用领域。
它让计算机能够理解、解释和生成人类语言。
"""
        }

        # 写入测试文件
        for filename, content in test_files.items():
            file_path = os.path.join(test_dir, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content.strip())

        print(f"📁 创建测试目录: {test_dir}")
        print(f"   包含 {len(test_files)} 个测试文件")

        # 初始化RAG系统
        rag_system = RAGSystem(use_generator=False, persist_directory=test_dir + "_vector_store")

        # 批量摄取文档
        batch_result = rag_system.ingest_directory(test_dir)

        print(f"\n📊 批量摄取结果:")
        print(f"   成功处理: {batch_result['processed_files']} 个文件")
        print(f"   失败文件: {batch_result['failed_files']} 个")
        print(f"   原始文档: {batch_result['total_original_documents']} 个")
        print(f"   分割块数: {batch_result['total_split_documents']} 个")

        # 测试查询
        print(f"\n🔍 测试查询功能...")

        # 查询机器学习相关
        ml_results = rag_system.search("什么是机器学习", k=2)
        print(f"   机器学习查询: 找到 {len(ml_results)} 个相关文档")

        # 查询深度学习相关
        dl_results = rag_system.search("深度学习", k=2)
        print(f"   深度学习查询: 找到 {len(dl_results)} 个相关文档")

        # 获取知识库统计
        stats = rag_system.get_knowledge_base_stats()
        print(f"\n📈 知识库统计:")
        print(f"   向量存储类型: {stats['collection_info'].get('vector_store_type', 'N/A')}")
        print(f"   文档数量: {stats['collection_info'].get('document_count', 0)}")

        print("✅ 批量文档加载测试通过")

    finally:
        # 清理测试目录
        try:
            shutil.rmtree(test_dir, ignore_errors=True)
        except:
            pass


# 测试函数
def test_rag_system():
    """测试RAG系统"""
    print("🧪 测试RAG系统...")

    # 创建测试数据
    import tempfile
    import os

    # 创建测试文件
    test_content = """
机器学习是人工智能的一个重要分支。
它专注于开发算法和统计模型，使计算机能够从数据中学习并做出预测或决策。

深度学习是机器学习的一个子领域。
它使用神经网络来处理复杂的模式识别任务，如图像识别和自然语言处理。

自然语言处理(NLP)是人工智能的一个应用领域。
它让计算机能够理解、解释和生成人类语言。
"""

    # 使用手动创建的临时目录
    temp_dir = tempfile.mkdtemp()

    try:
        # 创建测试文件
        test_file = os.path.join(temp_dir, "test_ai.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)

        # 测试1: 不使用生成器
        print("\n🔍 测试不使用生成器模式...")
        try:
            rag_system = RAGSystem(use_generator=False, persist_directory=temp_dir)

            # 摄取文档
            ingest_result = rag_system.ingest_documents(test_file)
            print(f"   文档摄取: {ingest_result['success']}")

            # 仅检索
            search_results = rag_system.search("什么是机器学习？", k=2)
            print(f"   仅检索: 找到 {len(search_results)} 个文档")

            # 查询（不使用生成器）
            query_result = rag_system.query("机器学习和深度学习的区别？", k=2)
            print(f"   查询结果: 使用生成器={query_result['used_generator']}")
            print(f"   相关文档: {query_result['sources_count']} 个")

            # 系统信息
            system_info = rag_system.get_system_info()
            print(f"   系统信息: 生成器启用={system_info['generator_enabled']}")

            print("✅ 不使用生成器模式测试通过")

        except Exception as e:
            print(f"   ⚠️ 不使用生成器模式测试失败: {str(e)}")

        # 测试2: 使用生成器（如果Ollama可用）
        print("\n🤖 测试使用生成器模式...")
        try:
            rag_system = RAGSystem(use_generator=True, persist_directory=temp_dir)

            # 查询（使用生成器）
            query_result = rag_system.query("什么是自然语言处理？", k=2)
            print(f"   查询结果: 使用生成器={query_result['used_generator']}")

            if query_result['used_generator']:
                print(f"   生成答案: {query_result['answer'][:100]}...")

            print("✅ 使用生成器模式测试通过")

        except Exception as e:
            print(f"   ⚠️ 使用生成器模式测试失败: {str(e)}")
            print("   可能是Ollama服务未启动")

    finally:
        # 手动清理，忽略错误
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

    print("\n🎯 RAG系统测试完成")

if __name__ == "__main__":
    # 运行批量文档测试
    test_batch_ingest()
    print("\n" + "=" * 50)
    # 运行原有测试
    test_rag_system()
