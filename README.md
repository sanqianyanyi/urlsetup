# urlsetup
用于批量检测URL存活的小工具
# 使用方法
options:
  -h, --help            show this help message and exit <br>
  -f FILE, --file FILE  URL列表文件路径 <br>
  -o OUTPUT, --output OUTPUT <br>
                        输出文件路径（CSV格式）<br>
  -s THREADS, --threads THREADS <br>
                        并发线程数（默认：3，最大建议50） <br>
<br>
使用示例：<br>
  基本检测：<br>
  python url_checker.py -f urls.txt -o results.csv<br>
  高级模式：<br>
  python url_checker.py -f urls.txt -o results.csv -s 10<br>

# 功能特性
每次请求使用随机UA头（5 Win + 5 Linux）<br>
自动协议补全和重定向跟踪<br>
三阶段检测机制（300ms超时/次）<br>
实时结果显示和CSV输出<br>
