import requests
import json
import time
from typing import Union, List, Dict, Any
from langchain_core.tools import tool, InjectedToolCallId

@tool
def send_payloads(url: str,
                  payloads: Union[Dict[str, Any], List[Dict[str, Any]]],
                  method: str = 'GET',
                  headers: Dict[str, str] = None,
                  timeout: int = 10,
                  delay: float = 0,
                  verbose: bool = False) -> str:
    """
    向指定 URL 发送单个或多个自定义 payload 并返回响应结果

    参数:
        url (str): 目标 URL
        payloads: 单个 payload 字典或 payload 字典列表
        method (str): HTTP 方法，'GET' 或 'POST'
        headers (dict): 请求头信息
        timeout (int): 超时时间（秒）
        delay (float): 每次请求之间的延迟（秒）
        verbose (bool): 是否打印详细请求信息

    返回:
        list: 包含每个 payload 响应结果的字典列表
    """

    # 默认请求头
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    # 确保 payloads 是列表形式
    if isinstance(payloads, dict):
        payloads = [payloads]

    results = []

    for i, payload in enumerate(payloads):
        try:
            # 添加延迟（除了第一个请求）
            if i > 0 and delay > 0:
                time.sleep(delay)

            if verbose:
                print(f"发送 payload {i + 1}/{len(payloads)}: {payload}")

            # 发送请求
            if method.upper() == 'GET':
                response = requests.get(
                    url,
                    params=payload,
                    headers=headers,
                    timeout=timeout,
                    allow_redirects=True
                )
            elif method.upper() == 'POST':
                # 根据 Content-Type 决定如何发送数据
                content_type = headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    data = json.dumps(payload)
                else:
                    data = payload

                response = requests.post(
                    url,
                    data=data,
                    headers=headers,
                    timeout=timeout,
                    allow_redirects=True
                )
            else:
                raise ValueError(f"不支持的 HTTP 方法: {method}")

            # 收集响应信息
            result = {
                'payload': payload,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text,
                'url': response.url,  # 最终 URL（考虑重定向）
                'history': [resp.url for resp in response.history],  # 重定向历史
                'encoding': response.encoding,
                'cookies': dict(response.cookies),
                'elapsed': response.elapsed.total_seconds(),  # 请求耗时
                'success': True
            }

            if verbose:
                print(f"状态码: {response.status_code}")
                print(f"响应大小: {len(response.text)} 字符")
                print(f"最终 URL: {response.url}")
                print("-" * 50)

        except requests.exceptions.RequestException as e:
            # 请求失败的情况
            result = {
                'payload': payload,
                'status_code': None,
                'error': str(e),
                'success': False
            }

            if verbose:
                print(f"请求失败: {e}")
                print("-" * 50)

        results.append(result)

    return "results:" + str(results)


def analyze_responses(results: List[Dict[str, Any]]) -> None:
    """
    分析响应结果并生成报告

    参数:
        results: send_payloads 函数的返回结果
    """
    print("=" * 60)
    print("响应分析报告")
    print("=" * 60)

    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful

    print(f"总请求数: {len(results)}")
    print(f"成功: {successful}")
    print(f"失败: {failed}")
    print()

    # 状态码统计
    status_codes = {}
    for result in results:
        if result['success']:
            code = result['status_code']
            status_codes[code] = status_codes.get(code, 0) + 1

    if status_codes:
        print("状态码分布:")
        for code, count in status_codes.items():
            print(f"  {code}: {count} 次")
        print()

    # 显示每个请求的简要信息
    for i, result in enumerate(results):
        print(f"请求 #{i + 1}:")
        print(f"  Payload: {result['payload']}")

        if result['success']:
            print(f"  状态码: {result['status_code']}")
            print(f"  响应大小: {len(result['content'])} 字符")
            print(f"  最终 URL: {result['url']}")
            print(f"  耗时: {result['elapsed']:.2f} 秒")
        else:
            print(f"  错误: {result['error']}")
        print()


# 使用示例
if __name__ == "__main__":
    # 示例 1: 发送单个 payload
    print("示例 1: 发送单个 payload")
    url = "https://httpbin.org/post"
    payload = {
        'username': 'testuser',
        'password': 'testpass',
        'action': 'login'
    }

    results = send_payloads(
        url=url,
        payloads=payload,
        method='POST',
        headers={'Content-Type': 'application/json'},
        verbose=True
    )

    analyze_responses(results)

    # 示例 2: 发送多个 payload (SQL 注入测试示例)
    print("\n示例 2: 发送多个 payload (SQL 注入测试)")
    url = "https://httpbin.org/get"
    payloads = [
        {'id': '1'},  # 正常请求
        {'id': "1'"},  # 单引号测试
        {'id': '1 OR 1=1'},  # SQL 注入尝试
        {'id': '1; DROP TABLE users'},  # 另一个 SQL 注入尝试
    ]

    results = send_payloads(
        url=url,
        payloads=payloads,
        method='GET',
        delay=1,  # 每次请求间隔 1 秒
        verbose=True
    )

    analyze_responses(results)

    # 示例 3: 保存结果到文件
    print("\n示例 3: 保存结果到文件")
    with open('payload_results.json', 'w', encoding='utf-8') as f:
        # 只保存必要信息，避免序列化问题
        simplified_results = []
        for result in results:
            simplified = {
                'payload': result['payload'],
                'status_code': result.get('status_code'),
                'success': result['success'],
                'content_length': len(result.get('content', '')) if result.get('content') else 0
            }
            simplified_results.append(simplified)

        json.dump(simplified_results, f, indent=2, ensure_ascii=False)

    print("结果已保存到 payload_results.json")