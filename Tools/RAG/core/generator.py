"""
生成器模块
负责基于检索内容生成答案
"""

from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
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


class Generator:
    """生成器类"""
    
    def __init__(self, 
                 model_name: str = "gpt-oss:20b",
                 temperature: float = 0.7,
                 max_tokens: int = 1000):
        """
        初始化生成器
        
        Args:
            model_name: Ollama模型名称
            temperature: 生成温度
            max_tokens: 最大token数
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # 初始化聊天模型
        self.model = self._init_model()
        
        # 创建提示模板
        self.prompt_template = self._create_prompt_template()
        
        # 创建生成链
        self.chain = self._create_chain()
    
    def _init_model(self) -> ChatOllama:
        """初始化聊天模型"""
        try:
            print(f"🤖 初始化Ollama聊天模型: {self.model_name}")
            return ChatOllama(
                model=self.model_name,
                temperature=self.temperature,
                num_predict=self.max_tokens,
                base_url=OLLAMA_BASE_URL
            )
        except Exception as e:
            raise Exception(f"聊天模型初始化失败: {str(e)}")
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """创建提示模板"""
        template = """
你是一个专业的AI助手。请基于提供的上下文信息回答用户的问题。

上下文信息:
{context}

用户问题: {question}

请按照以下要求回答:
1. 基于上下文信息提供准确、相关的答案
2. 如果上下文信息不足以回答问题，请明确说明
3. 保持回答简洁明了
4. 如果适用，可以引用上下文中的具体信息

回答:
"""
        return ChatPromptTemplate.from_template(template)
    
    def _create_chain(self):
        """创建生成链"""
        return self.prompt_template | self.model | StrOutputParser()
    
    def generate_answer(self, 
                       question: str, 
                       context_documents: List[Document]) -> str:
        """
        基于检索内容生成答案
        
        Args:
            question: 用户问题
            context_documents: 检索到的相关文档
            
        Returns:
            生成的答案
        """
        if not context_documents:
            return "抱歉，没有找到相关的上下文信息来回答这个问题。"
        
        try:
            # 构建上下文
            context = self._build_context(context_documents)
            
            # 生成答案
            answer = self.chain.invoke({
                "context": context,
                "question": question
            })
            
            return answer
            
        except Exception as e:
            raise Exception(f"答案生成失败: {str(e)}")
    
    def _build_context(self, documents: List[Document]) -> str:
        """
        构建上下文字符串
        
        Args:
            documents: 文档列表
            
        Returns:
            格式化的上下文字符串
        """
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            # 添加文档内容
            content = doc.page_content.strip()
            
            # 添加元数据信息
            metadata_info = []
            if doc.metadata:
                if "source" in doc.metadata:
                    metadata_info.append(f"来源: {doc.metadata['source']}")
                if "type" in doc.metadata:
                    metadata_info.append(f"类型: {doc.metadata['type']}")
            
            metadata_str = f" ({', '.join(metadata_info)})" if metadata_info else ""
            
            context_parts.append(f"[{i}] {content}{metadata_str}")
        
        return "\n\n".join(context_parts)
    
    def generate_answer_with_sources(self, 
                                   question: str, 
                                   context_documents: List[Document]) -> Dict[str, Any]:
        """
        生成答案并包含来源信息
        
        Args:
            question: 用户问题
            context_documents: 检索到的相关文档
            
        Returns:
            包含答案和来源信息的字典
        """
        answer = self.generate_answer(question, context_documents)
        
        # 构建来源信息
        sources = []
        for doc in context_documents:
            source_info = {
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "metadata": doc.metadata
            }
            sources.append(source_info)
        
        return {
            "answer": answer,
            "sources": sources,
            "sources_count": len(sources)
        }
    
    def update_model_config(self, 
                          model_name: str = None,
                          temperature: float = None,
                          max_tokens: int = None):
        """
        更新模型配置
        
        Args:
            model_name: 模型名称
            temperature: 生成温度
            max_tokens: 最大token数
        """
        config_updated = False
        
        if model_name and model_name != self.model_name:
            self.model_name = model_name
            config_updated = True
        
        if temperature is not None and temperature != self.temperature:
            self.temperature = temperature
            config_updated = True
        
        if max_tokens is not None and max_tokens != self.max_tokens:
            self.max_tokens = max_tokens
            config_updated = True
        
        if config_updated:
            # 重新初始化模型和链
            self.model = self._init_model()
            self.chain = self._create_chain()
            print(f"🔄 生成器配置已更新: model={self.model_name}, temp={self.temperature}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "model_type": "ChatOllama"
        }


# 测试函数
def test_generator():
    """测试生成器"""
    print("🧪 测试生成器...")
    
    # 创建测试数据
    from langchain_core.documents import Document
    
    test_documents = [
        Document(
            page_content="机器学习是人工智能的一个分支，专注于算法和统计模型。",
            metadata={"source": "ml_guide", "type": "definition"}
        ),
        Document(
            page_content="深度学习是机器学习的一个子领域，使用神经网络处理复杂任务。",
            metadata={"source": "dl_tutorial", "type": "definition"}
        )
    ]
    
    # 测试1: 基本答案生成
    print("\n🤖 测试基本答案生成...")
    try:
        generator = Generator()
        
        question = "什么是机器学习？"
        answer = generator.generate_answer(question, test_documents)
        
        print(f"   问题: {question}")
        print(f"   答案: {answer[:100]}...")
        print("   ✅ 基本答案生成测试通过")
        
    except Exception as e:
        print(f"   ⚠️ 基本答案生成测试失败: {str(e)}")
        print("   可能是Ollama服务未启动，跳过详细测试")
        return
    
    # 测试2: 带来源的答案生成
    print("\n📚 测试带来源的答案生成...")
    try:
        generator = Generator()
        
        question = "机器学习和深度学习有什么区别？"
        result = generator.generate_answer_with_sources(question, test_documents)
        
        print(f"   问题: {question}")
        print(f"   答案: {result['answer'][:100]}...")
        print(f"   来源数量: {result['sources_count']}")
        print("   ✅ 带来源答案生成测试通过")
        
    except Exception as e:
        print(f"   ⚠️ 带来源答案生成测试失败: {str(e)}")
    
    # 测试3: 空上下文处理
    print("\n⚠️ 测试空上下文处理...")
    try:
        generator = Generator()
        
        question = "什么是人工智能？"
        answer = generator.generate_answer(question, [])
        
        print(f"   问题: {question}")
        print(f"   答案: {answer}")
        print("   ✅ 空上下文处理测试通过")
        
    except Exception as e:
        print(f"   ⚠️ 空上下文处理测试失败: {str(e)}")
    
    # 测试4: 模型配置
    print("\n⚙️ 测试模型配置...")
    try:
        generator = Generator()
        
        # 获取模型信息
        info = generator.get_model_info()
        print(f"   初始配置: {info}")
        
        # 更新配置
        generator.update_model_config(temperature=0.5, max_tokens=500)
        
        updated_info = generator.get_model_info()
        print(f"   更新后配置: {updated_info}")
        
        print("   ✅ 模型配置测试通过")
        
    except Exception as e:
        print(f"   ⚠️ 模型配置测试失败: {str(e)}")
    
    # 测试5: 上下文构建
    print("\n📝 测试上下文构建...")
    try:
        generator = Generator()
        
        context = generator._build_context(test_documents)
        print(f"   构建的上下文:\n{context[:200]}...")
        
        print("   ✅ 上下文构建测试通过")
        
    except Exception as e:
        print(f"   ⚠️ 上下文构建测试失败: {str(e)}")
    
    print("\n🎯 生成器测试完成")


if __name__ == "__main__":
    test_generator()