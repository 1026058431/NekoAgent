"""
文档加载器模块
负责从不同来源加载文档
"""

import os
from typing import List, Union
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    WebBaseLoader,
    CSVLoader,
    JSONLoader
)


class DocumentLoader:
    """文档加载器类"""
    
    def __init__(self):
        self.supported_formats = ["pdf", "txt", "html", "csv", "json","md"]
    
    def load_file(self, file_path: str) -> List[Document]:
        """
        根据文件扩展名自动选择合适的加载器
        
        Args:
            file_path: 文件路径
            
        Returns:
            文档列表
            
        Raises:
            ValueError: 不支持的文件格式
            FileNotFoundError: 文件不存在
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        file_ext = file_path.lower().split('.')[-1]
        
        if file_ext == "pdf":
            return self.load_pdf(file_path)
        elif file_ext == "txt":
            return self.load_text(file_path)
        elif file_ext == "md":
            return self.load_text(file_path)  # MD文件可以用文本加载器处理
        elif file_ext in ["html", "htm"]:
            return self.load_web(file_path)
        elif file_ext == "csv":
            return self.load_csv(file_path)
        elif file_ext == "json":
            return self.load_json(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """加载PDF文档"""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # 添加文件元数据
            for doc in documents:
                doc.metadata.update({
                    "source": file_path,
                    "type": "pdf",
                    "page": doc.metadata.get("page", 0)
                })
            
            return documents
        except Exception as e:
            raise Exception(f"PDF加载失败: {str(e)}")
    
    def load_text(self, file_path: str) -> List[Document]:
        """加载文本文件"""
        try:
            loader = TextLoader(file_path, encoding="utf-8")
            documents = loader.load()
            
            # 添加文件元数据
            for doc in documents:
                doc.metadata.update({
                    "source": file_path,
                    "type": "text"
                })
            
            return documents
        except Exception as e:
            raise Exception(f"文本文件加载失败: {str(e)}")
    
    def load_web(self, url_or_path: str) -> List[Document]:
        """加载网页内容"""
        try:
            # 如果是本地HTML文件，使用文件路径
            if os.path.exists(url_or_path):
                loader = WebBaseLoader(url_or_path)
            else:
                # 如果是URL，直接加载
                loader = WebBaseLoader(url_or_path)
            
            documents = loader.load()
            
            # 添加元数据
            for doc in documents:
                doc.metadata.update({
                    "source": url_or_path,
                    "type": "web"
                })
            
            return documents
        except Exception as e:
            raise Exception(f"网页内容加载失败: {str(e)}")
    
    def load_csv(self, file_path: str) -> List[Document]:
        """加载CSV文件"""
        try:
            loader = CSVLoader(file_path)
            documents = loader.load()
            
            # 添加元数据
            for doc in documents:
                doc.metadata.update({
                    "source": file_path,
                    "type": "csv"
                })
            
            return documents
        except Exception as e:
            raise Exception(f"CSV文件加载失败: {str(e)}")
    
    def load_json(self, file_path: str) -> List[Document]:
        """加载JSON文件"""
        try:
            loader = JSONLoader(
                file_path=file_path,
                jq_schema='.',
                text_content=False
            )
            documents = loader.load()
            
            # 添加元数据
            for doc in documents:
                doc.metadata.update({
                    "source": file_path,
                    "type": "json"
                })
            
            return documents
        except Exception as e:
            raise Exception(f"JSON文件加载失败: {str(e)}")
    
    def load_directory(self, dir_path: str) -> List[Document]:
        """加载目录中的所有支持文件"""
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"目录不存在: {dir_path}")
        
        all_documents = []
        
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = file.lower().split('.')[-1]
                
                if file_ext in self.supported_formats:
                    try:
                        documents = self.load_file(file_path)
                        all_documents.extend(documents)
                    except Exception as e:
                        print(f"警告: 加载文件 {file_path} 失败: {str(e)}")
        
        return all_documents


# 测试函数
def test_document_loader():
    """测试文档加载器"""
    print("🧪 测试文档加载器...")
    
    loader = DocumentLoader()
    
    # 创建测试数据
    test_content = "这是一个测试文档内容，用于验证文档加载器的功能。"
    
    # 测试文本文件加载
    try:
        # 创建测试文件
        test_file = "test_sample.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        documents = loader.load_text(test_file)
        
        print(f"✅ 文本文件加载测试通过")
        print(f"   加载文档数量: {len(documents)}")
        print(f"   文档内容: {documents[0].page_content[:50]}...")
        print(f"   文档元数据: {documents[0].metadata}")
        
        # 清理测试文件
        os.remove(test_file)
        
    except Exception as e:
        print(f"❌ 文本文件加载测试失败: {str(e)}")
    
    # 测试自动文件类型检测
    try:
        # 创建测试文件
        test_file = "test_auto.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        documents = loader.load_file(test_file)
        
        print(f"✅ 自动文件类型检测测试通过")
        print(f"   加载文档数量: {len(documents)}")
        
        # 清理测试文件
        os.remove(test_file)
        
    except Exception as e:
        print(f"❌ 自动文件类型检测测试失败: {str(e)}")
    
    # 测试错误处理
    try:
        documents = loader.load_file("nonexistent_file.txt")
        print(f"❌ 错误处理测试失败: 应该抛出异常")
    except FileNotFoundError:
        print(f"✅ 错误处理测试通过")
    
    print("🎯 文档加载器测试完成")


if __name__ == "__main__":
    test_document_loader()