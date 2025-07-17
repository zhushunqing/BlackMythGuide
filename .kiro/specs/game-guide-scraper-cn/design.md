# 设计文档

## 概述

本设计文档详细描述了"黑神话悟空"游戏攻略爬虫的技术实现方案。该爬虫将从指定的起始URL开始，抓取所有相关页面内容，包括"下一页"链接指向的所有页面，并将内容整理成一本结构化的Markdown格式攻略书。

## 架构

系统将采用模块化设计，主要包含以下几个核心组件：

1. **网页抓取器（Scraper）**：负责发送HTTP请求，获取网页内容。
2. **内容解析器（Parser）**：负责从HTML中提取有用信息，如文本、图片等。
3. **图片下载器（ImageDownloader）**：负责下载和保存图片文件。
4. **内容组织器（ContentOrganizer）**：负责将解析后的内容组织成结构化的文档。
5. **Markdown生成器（MarkdownGenerator）**：负责将结构化内容转换为Markdown格式。
6. **主控制器（Controller）**：协调各组件工作，管理整个抓取和生成过程。

系统架构图如下：

```mermaid
graph TD
    A[主控制器] --> B[网页抓取器]
    A --> C[内容解析器]
    A --> D[图片下载器]
    A --> E[内容组织器]
    A --> F[Markdown生成器]
    B --> C
    C --> D
    C --> E
    E --> F
```## 
组件与接口

### 1. 网页抓取器（Scraper）

**职责**：发送HTTP请求，获取网页内容。

**接口**：
```python
class Scraper:
    def __init__(self, user_agent: str, delay: float = 1.0):
        """
        初始化抓取器
        
        参数:
            user_agent: 请求头中的User-Agent
            delay: 请求间隔时间（秒）
        """
        pass
        
    def fetch_page(self, url: str) -> str:
        """
        抓取指定URL的页面内容
        
        参数:
            url: 要抓取的页面URL
            
        返回:
            页面的HTML内容
        """
        pass
        
    def get_next_page_url(self, html: str, base_url: str) -> str:
        """
        从HTML中提取"下一页"的URL
        
        参数:
            html: 当前页面的HTML内容
            base_url: 当前页面的URL
            
        返回:
            下一页的URL，如果没有下一页则返回None
        """
        pass
```

### 2. 内容解析器（Parser）

**职责**：从HTML中提取有用信息，如文本、图片等。

**接口**：
```python
class Parser:
    def parse_content(self, html: str) -> dict:
        """
        解析HTML内容，提取标题、正文、图片URL等
        
        参数:
            html: 页面的HTML内容
            
        返回:
            包含解析结果的字典，格式如下：
            {
                'title': '页面标题',
                'content': [
                    {'type': 'text', 'value': '文本内容'},
                    {'type': 'image', 'url': '图片URL', 'alt': '图片描述'}
                ]
            }
        """
        pass
        
    def extract_title(self, html: str) -> str:
        """
        从HTML中提取页面标题
        
        参数:
            html: 页面的HTML内容
            
        返回:
            页面标题
        """
        pass
        
    def extract_content(self, html: str) -> list:
        """
        从HTML中提取正文内容
        
        参数:
            html: 页面的HTML内容
            
        返回:
            内容元素列表
        """
        pass
        
    def extract_images(self, html: str) -> list:
        """
        从HTML中提取图片URL
        
        参数:
            html: 页面的HTML内容
            
        返回:
            图片信息列表
        """
        pass
```

### 3. 图片下载器（ImageDownloader）

**职责**：下载和保存图片文件。

**接口**：
```python
class ImageDownloader:
    def __init__(self, output_dir: str, delay: float = 0.5):
        """
        初始化图片下载器
        
        参数:
            output_dir: 图片保存目录
            delay: 下载间隔时间（秒）
        """
        pass
        
    def download_image(self, url: str, filename: str = None) -> str:
        """
        下载图片并保存到本地
        
        参数:
            url: 图片URL
            filename: 保存的文件名，如果为None则自动生成
            
        返回:
            保存后的本地文件路径
        """
        pass
        
    def download_all_images(self, image_list: list) -> dict:
        """
        批量下载图片
        
        参数:
            image_list: 图片信息列表
            
        返回:
            图片URL到本地路径的映射字典
        """
        pass
```### 4
. 内容组织器（ContentOrganizer）

**职责**：将解析后的内容组织成结构化的文档。

**接口**：
```python
class ContentOrganizer:
    def __init__(self):
        """
        初始化内容组织器
        """
        pass
        
    def add_page_content(self, page_content: dict):
        """
        添加一个页面的内容
        
        参数:
            page_content: 页面内容字典
        """
        pass
        
    def organize_content(self) -> dict:
        """
        组织所有内容，生成结构化文档
        
        返回:
            结构化文档字典
        """
        pass
        
    def generate_toc(self) -> list:
        """
        生成目录
        
        返回:
            目录项列表
        """
        pass
```

### 5. Markdown生成器（MarkdownGenerator）

**职责**：将结构化内容转换为Markdown格式。

**接口**：
```python
class MarkdownGenerator:
    def __init__(self, image_path_mapping: dict = None):
        """
        初始化Markdown生成器
        
        参数:
            image_path_mapping: 图片URL到本地路径的映射字典
        """
        pass
        
    def generate_markdown(self, content: dict) -> str:
        """
        生成Markdown文档
        
        参数:
            content: 结构化内容字典
            
        返回:
            Markdown格式的文档字符串
        """
        pass
        
    def generate_toc_markdown(self, toc: list) -> str:
        """
        生成目录的Markdown
        
        参数:
            toc: 目录项列表
            
        返回:
            目录的Markdown字符串
        """
        pass
        
    def save_markdown(self, markdown: str, output_file: str):
        """
        保存Markdown到文件
        
        参数:
            markdown: Markdown字符串
            output_file: 输出文件路径
        """
        pass
```

### 6. 主控制器（Controller）

**职责**：协调各组件工作，管理整个抓取和生成过程。

**接口**：
```python
class Controller:
    def __init__(self, config: dict):
        """
        初始化控制器
        
        参数:
            config: 配置字典
        """
        pass
        
    def run(self):
        """
        运行爬虫
        """
        pass
        
    def report_progress(self, message: str, percentage: float = None):
        """
        报告进度
        
        参数:
            message: 进度消息
            percentage: 完成百分比
        """
        pass
```## 数据模型


### 1. 页面内容模型

```python
{
    'url': '页面URL',
    'title': '页面标题',
    'page_number': 页码,
    'content': [
        {'type': 'text', 'value': '文本内容'},
        {'type': 'image', 'url': '图片URL', 'alt': '图片描述', 'local_path': '本地路径'}
    ]
}
```

### 2. 结构化文档模型

```python
{
    'title': '文档标题',
    'source_url': '原始URL',
    'toc': [
        {'level': 1, 'title': '章节标题', 'id': '章节ID'},
        {'level': 2, 'title': '小节标题', 'id': '小节ID'}
    ],
    'chapters': [
        {
            'title': '章节标题',
            'id': '章节ID',
            'content': [
                {'type': 'text', 'value': '文本内容'},
                {'type': 'image', 'url': '图片URL', 'alt': '图片描述', 'local_path': '本地路径'}
            ],
            'sections': [
                {
                    'title': '小节标题',
                    'id': '小节ID',
                    'content': [...]
                }
            ]
        }
    ]
}
```

### 3. 配置模型

```python
{
    'start_url': '起始URL',
    'user_agent': 'User-Agent字符串',
    'delay': 请求间隔时间（秒）,
    'output_dir': '输出目录',
    'output_file': '输出文件名',
    'download_images': 是否下载图片,
    'image_dir': '图片保存目录'
}
```## 错误
处理

系统将实现以下错误处理机制：

1. **网络错误处理**：
   - 实现请求重试机制，当请求失败时自动重试
   - 记录失败的URL，以便后续手动处理
   - 在连接超时或服务器错误时提供友好的错误信息

2. **解析错误处理**：
   - 当HTML结构不符合预期时，尝试使用备用解析策略
   - 记录无法解析的内容，以便后续手动处理
   - 确保即使部分内容解析失败，也不会影响整体流程

3. **图片下载错误处理**：
   - 当图片下载失败时，记录错误并继续处理其他图片
   - 提供图片URL到本地路径的映射，即使图片下载失败也能生成有效的Markdown

4. **文件操作错误处理**：
   - 在写入文件前检查目录是否存在，不存在则创建
   - 处理文件权限和磁盘空间不足等错误
   - 实现自动备份机制，防止数据丢失

## 测试策略

系统将采用以下测试策略：

1. **单元测试**：
   - 为每个组件编写单元测试，确保各个功能正常工作
   - 使用模拟（mock）对象测试依赖外部服务的组件
   - 测试各种边缘情况和错误处理路径

2. **集成测试**：
   - 测试组件之间的交互
   - 验证数据在组件之间的正确传递
   - 确保系统作为一个整体能够正常工作

3. **端到端测试**：
   - 使用真实的网页进行测试
   - 验证从抓取到生成Markdown的完整流程
   - 检查生成的Markdown文档是否符合预期

4. **性能测试**：
   - 测试系统在处理大量页面时的性能
   - 评估内存使用情况和执行时间
   - 确保系统能够处理目标网站的所有内容## 实现细节


### 1. 网页抓取实现

我们将使用Python的`requests`库来实现网页抓取功能。为了避免被目标网站封锁，我们将：

- 设置合理的User-Agent
- 实现请求延迟
- 处理HTTP错误和重定向

关键代码示例：

```python
import requests
import time
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self, user_agent, delay=1.0):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
        self.delay = delay
        self.last_request_time = 0
        
    def fetch_page(self, url):
        # 实现请求延迟
        current_time = time.time()
        sleep_time = max(0, self.delay - (current_time - self.last_request_time))
        if sleep_time > 0:
            time.sleep(sleep_time)
            
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'  # 确保中文正确显示
            self.last_request_time = time.time()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
            
    def get_next_page_url(self, html, base_url):
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'html.parser')
        next_link = soup.find('a', text='下一页')
        
        if next_link and 'href' in next_link.attrs:
            next_url = next_link['href']
            # 处理相对URL
            if not next_url.startswith('http'):
                from urllib.parse import urljoin
                next_url = urljoin(base_url, next_url)
            return next_url
        return None
```

### 2. 内容解析实现

我们将使用`BeautifulSoup`库来解析HTML内容。针对目标网站的特定结构，我们将：

- 提取页面标题
- 提取正文内容
- 提取图片URL和描述

关键代码示例：

```python
from bs4 import BeautifulSoup

class Parser:
    def parse_content(self, html):
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'html.parser')
        
        result = {
            'title': self.extract_title(soup),
            'content': self.extract_content(soup)
        }
        
        return result
        
    def extract_title(self, soup):
        # 提取页面标题
        title_tag = soup.find('title')
        if title_tag:
            # 处理标题，去除网站名称等
            title = title_tag.text.strip()
            if '-' in title:
                title = title.split('-')[0].strip()
            return title
        return "未知标题"
        
    def extract_content(self, soup):
        content = []
        
        # 找到主要内容区域
        content_div = soup.find('div', class_='Mid2L_con')
        if not content_div:
            return content
            
        # 提取段落和图片
        for element in content_div.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5']):
            # 处理文本段落
            if element.name == 'p' and not element.find('img'):
                text = element.text.strip()
                if text:
                    content.append({'type': 'text', 'value': text})
                    
            # 处理图片
            for img in element.find_all('img'):
                img_url = img.get('data-src') or img.get('src')
                if img_url:
                    # 处理相对URL
                    if not img_url.startswith('http'):
                        from urllib.parse import urljoin
                        img_url = urljoin('https://www.gamersky.com/', img_url)
                    
                    alt = img.get('alt', '')
                    content.append({'type': 'image', 'url': img_url, 'alt': alt})
                    
        return content
```### 
3. 图片下载实现

我们将实现一个图片下载器，用于下载和保存图片：

```python
import os
import requests
import time
import hashlib
from urllib.parse import urlparse

class ImageDownloader:
    def __init__(self, output_dir, delay=0.5):
        self.output_dir = output_dir
        self.delay = delay
        self.last_download_time = 0
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
    def download_image(self, url, filename=None):
        # 实现下载延迟
        current_time = time.time()
        sleep_time = max(0, self.delay - (current_time - self.last_download_time))
        if sleep_time > 0:
            time.sleep(sleep_time)
            
        try:
            # 如果没有提供文件名，从URL生成一个
            if not filename:
                # 使用URL的哈希值作为文件名
                url_hash = hashlib.md5(url.encode()).hexdigest()
                parsed_url = urlparse(url)
                path = parsed_url.path
                ext = os.path.splitext(path)[1] or '.jpg'  # 默认为.jpg
                filename = f"{url_hash}{ext}"
                
            local_path = os.path.join(self.output_dir, filename)
            
            # 下载图片
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            self.last_download_time = time.time()
            return local_path
            
        except Exception as e:
            print(f"Error downloading image {url}: {e}")
            return None
            
    def download_all_images(self, image_list):
        result = {}
        for image in image_list:
            if image['type'] == 'image' and 'url' in image:
                local_path = self.download_image(image['url'])
                if local_path:
                    image['local_path'] = local_path
                    result[image['url']] = local_path
        return result
```

### 4. Markdown生成实现

我们将实现一个Markdown生成器，用于将结构化内容转换为Markdown格式：

```python
import os

class MarkdownGenerator:
    def __init__(self, image_path_mapping=None):
        self.image_path_mapping = image_path_mapping or {}
        
    def generate_markdown(self, content):
        markdown = []
        
        # 添加标题
        markdown.append(f"# {content['title']}\n")
        
        # 添加来源信息
        if 'source_url' in content:
            markdown.append(f"*来源: [{content['source_url']}]({content['source_url']})*\n")
            
        # 添加目录
        if 'toc' in content and content['toc']:
            markdown.append("## 目录\n")
            markdown.append(self.generate_toc_markdown(content['toc']))
            markdown.append("\n---\n")
            
        # 添加章节内容
        for chapter in content.get('chapters', []):
            markdown.append(f"## {chapter['title']}\n")
            
            # 添加章节内容
            markdown.append(self.generate_content_markdown(chapter['content']))
            
            # 添加小节内容
            for section in chapter.get('sections', []):
                markdown.append(f"### {section['title']}\n")
                markdown.append(self.generate_content_markdown(section['content']))
                
        return '\n'.join(markdown)
        
    def generate_content_markdown(self, content_list):
        markdown = []
        
        for item in content_list:
            if item['type'] == 'text':
                markdown.append(f"{item['value']}\n")
            elif item['type'] == 'image':
                alt = item.get('alt', '')
                url = item.get('url', '')
                
                # 使用本地路径（如果有）
                if url in self.image_path_mapping:
                    local_path = self.image_path_mapping[url]
                    # 使用相对路径
                    rel_path = os.path.basename(local_path)
                    markdown.append(f"![{alt}](images/{rel_path})\n")
                else:
                    # 使用原始URL
                    markdown.append(f"![{alt}]({url})\n")
                    
        return '\n'.join(markdown)
        
    def generate_toc_markdown(self, toc):
        markdown = []
        
        for item in toc:
            indent = '  ' * (item['level'] - 1)
            markdown.append(f"{indent}- [{item['title']}](#{item['id']})")
            
        return '\n'.join(markdown)
        
    def save_markdown(self, markdown, output_file):
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        os.makedirs(output_dir, exist_ok=True)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
```### 5. 主
控制器实现

主控制器将协调各组件的工作，管理整个抓取和生成过程：

```python
class Controller:
    def __init__(self, config):
        self.config = config
        self.scraper = Scraper(config['user_agent'], config['delay'])
        self.parser = Parser()
        self.content_organizer = ContentOrganizer()
        
        if config['download_images']:
            self.image_downloader = ImageDownloader(config['image_dir'])
        else:
            self.image_downloader = None
            
    def run(self):
        url = self.config['start_url']
        page_number = 1
        
        while url:
            # 报告进度
            self.report_progress(f"正在抓取第 {page_number} 页: {url}")
            
            # 抓取页面
            html = self.scraper.fetch_page(url)
            if not html:
                self.report_progress(f"无法抓取页面: {url}")
                break
                
            # 解析内容
            content = self.parser.parse_content(html)
            if not content:
                self.report_progress(f"无法解析页面内容: {url}")
                break
                
            # 添加页面信息
            content['url'] = url
            content['page_number'] = page_number
            
            # 下载图片（如果需要）
            if self.image_downloader:
                image_items = [item for item in content['content'] if item['type'] == 'image']
                self.report_progress(f"正在下载第 {page_number} 页的图片 ({len(image_items)} 张)")
                self.image_downloader.download_all_images(image_items)
                
            # 添加到内容组织器
            self.content_organizer.add_page_content(content)
            
            # 获取下一页URL
            next_url = self.scraper.get_next_page_url(html, url)
            if next_url == url:
                # 避免无限循环
                break
                
            url = next_url
            page_number += 1
            
        # 组织内容
        self.report_progress("正在组织内容...")
        organized_content = self.content_organizer.organize_content()
        
        # 生成Markdown
        self.report_progress("正在生成Markdown...")
        image_mapping = {}
        if self.image_downloader:
            # 收集所有图片的映射
            for chapter in organized_content.get('chapters', []):
                for item in chapter.get('content', []):
                    if item['type'] == 'image' and 'url' in item and 'local_path' in item:
                        image_mapping[item['url']] = item['local_path']
                        
                for section in chapter.get('sections', []):
                    for item in section.get('content', []):
                        if item['type'] == 'image' and 'url' in item and 'local_path' in item:
                            image_mapping[item['url']] = item['local_path']
                            
        markdown_generator = MarkdownGenerator(image_mapping)
        markdown = markdown_generator.generate_markdown(organized_content)
        
        # 保存Markdown
        output_file = os.path.join(self.config['output_dir'], self.config['output_file'])
        self.report_progress(f"正在保存Markdown到 {output_file}...")
        markdown_generator.save_markdown(markdown, output_file)
        
        self.report_progress("完成！")
        
    def report_progress(self, message, percentage=None):
        print(message)
        # 这里可以添加更复杂的进度报告逻辑
```

## 总结

本设计文档详细描述了"黑神话悟空"游戏攻略爬虫的技术实现方案。系统采用模块化设计，包含网页抓取器、内容解析器、图片下载器、内容组织器、Markdown生成器和主控制器等核心组件。

系统将从指定的起始URL开始，抓取所有相关页面内容，包括"下一页"链接指向的所有页面，下载图片，并将内容整理成一本结构化的Markdown格式攻略书。

系统实现了错误处理机制，能够处理网络错误、解析错误、图片下载错误和文件操作错误等异常情况。同时，系统也提供了进度报告功能，让用户了解当前抓取状态。

通过本设计的实现，用户将能够方便地获取完整的"黑神话悟空"游戏攻略内容，并以Markdown格式进行阅读和查询。