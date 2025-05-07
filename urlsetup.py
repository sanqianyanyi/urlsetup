import argparse
import requests
import os
import sys
import random
import time
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 预定义的User-Agent列表
WINDOWS_UA = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 11.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/115.0.1901.200 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Brave/120.0.0.0 Chrome/120.0.0.0 Safari/537.3'
]

LINUX_UA = [
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.3',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.60',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chromium/120.0.6099.71 Safari/537.3',
    'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0'
]

def get_random_ua():
    """随机返回Windows或Linux的User-Agent"""
    return random.choice(WINDOWS_UA + LINUX_UA)

def normalize_url(original_url):
    """自动补全URL协议头并进行标准化处理"""
    parsed = urlparse(original_url)
    if not parsed.scheme:
        for protocol in ['https://', 'http://']:
            normalized = protocol + original_url
            try:
                # 使用更可靠的GET方法测试
                requests.get(normalized, 
                           timeout=0.3,
                           headers={'User-Agent': get_random_ua()},
                           allow_redirects=False)
                return normalized
            except:
                continue
        return 'http://' + original_url
    return original_url

def check_url(raw_url):
    """带UA轮换的检测函数"""
    normalized_url = normalize_url(raw_url)
    last_error = None
    
    for attempt in range(3):
        try:
            current_url = normalized_url.replace('https://', 'http://') if (attempt % 2 == 1) else normalized_url
            response = requests.head(current_url,
                                   timeout=0.3,
                                   allow_redirects=True,
                                   headers={'User-Agent': get_random_ua()})
            return (raw_url, response.url, response.status_code, None)
        except Exception as e:
            last_error = e
            time.sleep(0.1)  # 增加尝试间隔
    return (raw_url, normalized_url, None, str(last_error))

def main():
    parser = argparse.ArgumentParser(
        description='智能UA轮换URL检测工具',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''使用示例：
  基本检测：
  python url_checker.py -f urls.txt -o results.csv
  
  高级模式：
  python url_checker.py -f urls.txt -o results.csv -s 10

功能特性：
  ✔ 每次请求使用随机UA头（5 Win + 5 Linux）
  ✔ 自动协议补全和重定向跟踪
  ✔ 三阶段检测机制（300ms超时/次）
  ✔ 实时结果显示和CSV输出
''')
    parser.add_argument('-f', '--file', required=True, help='URL列表文件路径')
    parser.add_argument('-o', '--output', required=True, help='输出文件路径（CSV格式）')
    parser.add_argument('-s', '--threads', type=int, default=3, 
                      help='并发线程数（默认：3，最大建议50）')
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"\033[91m错误：输入文件 '{args.file}' 不存在\033[0m")
        sys.exit(1)

    with open(args.file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    if not urls:
        print("\033[91m错误：文件中没有有效的URL\033[0m")
        sys.exit(2)

    print(f"\n🛡 启用UA轮换模式 | 线程数：{args.threads} | 超时：300ms/次\n")
    print("开始检测...\n")

    print_lock = threading.Lock()
    results = []
    processed = 0
    total = len(urls)
    
    def process_result(future):
        nonlocal processed
        with print_lock:
            processed += 1
            raw_url, final_url, status, error = future.result()
            if status:
                results.append(f'"{final_url}",{status}')
                print(f"[{processed}/{total}] \033[94m{raw_url}\033[0m → \033[36m{final_url}\033[0m (\033[1m{status}\033[0m)")
            else:
                print(f"[{processed}/{total}] \033[90m{raw_url}\033[0m → \033[31m{error[:50]}\033[0m")

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(check_url, url): url for url in urls}
        try:
            for future in as_completed(futures):
                process_result(future)
        except KeyboardInterrupt:
            print("\n\033[91m用户中断，正在保存已检测结果...\033[0m")
            executor.shutdown(wait=False, cancel_futures=True)

    # 保存结果
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write("FINAL_URL,STATUS_CODE\n")
        f.write("\n".join(results))
    
    print(f"\n✅ 检测完成！成功检测：{len(results)}，失败：{len(urls)-len(results)}")
    print(f"   结果文件保存至：\033[1m{args.output}\033[0m")

if __name__ == "__main__":
    main()