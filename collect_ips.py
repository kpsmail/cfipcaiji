import requests
from bs4 import BeautifulSoup
import re
import os
import ssl
from urllib3.util.ssl_ import create_urllib3_context
from requests.adapters import HTTPAdapter

# 自定义 SSL 适配器，强制使用 TLS 1.2
class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ssl_version=ssl.PROTOCOL_TLSv1_2)
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

# 目标 URL 列表
urls = ['https://api.uouin.com/cloudflare.html', 
        'https://ip.164746.xyz']

# IP 地址正则表达式
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

# 如果 ip.txt 存在则删除
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 创建文件存储 IP 地址
with open('ip.txt', 'w') as file:
    for url in urls:
        # 创建带有自定义 TLS 适配器的会话
        session = requests.Session()
        session.mount('https://', TLSAdapter())
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        
        # 发送 HTTP 请求获取网页内容
        try:
            response = session.get(url, timeout=10, headers=headers)
            response.raise_for_status()  # 检查 HTTP 状态码
            
            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 根据网站结构查找包含 IP 地址的元素
            if url == 'https://api.uouin.com/cloudflare.html':
                elements = soup.find_all('tr')
            elif url == 'https://ip.164746.xyz':
                elements = soup.find_all('tr')
            else:
                elements = soup.find_all('li')
            
            # 提取 IP 地址并写入指定格式
            for element in elements:
                element_text = element.get_text()
                ip_matches = re.findall(ip_pattern, element_text)
                
                # 写入 IP 地址到文件，格式为 {ip}:port#CF优选port
                for ip in ip_matches:
                    file.write(f'{ip}:443#CF优选443\n')
                    file.write(f'{ip}:8443#CF优选8443\n')
                    file.write(f'{ip}:2053#CF优选2053\n')
                    
        except requests.exceptions.RequestException as e:
            print(f"无法访问 {url}: {e}")
            continue

print('IP 地址已保存到 ip.txt 文件中。')
