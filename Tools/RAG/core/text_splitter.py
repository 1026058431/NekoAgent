"""
文本分割器模块
负责将大文档分割为适合向量化的小块
"""

from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextSplitter:
    """文本分割器类"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        初始化文本分割器
        
        Args:
            chunk_size: 每个chunk的最大字符数
            chunk_overlap: chunk之间的重叠字符数
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 使用递归字符文本分割器
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        分割文档列表
        
        Args:
            documents: 要分割的文档列表
            
        Returns:
            分割后的文档列表
        """
        if not documents:
            return []
        
        try:
            # 使用LangChain的分割器
            split_docs = self.splitter.split_documents(documents)
            
            # 确保元数据被正确传递
            for i, doc in enumerate(split_docs):
                # 保留原始元数据
                if i < len(documents):
                    doc.metadata.update(documents[0].metadata)
                
                # 添加分割相关的元数据
                doc.metadata.update({
                    "chunk_size": len(doc.page_content),
                    "chunk_index": i,
                    "total_chunks": len(split_docs)
                })
            
            return split_docs
            
        except Exception as e:
            raise Exception(f"文档分割失败: {str(e)}")
    
    def split_text(self, text: str, metadata: dict = None) -> List[Document]:
        """
        分割纯文本
        
        Args:
            text: 要分割的文本
            metadata: 可选的元数据
            
        Returns:
            分割后的文档列表
        """
        if not text:
            return []
        
        try:
            # 创建临时文档
            temp_doc = Document(
                page_content=text,
                metadata=metadata or {}
            )
            
            # 分割文档
            return self.split_documents([temp_doc])
            
        except Exception as e:
            raise Exception(f"文本分割失败: {str(e)}")
    
    def get_splitter_info(self) -> dict:
        """获取分割器配置信息"""
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "splitter_type": "RecursiveCharacterTextSplitter"
        }


# 测试函数
def test_text_splitter():
    """测试文本分割器"""
    print("🧪 测试文本分割器...")
    
    # 创建测试分割器
    splitter = TextSplitter(chunk_size=500, chunk_overlap=50)
    
    # 测试1: 短文本分割
    print("📝 测试短文本分割...")
    short_text = "这是一个短文本，不需要分割。"
    documents = splitter.split_text(short_text, {"source": "test"})
    
    print(f"   短文本分割结果: {len(documents)} 个文档")
    print(f"   文档内容: {documents[0].page_content}")
    print(f"   文档元数据: {documents[0].metadata}")
    
    # 测试2: 长文本分割
    print("\n📝 测试长文本分割...")
    long_text = """
    这是一个长文本，需要被分割成多个chunk。
    
    第一段内容。第一段内容。第一段内容。第一段内容。第一段内容。
    第一段内容。第一段内容。第一段内容。第一段内容。第一段内容。
    
    第二段内容。第二段内容。第二段内容。第二段内容。第二段内容。
    第二段内容。第二段内容。第二段内容。第二段内容。第二段内容。
    
    第三段内容。第三段内容。第三段内容。第三段内容。第三段内容。
    第三段内容。第三段内容。第三段内容。第三段内容。第三段内容。
    
    第四段内容。第四段内容。第四段内容。第四段内容。第四段内容。
    第四段内容。第四段内容。第四段内容。第四段内容。第四段内容。
    """
    
    documents = splitter.split_text(long_text, {"source": "long_test"})
    
    print(f"   长文本分割结果: {len(documents)} 个文档")
    for i, doc in enumerate(documents[:3]):  # 只显示前3个
        print(f"   文档{i+1}: {doc.page_content[:100]}...")
        print(f"   元数据: chunk_size={doc.metadata.get('chunk_size')}, "
              f"chunk_index={doc.metadata.get('chunk_index')}")
    
    # 测试3: 文档列表分割
    print("\n📝 测试文档列表分割...")
    from langchain_core.documents import Document
    
    doc1 = Document(page_content="第一个文档内容", metadata={"doc_id": 1})
    doc2 = Document(page_content="第二个文档内容", metadata={"doc_id": 2})
    
    documents = splitter.split_documents([doc1, doc2])
    
    print(f"   文档列表分割结果: {len(documents)} 个文档")
    
    # 测试4: 分割器信息
    print("\n📝 测试分割器信息...")
    info = splitter.get_splitter_info()
    print(f"   分割器配置: {info}")
    
    print("\n🎯 文本分割器测试完成")


if __name__ == "__main__":
    test_text_splitter()