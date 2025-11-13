"""
🐱 HTTP获取工具

集成功能：
- HTTP请求和重试机制
- HTML解析和内容提取
- 文本处理和优化
- 智能内容类型检测

作者: Neko
版本: 4.0
"""

from langchain.tools import tool
import requests
import time
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Union, Callable
from collections import Counter
import string
from urllib.parse import urljoin, urlparse


# ==================== 辅助函数 ====================

def _is_html_content(content_type: str) -> bool:
    """判断是否为HTML内容"""
    return content_type and 'text/html' in content_type.lower()


def _build_error_response(error_msg: str, attempt: int, url: str, strategy: str) -> Dict:
    """构建错误响应"""
    return {
        'success': False,
        'error': error_msg,
        'status_code': 0,
        'url': url,
        'attempt': attempt,
        'optimization_strategy': strategy
    }


# ==================== HTML解析模块 ====================

def _parse_html_impl(
    content: str,
    base_url: str = "",
    extract_rules: Optional[Dict] = None,
    optimize: bool = True
) -> Dict[str, Union[str, List, Dict]]:
    """
    HTML解析实现函数

    Args:
        content: HTML内容
        base_url: 基础URL，用于解析相对链接
        extract_rules: 提取规则配置
            - title_selector: 标题选择器
            - content_selector: 内容选择器
            - link_selector: 链接选择器
            - remove_selectors: 要移除的元素选择器列表
        optimize: 是否优化内容（清理噪音）

    Returns:
        Dict: 包含解析结果的字典
    """

    # 默认提取规则
    default_rules = {
        'title_selector': 'title, h1, .title, .heading',
        'content_selector': 'main, article, .content, .main-content, body',
        'link_selector': 'a[href]',
        'remove_selectors': [
            'script', 'style', 'nav', 'header', 'footer',
            '.ad', '.ads', '.advertisement', '.navigation',
            '.menu', '.sidebar', '.footer', '.nextra-toc'
        ]
    }

    # 合并规则
    if extract_rules:
        default_rules.update(extract_rules)

    rules = default_rules

    try:
        # 创建BeautifulSoup对象
        soup = BeautifulSoup(content, 'html.parser')

        # 移除不需要的元素
        for selector in rules['remove_selectors']:
            for element in soup.select(selector):
                element.decompose()

        # 提取标题
        title = ""
        for selector in rules['title_selector'].split(', '):
            title_elem = soup.select_one(selector.strip())
            if title_elem and title_elem.get_text().strip():
                title = title_elem.get_text().strip()
                break

        # 提取主要内容
        content_text = ""
        content_elem = soup.select_one(rules['content_selector'])
        if content_elem:
            content_text = content_elem.get_text().strip()
        else:
            # 如果没有找到特定内容区域，使用整个body
            body_elem = soup.find('body')
            if body_elem:
                content_text = body_elem.get_text().strip()

        # 优化内容（如果启用）
        if optimize:
            content_text = _clean_text(content_text)

        # 提取链接
        links = _extract_links(soup, base_url, rules['link_selector'])

        # 提取元数据
        metadata = _extract_metadata(soup)

        # 提取代码块（对于文档页面很重要）
        code_blocks = _extract_code_blocks(soup)

        return {
            'success': True,
            'title': title,
            'content': content_text,
            'content_length': len(content_text),
            'links': links,
            'metadata': metadata,
            'code_blocks': code_blocks,
            'link_count': len(links),
            'code_block_count': len(code_blocks),
            'optimized': optimize
        }

    except Exception as e:
        return {
            'success': False,
            'error': f'HTML解析错误: {str(e)}',
            'title': '',
            'content': '',
            'links': [],
            'metadata': {},
            'code_blocks': [],
            'optimized': optimize
        }


def _extract_links(soup: BeautifulSoup, base_url: str, selector: str) -> List[Dict]:
    """提取页面中的所有链接"""
    links = []
    seen_urls = set()

    for link_elem in soup.select(selector):
        href = link_elem.get('href', '').strip()
        if not href or href.startswith('javascript:') or href == '#':
            continue

        # 解析完整URL
        full_url = urljoin(base_url, href) if base_url else href

        # 去重
        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)

        # 提取链接信息
        link_info = {
            'url': full_url,
            'text': link_elem.get_text().strip(),
            'title': link_elem.get('title', ''),
            'is_external': _is_external_link(full_url, base_url)
        }

        links.append(link_info)

    return links


def _extract_metadata(soup: BeautifulSoup) -> Dict[str, str]:
    """提取页面元数据"""
    metadata = {}

    # 提取meta标签
    for meta in soup.find_all('meta'):
        name = meta.get('name') or meta.get('property')
        content = meta.get('content', '')

        if name and content:
            metadata[name] = content

    return metadata


def _extract_code_blocks(soup: BeautifulSoup, max_blocks: int = 10) -> List[Dict]:
    """提取代码块"""
    code_blocks = []

    for code_elem in soup.find_all(['code', 'pre']):
        code_text = code_elem.get_text().strip()
        if len(code_text) > 10:  # 只保留有意义的代码块
            code_blocks.append({
                'content': code_text,
                'language': _detect_code_language(code_elem),
                'length': len(code_text)
            })
            if len(code_blocks) >= max_blocks:
                break

    return code_blocks


def _detect_code_language(code_elem) -> str:
    """检测代码语言"""
    # 简单的语言检测
    class_attr = code_elem.get('class', [])
    if class_attr:
        for cls in class_attr:
            if 'language-' in cls:
                return cls.replace('language-', '')

    # 根据内容推测
    code_text = code_elem.get_text()
    if 'def ' in code_text or 'import ' in code_text:
        return 'python'
    elif 'function' in code_text or 'const ' in code_text:
        return 'javascript'
    elif '<' in code_text and '>' in code_text:
        return 'html'
    else:
        return 'unknown'


def _clean_text(text: str) -> str:
    """清理文本内容"""
    if not text:
        return ""

    # 移除多余的空格和换行
    text = re.sub(r'\s+', ' ', text)

    # 移除首尾空格
    text = text.strip()

    return text


def _is_external_link(url: str, base_url: str) -> bool:
    """判断是否为外部链接"""
    if not base_url:
        return False

    try:
        base_domain = urlparse(base_url).netloc
        url_domain = urlparse(url).netloc

        return bool(url_domain and url_domain != base_domain)
    except:
        return False


# ==================== 文本处理模块 ====================

def _process_text_impl(
    content: str,
    filters: Optional[List[str]] = None,
    max_length: Optional[int] = None,
    generate_summary: bool = False,
    extract_keywords: bool = False,
    keyword_count: int = 10,
    optimize_strategy: str = "smart"
) -> Dict[str, Union[str, List, Dict]]:
    """
    文本处理实现函数（简洁版）

    Args:
        content: 原始文本内容
        filters: 过滤器列表
            - 'remove_extra_spaces': 移除多余空格
            - 'remove_special_chars': 移除特殊字符
            - 'normalize_newlines': 标准化换行符
            - 'remove_numbers': 移除数字
        max_length: 最大文本长度（截断）
        generate_summary: 是否生成摘要
        extract_keywords: 是否提取关键词
        keyword_count: 关键词数量
        optimize_strategy: 优化策略
            - "smart": 智能优化
            - "chunk": 分块处理
            - "summary": 摘要生成

    Returns:
        Dict: 包含处理结果的字典
    """

    # 空内容直接返回
    if not content:
        return {
            'success': True,
            'processed_text': '',
            'original_length': 0,
            'processed_length': 0,
            'reduction_ratio': 0,
            'stats': {'char_count': 0, 'word_count': 0, 'sentence_count': 0, 'paragraph_count': 1},
            'optimization_strategy': optimize_strategy
        }

    # 默认过滤器
    default_filters = [
        'remove_extra_spaces',
        'normalize_newlines',
        'remove_special_chars'
    ]

    if filters:
        active_filters = filters
    else:
        active_filters = default_filters

    try:
        # 应用过滤器
        processed_text = content

        for filter_name in active_filters:
            if filter_name == 'remove_extra_spaces':
                processed_text = _remove_extra_spaces(processed_text)
            elif filter_name == 'remove_special_chars':
                processed_text = _remove_special_chars(processed_text)
            elif filter_name == 'normalize_newlines':
                processed_text = _normalize_newlines(processed_text)
            elif filter_name == 'remove_numbers':
                processed_text = _remove_numbers(processed_text)

        # 根据优化策略进一步处理
        if optimize_strategy == "summary" and generate_summary:
            # 摘要策略
            summary = _generate_text_summary(processed_text, summary_ratio=0.3)
            processed_text = summary
        elif optimize_strategy == "chunk" and max_length:
            # 分块处理
            processed_text = _chunk_content(processed_text, max_length)
        elif optimize_strategy == "smart" and max_length and len(processed_text) > max_length:
            # 智能优化
            processed_text = _smart_optimize_content(processed_text, max_length)

        # 长度限制
        original_length = len(processed_text)
        if max_length and len(processed_text) > max_length:
            processed_text = processed_text[:max_length] + "..."

        # 统计信息
        stats = _calculate_text_stats(processed_text)

        result = {
            'success': True,
            'processed_text': processed_text,
            'original_length': len(content),
            'processed_length': len(processed_text),
            'reduction_ratio': (len(content) - len(processed_text)) / len(content),
            'stats': stats,
            'optimization_strategy': optimize_strategy
        }

        # 生成摘要（如果未在优化中生成）
        if generate_summary and optimize_strategy != "summary":
            summary = _generate_text_summary(processed_text)
            result['summary'] = summary

        # 提取关键词
        if extract_keywords:
            keywords = _extract_text_keywords(processed_text, keyword_count)
            result['keywords'] = keywords

        return result

    except Exception as e:
        return {
            'success': False,
            'error': f'文本处理错误: {str(e)}',
            'processed_text': '',
            'original_length': 0,
            'processed_length': 0,
            'stats': {},
            'optimization_strategy': optimize_strategy
        }


def _remove_extra_spaces(text: str) -> str:
    """移除多余空格"""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _remove_special_chars(text: str) -> str:
    """移除特殊字符"""
    pattern = r'[^\w\s\u4e00-\u9fff.,!?;:()\-\'\"]'
    return re.sub(pattern, '', text)


def _normalize_newlines(text: str) -> str:
    """标准化换行符"""
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text


def _remove_numbers(text: str) -> str:
    """移除数字"""
    return re.sub(r'\d+', '', text)


def _smart_optimize_content(text: str, max_length: int) -> str:
    """智能优化内容"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # 给句子打分
    scored_sentences = []
    for sentence in sentences:
        score = _score_sentence_importance(sentence)
        scored_sentences.append((sentence, score))

    # 按重要性排序
    scored_sentences.sort(key=lambda x: x[1], reverse=True)

    # 选择最重要的句子
    result = ""
    for sentence, score in scored_sentences:
        if len(result) + len(sentence) + 2 <= max_length:
            result += sentence + ". "
        else:
            break

    return result.strip() if result else text[:max_length]


def _score_sentence_importance(sentence: str) -> float:
    """给句子重要性打分"""
    score = 0.0
    sentence_lower = sentence.lower()

    # 关键词加分
    important_keywords = [
        '重要', '关键', '注意', '警告', '示例', '代码',
        'important', 'key', 'note', 'warning', 'example', 'code'
    ]

    for keyword in important_keywords:
        if keyword in sentence_lower:
            score += 2.0

    # 长度适中加分
    sentence_length = len(sentence)
    if 20 <= sentence_length <= 200:
        score += 1.0

    return score


def _chunk_content(text: str, max_chunk_size: int) -> str:
    """分块处理内容"""
    paragraphs = re.split(r'\n\s*\n', text)

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 <= max_chunk_size:
            current_chunk += paragraph + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks[0] if chunks else ""


def _calculate_text_stats(text: str) -> Dict[str, int]:
    """计算文本统计信息"""
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    word_count = len(words)
    sentence_count = len(sentences)

    return {
        'char_count': len(text),
        'word_count': word_count,
        'sentence_count': sentence_count,
        'paragraph_count': text.count('\n\n') + 1,
        'avg_word_length': sum(len(word) for word in words) / word_count if word_count > 0 else 0,
        'avg_sentence_length': word_count / sentence_count if sentence_count > 0 else 0
    }


def _generate_text_summary(text: str, summary_ratio: float = 0.3) -> str:
    """生成文本摘要"""
    if not text:
        return ""

    # 按句子分割
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # 给句子打分
    scored_sentences = []
    for sentence in sentences:
        score = _score_sentence_importance(sentence)
        scored_sentences.append((sentence, score))

    # 按重要性排序
    scored_sentences.sort(key=lambda x: x[1], reverse=True)

    # 选择最重要的句子
    summary_length = max(1, int(len(sentences) * summary_ratio))
    summary_sentences = [s[0] for s in scored_sentences[:summary_length]]

    # 按原文顺序排序
    summary_sentences_sorted = []
    for sentence in sentences:
        if sentence in summary_sentences:
            summary_sentences_sorted.append(sentence)

    return '. '.join(summary_sentences_sorted) + '.'


def _extract_text_keywords(text: str, count: int = 10) -> List[Dict[str, Union[str, int]]]:
    """提取文本关键词"""
    if not text:
        return []

    # 分词
    words = text.lower().split()

    # 移除停用词和短词
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    filtered_words = [
        word.strip(string.punctuation)
        for word in words
        if len(word) > 2 and word not in stop_words
    ]

    # 计算词频
    word_freq = Counter(filtered_words)

    # 返回前N个关键词
    keywords = []
    for word, freq in word_freq.most_common(count):
        keywords.append({
            'word': word,
            'frequency': freq,
            'score': freq / len(filtered_words) if filtered_words else 0
        })

    return keywords

# ==================== 处理策略层 ====================

def _handle_raw_mode(content: str, response, max_content_length: Optional[int]) -> Dict:
    """处理raw模式"""
    content_length = len(content)

    if max_content_length and content_length > max_content_length:
        truncated_content = content[:max_content_length] + "..."
        return {
            'success': True,
            'status_code': response.status_code,
            'content': truncated_content,
            'headers': dict(response.headers),
            'url': response.url,
            'encoding': response.encoding,
            'content_type': response.headers.get('content-type', ''),
            'content_length': content_length,
            'content_optimized': False,
            'optimization_strategy': 'raw',
            'content_truncated': True
        }
    else:
        return {
            'success': True,
            'status_code': response.status_code,
            'content': content,
            'headers': dict(response.headers),
            'url': response.url,
            'encoding': response.encoding,
            'content_type': response.headers.get('content-type', ''),
            'content_length': content_length,
            'content_optimized': False,
            'optimization_strategy': 'raw',
            'content_truncated': False
        }


def _handle_parse_mode(content: str, response, max_content_length: Optional[int], url: str) -> Dict:
    """处理parse模式 - 使用集成的HTML解析"""
    content_type = response.headers.get('content-type', '')

    if _is_html_content(content_type):
        # HTML内容，使用集成的HTML解析
        parse_result = _parse_html_impl(content, base_url=url)

        if parse_result['success']:
            parsed_content = parse_result['content']

            # 长度限制
            if max_content_length and len(parsed_content) > max_content_length:
                parsed_content = parsed_content[:max_content_length] + "..."

            return {
                'success': True,
                'status_code': response.status_code,
                'content': parsed_content,
                'headers': dict(response.headers),
                'url': response.url,
                'encoding': response.encoding,
                'content_type': content_type,
                'content_length': len(content),
                'content_optimized': True,
                'optimization_strategy': 'parse',
                'content_truncated': len(parsed_content) < len(content)
            }
        else:
            # HTML解析失败，返回原始内容
            return _handle_raw_mode(content, response, max_content_length)
    else:
        # 非HTML内容，直接返回原始
        return _handle_raw_mode(content, response, max_content_length)


def _handle_smart_mode(content: str, response, max_content_length: Optional[int], url: str) -> Dict:
    """处理smart模式 - 使用集成的HTML解析和文本处理"""
    content_type = response.headers.get('content-type', '')

    if _is_html_content(content_type):
        # HTML内容，进行完整优化流程
        parse_result = _parse_html_impl(content, base_url=url)

        if parse_result['success']:
            # 使用集成的文本处理
            process_result = _process_text_impl(
                parse_result['content'],
                max_length=max_content_length,
                generate_summary=False,
                optimize_strategy="smart"
            )

            if process_result['success']:
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'content': process_result['processed_text'],
                    'headers': dict(response.headers),
                    'url': response.url,
                    'encoding': response.encoding,
                    'content_type': content_type,
                    'content_length': len(content),
                    'content_optimized': True,
                    'optimization_strategy': 'smart',
                    'content_truncated': process_result['processed_length'] < len(parse_result['content'])
                }
            else:
                # 文本处理失败，返回解析后的内容
                return _handle_parse_mode(content, response, max_content_length, url)
        else:
            # HTML解析失败，返回原始内容
            return _handle_raw_mode(content, response, max_content_length)
    else:
        # 非HTML内容，直接返回原始
        return _handle_raw_mode(content, response, max_content_length)

# ==================== HTTP请求核心实现 ====================

def _get_http_impl(
    url: str,
    method: str = "GET",
    headers: Optional[Dict] = None,
    data: Optional[Dict] = None,
    timeout: int = 30,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    max_content_length: Optional[int] = 15000,
    optimize_strategy: str = "raw",
    encoding: Optional[str] = None  # 🆕 新增编码参数
) -> Dict[str, Union[str, int, bool, Dict]]:
    """
    HTTP获取工具（完全集成版）

    Args:
        url: 请求的URL地址
        method: 请求方法，GET或POST
        headers: 自定义请求头
        data: POST请求的数据
        timeout: 请求超时时间（秒）
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）
        max_content_length: 最大内容长度
        optimize_strategy: 内容优化策略
            - "raw": 返回原始内容
            - "parse": HTML解析为纯文本，其他返回原始
            - "smart": HTML优化处理，其他返回原始
        encoding: 手动指定编码（可选）
            - 用于解决中文网站乱码问题
            - 示例："GBK"（人民网、央视网等）
            - 示例："UTF-8"（现代网站）
            - 不指定时使用自动检测

    Returns:
        Dict: 包含响应状态、内容、头信息等的字典
    """

    # 验证策略参数
    valid_strategies = ["raw", "parse", "smart"]
    if optimize_strategy not in valid_strategies:
        return _build_error_response(
            f'无效的优化策略: {optimize_strategy}，可用策略: {valid_strategies}',
            0, url, optimize_strategy
        )

    # 默认请求头
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Neko-Crawler/4.0'
    }

    # 合并请求头
    if headers:
        default_headers.update(headers)

    # 重试机制
    for attempt in range(max_retries):
        try:
            # 发送请求
            if method.upper() == "GET":
                response = requests.get(
                    url,
                    headers=default_headers,
                    timeout=timeout,
                    allow_redirects=True
                )
            elif method.upper() == "POST":
                response = requests.post(
                    url,
                    headers=default_headers,
                    data=data,
                    timeout=timeout,
                    allow_redirects=True
                )
            else:
                return _build_error_response(
                    f'不支持的请求方法: {method}',
                    attempt + 1, url, optimize_strategy
                )

            # 检查响应状态
            if response.status_code == 200:
                if encoding:
                    response.encoding = encoding
                content = response.text

                # 根据策略分发处理
                if optimize_strategy == "raw":
                    return _handle_raw_mode(content, response, max_content_length)
                elif optimize_strategy == "parse":
                    return _handle_parse_mode(content, response, max_content_length, url)
                elif optimize_strategy == "smart":
                    return _handle_smart_mode(content, response, max_content_length, url)

            else:
                # 非200状态码
                return {
                    'success': True,  # 请求成功，只是服务器返回错误
                    'status_code': response.status_code,
                    'content': response.text,
                    'headers': dict(response.headers),
                    'url': response.url,
                    'encoding': response.encoding,
                    'error': f'HTTP状态码: {response.status_code}',
                    'attempt': attempt + 1,
                    'content_optimized': False,
                    'optimization_strategy': optimize_strategy
                }

        except requests.exceptions.Timeout:
            error_msg = f"请求超时 (尝试 {attempt + 1}/{max_retries})"
        except requests.exceptions.ConnectionError:
            error_msg = f"连接错误 (尝试 {attempt + 1}/{max_retries})"
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP错误: {e} (尝试 {attempt + 1}/{max_retries})"
        except requests.exceptions.RequestException as e:
            error_msg = f"请求异常: {e} (尝试 {attempt + 1}/{max_retries})"
        except Exception as e:
            error_msg = f"未知错误: {e} (尝试 {attempt + 1}/{max_retries})"

        # 如果不是最后一次尝试，等待后重试
        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    # 所有重试都失败
    return _build_error_response(error_msg, max_retries, url, optimize_strategy)

# ==================== 主工具接口 ====================

@tool
def get_http(
    url: str,
    method: str = "GET",
    headers: Optional[Dict] = None,
    data: Optional[Dict] = None,
    timeout: int = 30,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    max_content_length: Optional[int] = 15000,
    optimize_strategy: str = "raw",
    encoding: Optional[str] = None  # 🆕 新增编码参数
) -> Dict[str, Union[str, int, bool, Dict]]:
    """
    HTTP请求实现函数（完全集成版）

    Args:
        url: 请求的URL地址
        method: 请求方法，GET或POST
        headers: 自定义请求头
        data: POST请求的数据
        timeout: 请求超时时间（秒）
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）
        max_content_length: 最大内容长度
        optimize_strategy: 内容优化策略
            - "raw": 返回原始内容
            - "parse": HTML解析为纯文本，其他返回原始
            - "smart": HTML优化处理，其他返回原始
        encoding: 手动指定编码（可选）
            - 用于解决中文网站乱码问题
            - 示例："GBK"
            - 示例："UTF-8"（人民网、中文网站）
            - 不指定时使用自动检测

    Returns:
        Dict: 包含响应状态、内容、头信息等的字典
    """
    return _get_http_impl(
        url=url,
        method=method,
        headers=headers,
        data=data,
        timeout=timeout,
        max_retries=max_retries,
        retry_delay=retry_delay,
        max_content_length=max_content_length,
        optimize_strategy=optimize_strategy,
        encoding=encoding  # 🆕 新增参数传递
    )


# ==================== 测试函数 ====================

def test_http_client_integrated():
    """测试完全集成版HTTP客户端功能"""
    print("🐱 测试完全集成版HTTP获取工具...")

    test_urls = [
        ("http://httpbin.org/get", "JSON页面"),
        ("http://httpbin.org/html", "HTML页面"),
        ("http://example.com", "标准HTML页面")
    ]

    for url, description in test_urls:
        print(f"\n🎯 测试URL: {description}")
        print("-" * 40)

        for strategy in ["raw", "parse", "smart"]:
            print(f"📋 测试模式: {strategy}")
            result = _get_http_impl(
                url,
                max_content_length=5000,
                optimize_strategy=strategy
            )

            print(f"请求成功: {result['success']}")
            print(f"状态码: {result.get('status_code', 'N/A')}")
            print(f"优化策略: {result.get('optimization_strategy', 'N/A')}")
            print(f"内容优化: {result.get('content_optimized', False)}")

            if result['success']:
                content_preview = result['content'][:100] if result['content'] else "[空内容]"
                print(f"内容预览: {content_preview}...")
                print("✅ 模式正常工作")
            else:
                print(f"❌ 错误: {result.get('error', '未知错误')}")

    return True


if __name__ == "__main__":
    success = test_http_client_integrated()
    if success:
        print("\n✅ 完全集成版HTTP客户端测试通过！")
    else:
        print("\n❌ 完全集成版HTTP客户端测试失败！")
