"""
网页抓取器模块，负责发送HTTP请求，获取网页内容。
"""
import time
import requests
from typing import Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup


class Scraper:
    """
    网页抓取器类，用于抓取指定URL的页面内容。
    
    属性:
        session: requests.Session对象，用于发送HTTP请求
        delay: 请求间隔时间（秒）
        last_request_time: 上次请求的时间戳
        max_retries: 最大重试次数
        retry_delay: 重试间隔时间（秒）
    """
    
    def __init__(self, user_agent: str, delay: float = 1.0, max_retries: int = 3, retry_delay: float = 2.0):
        """
        初始化抓取器
        
        参数:
            user_agent: 请求头中的User-Agent
            delay: 请求间隔时间（秒），默认为1.0秒
            max_retries: 最大重试次数，默认为3次
            retry_delay: 重试间隔时间（秒），默认为2.0秒
        """
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
        self.delay = delay
        self.last_request_time = 0
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
    def fetch_page(self, url: str) -> Optional[str]:
        """
        抓取指定URL的页面内容
        
        参数:
            url: 要抓取的页面URL
            
        返回:
            页面的HTML内容，如果抓取失败则返回None
        """
        # 实现请求延迟
        current_time = time.time()
        sleep_time = max(0, self.delay - (current_time - self.last_request_time))
        if sleep_time > 0:
            time.sleep(sleep_time)
        
        retries = 0
        while retries <= self.max_retries:
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()  # 如果状态码不是200，抛出HTTPError异常
                
                # 更新最后请求时间
                self.last_request_time = time.time()
                
                # 确保中文内容正确显示
                response.encoding = 'utf-8'
                
                return response.text
            
            except requests.exceptions.HTTPError as e:
                # HTTP错误（如404, 500等）
                print(f"HTTP错误: {e}")
                if 500 <= e.response.status_code < 600:
                    # 服务器错误，可以重试
                    retries += 1
                    if retries <= self.max_retries:
                        print(f"重试 ({retries}/{self.max_retries})...")
                        time.sleep(self.retry_delay)
                        continue
                return None
            
            except requests.exceptions.ConnectionError:
                # 连接错误
                print(f"连接错误: 无法连接到 {url}")
                retries += 1
                if retries <= self.max_retries:
                    print(f"重试 ({retries}/{self.max_retries})...")
                    time.sleep(self.retry_delay)
                    continue
                return None
            
            except requests.exceptions.Timeout:
                # 超时错误
                print(f"超时错误: {url} 请求超时")
                retries += 1
                if retries <= self.max_retries:
                    print(f"重试 ({retries}/{self.max_retries})...")
                    time.sleep(self.retry_delay)
                    continue
                return None
            
            except requests.exceptions.RequestException as e:
                # 其他请求异常
                print(f"请求错误: {e}")
                return None
                
    def get_next_page_url(self, html: str, base_url: str) -> Optional[str]:
        """
        从HTML中提取"下一页"的URL
        
        参数:
            html: 当前页面的HTML内容
            base_url: 当前页面的URL
            
        返回:
            下一页的URL，如果没有下一页则返回None
        """
        if not html:
            return None
            
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找包含"下一页"文本的链接
        # 针对游戏攻略网站的特定结构进行查找
        next_link = soup.find('a', text='下一页')
        if not next_link:
            # 尝试其他可能的"下一页"链接模式
            next_link = soup.find('a', text=lambda t: t and '下一页' in t)
            
        if not next_link:
            # 尝试查找带有特定class的下一页链接
            next_link = soup.find('a', class_=lambda c: c and ('next' in c.lower() or 'nextpage' in c.lower()))
            
        # 如果找到了下一页链接
        if next_link and 'href' in next_link.attrs:
            next_url = next_link['href']
            
            # 处理相对URL，转换为绝对URL
            if not next_url.startswith(('http://', 'https://')):
                next_url = urljoin(base_url, next_url)
                
            # 循环检测：如果下一页URL与当前页面URL相同，则认为没有下一页
            if next_url == base_url:
                print(f"检测到循环链接: {next_url}")
                return None
                
            # 记录找到的下一页URL
            print(f"找到下一页链接: {next_url}")
            return next_url
            
        # 没有找到下一页链接
        print("未找到下一页链接")
        return None