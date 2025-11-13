"""
RAG系统工具接口 - 动态嵌入模型版
支持在运行时选择使用Ollama嵌入或默认嵌入
"""

import os
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool

current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))  # 假设在Tools目录下

knowledge_base_path = os.path.join(project_root, "Sandbox", "knowledge_base")
vector_store_path = os.path.join(project_root, "Data", "RAG", "vector_store")

# 配置信息
RAG_CONFIG = {
    "knowledge_base_path": knowledge_base_path,
    "vector_store_base_path": vector_store_path,
    "auto_load_on_init": False,  # 不自动加载，按需加载
    "use_generator": False,
    "supported_formats": [".txt", ".md", ".pdf", ".docx", ".doc", ".html", ".htm"],
    "text_splitter": {
        "chunk_size": 1000,
        "chunk_overlap": 200
    },
    "retrieval": {
        "default_k": 3,
        "similarity_threshold": 0.7
    }
}


def get_vector_store_path(use_ollama_embedding: bool) -> str:
    """
    根据嵌入模型类型获取对应的向量库路径

    Args:
        use_ollama_embedding: 是否使用Ollama嵌入模型

    Returns:
        向量库路径
    """
    base_path = RAG_CONFIG["vector_store_base_path"]
    if use_ollama_embedding:
        return base_path + "/ollama"
    else:
        return base_path + "/default"


def get_rag_system(use_ollama_embedding: bool = False, use_generator: bool = False):
    """
    获取RAG系统实例

    Args:
        use_ollama_embedding: 是否使用Ollama嵌入模型
        use_generator: 是否使用生成器

    Returns:
        RAG系统实例
    """
    try:
        from Tools.RAG.main import RAGSystem

        # 获取对应的向量库路径
        vector_store_path = get_vector_store_path(use_ollama_embedding)

        # 初始化RAG系统
        rag_system = RAGSystem(
            use_ollama_embedding=use_ollama_embedding,
            use_generator=use_generator,
            persist_directory=vector_store_path
        )

        return rag_system

    except Exception as e:
        raise Exception(f"RAG系统初始化失败: {str(e)}")


def ensure_knowledge_base_loaded(rag_system, use_ollama_embedding: bool):
    """
    确保知识库已加载

    Args:
        rag_system: RAG系统实例
        use_ollama_embedding: 是否使用Ollama嵌入模型
    """
    try:
        knowledge_base_path = RAG_CONFIG["knowledge_base_path"]
        vector_store_path = get_vector_store_path(use_ollama_embedding)

        # 检查知识库目录是否存在
        if not os.path.exists(knowledge_base_path):
            raise Exception(f"知识库目录不存在: {knowledge_base_path}")

        # 检查向量存储是否已存在
        if os.path.exists(vector_store_path):
            print(f"📚 使用现有向量存储: {vector_store_path}")
            return

        # 加载知识库
        print(f"📚 开始加载知识库: {knowledge_base_path}")
        result = rag_system.ingest_directory(
            directory_path=knowledge_base_path,
            file_extensions=RAG_CONFIG["supported_formats"]
        )

        if result["success"]:
            print(f"✅ 知识库加载完成: 处理了 {result['processed_files']} 个文件")
        else:
            raise Exception(f"知识库加载失败: {result.get('error', '未知错误')}")

    except Exception as e:
        raise Exception(f"知识库加载失败: {str(e)}")


@tool
def rag_search(question: str, k: int = None, use_ollama_embedding: bool = False) -> List[Dict[str, Any]]:
    """
    使用RAG系统检索相关文档（支持动态嵌入模型选择）

    Args:
        question: 查询问题
        k: 返回文档数量，默认使用配置值
        use_ollama_embedding: 是否使用Ollama嵌入模型

    Returns:
        检索到的文档列表，包含内容和元数据
    """
    try:
        if k is None:
            k = RAG_CONFIG["retrieval"]["default_k"]

        # 获取RAG系统实例
        rag_system = get_rag_system(use_ollama_embedding=use_ollama_embedding, use_generator=False)

        # 确保知识库已加载
        ensure_knowledge_base_loaded(rag_system, use_ollama_embedding)

        # 检索文档
        documents = rag_system.search(question, k=k)

        # 转换为可序列化的格式
        result = []
        for doc in documents:
            result.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "source": doc.metadata.get("source", "unknown")
            })

        return result

    except Exception as e:
        return [{"error": f"检索失败: {str(e)}"}]


@tool
def rag_query(question: str, k: int = None, use_generator: bool = None, use_ollama_embedding: bool = False) -> Dict[str, Any]:
    """
    使用RAG系统查询知识库（支持动态嵌入模型选择）

    Args:
        question: 查询问题
        k: 返回文档数量，默认使用配置值
        use_generator: 是否使用生成器生成答案
        use_ollama_embedding: 是否使用Ollama嵌入模型

    Returns:
        查询结果，包含检索到的文档和可选生成的答案
    """
    try:
        if k is None:
            k = RAG_CONFIG["retrieval"]["default_k"]
        if use_generator is None:
            use_generator = RAG_CONFIG["use_generator"]

        # 获取RAG系统实例
        rag_system = get_rag_system(use_ollama_embedding=use_ollama_embedding, use_generator=use_generator)

        # 确保知识库已加载
        ensure_knowledge_base_loaded(rag_system, use_ollama_embedding)

        # 查询知识库
        result = rag_system.query(question, k=k, use_generator=use_generator)

        # 转换文档为可序列化格式
        if "retrieved_documents" in result:
            docs = []
            for doc in result["retrieved_documents"]:
                docs.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source": doc.metadata.get("source", "unknown")
                })
            result["retrieved_documents"] = docs

        return result

    except Exception as e:
        return {
            "question": question,
            "error": f"查询失败: {str(e)}",
            "retrieved_documents": [],
            "sources_count": 0,
            "used_generator": use_generator if use_generator is not None else RAG_CONFIG["use_generator"]
        }


@tool
def rag_system_info(use_ollama_embedding: bool = False) -> Dict[str, Any]:
    """
    获取RAG系统信息（支持动态嵌入模型选择）

    Args:
        use_ollama_embedding: 是否使用Ollama嵌入模型

    Returns:
        系统配置和状态信息
    """
    try:
        # 获取RAG系统实例
        rag_system = get_rag_system(use_ollama_embedding=use_ollama_embedding, use_generator=False)

        system_info = rag_system.get_system_info()

        # 添加配置信息
        system_info["config"] = {
            "knowledge_base_path": RAG_CONFIG["knowledge_base_path"],
            "vector_store_path": get_vector_store_path(use_ollama_embedding),
            "auto_load_on_init": RAG_CONFIG["auto_load_on_init"],
            "supported_formats": RAG_CONFIG["supported_formats"]
        }

        return system_info

    except Exception as e:
        return {"error": f"获取系统信息失败: {str(e)}"}


@tool
def rag_refresh(use_ollama_embedding: bool = False) -> Dict[str, Any]:
    """
    刷新知识库 - 重新加载知识库文档（支持动态嵌入模型选择）

    Args:
        use_ollama_embedding: 是否使用Ollama嵌入模型

    Returns:
        刷新操作结果
    """
    try:
        knowledge_base_path = RAG_CONFIG["knowledge_base_path"]

        # 检查知识库目录是否存在
        if not os.path.exists(knowledge_base_path):
            return {
                "success": False,
                "error": f"知识库目录不存在: {knowledge_base_path}"
            }

        print(f"🔄 开始刷新知识库: {knowledge_base_path}")

        # 获取RAG系统实例
        rag_system = get_rag_system(use_ollama_embedding=use_ollama_embedding, use_generator=False)

        # 重新加载知识库
        result = rag_system.ingest_directory(
            directory_path=knowledge_base_path,
            file_extensions=RAG_CONFIG["supported_formats"]
        )

        if result["success"]:
            return {
                "success": True,
                "message": f"知识库刷新完成: 处理了 {result['processed_files']} 个文件",
                "details": result
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "未知错误"),
                "details": result
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"知识库刷新失败: {str(e)}"
        }


@tool
def rag_clear_knowledge_base(use_ollama_embedding: bool = False) -> Dict[str, Any]:
    """
    清空RAG知识库（支持动态嵌入模型选择）

    Args:
        use_ollama_embedding: 是否使用Ollama嵌入模型

    Returns:
        清空操作结果
    """
    try:
        # 获取RAG系统实例
        rag_system = get_rag_system(use_ollama_embedding=use_ollama_embedding, use_generator=False)

        success = rag_system.clear_knowledge_base()
        return {
            "success": success,
            "message": "知识库已清空" if success else "清空失败"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"清空知识库失败: {str(e)}"
        }


# 工具列表
RAG_TOOLS = [
    rag_search,
    rag_query,
    rag_system_info,
    rag_refresh,
    rag_clear_knowledge_base,
]


def get_rag_tools():
    """
    获取所有动态RAG工具

    Returns:
        RAG工具列表
    """
    return RAG_TOOLS


# 测试函数
def test_rag_tools():
    """测试动态RAG工具"""
    print("🧪 测试动态RAG工具...")
    # 测试刷新
    try:
        refresh_result = rag_refresh(use_ollama_embedding=False)
        print(f"   刷新测试: {refresh_result.get('success', False)}")
        refresh_result = rag_refresh(use_ollama_embedding=True)
        print(f"   刷新测试: {refresh_result.get('success', False)}")
        print("✅ 刷新工具测试通过")
    except Exception as e:
        print(f"   ⚠️ 刷新工具测试失败: {str(e)}")

    # 测试系统信息
    try:
        info_default = rag_system_info(use_ollama_embedding=False)
        print(f"   默认嵌入系统信息: {info_default.get('embedding_model', {})}")

        info_ollama = rag_system_info(use_ollama_embedding=True)
        print(f"   Ollama嵌入系统信息: {info_ollama.get('embedding_model', {})}")

        print("✅ 系统信息工具测试通过")
    except Exception as e:
        print(f"   ⚠️ 系统信息工具测试失败: {str(e)}")

    # 测试搜索
    try:
        results_default = rag_search("什么是Langchain", k=2, use_ollama_embedding=False)
        print(f"   默认嵌入搜索: 找到 {len(results_default)} 个文档")

        results_ollama = rag_search("什么是Langchain", k=2, use_ollama_embedding=True)
        print(f"   Ollama嵌入搜索: 找到 {len(results_ollama)} 个文档")

        print("✅ 搜索工具测试通过")
    except Exception as e:
        print(f"   ⚠️ 搜索工具测试失败: {str(e)}")

    print("🎯 动态RAG工具测试完成")


if __name__ == "__main__":
    test_rag_tools()