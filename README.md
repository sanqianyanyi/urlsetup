# urlsetup
用于批量检测URL存活的小工具
# 使用方法
options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  URL列表文件路径
  -o OUTPUT, --output OUTPUT
                        输出文件路径（CSV格式）
  -s THREADS, --threads THREADS
                        并发线程数（默认：3，最大建议50）

使用示例：
  基本检测：
  python url_checker.py -f urls.txt -o results.csv
  高级模式：
  python url_checker.py -f urls.txt -o results.csv -s 10

# 功能特性
每次请求使用随机UA头（5 Win + 5 Linux）
自动协议补全和重定向跟踪
三阶段检测机制（300ms超时/次）
实时结果显示和CSV输出
