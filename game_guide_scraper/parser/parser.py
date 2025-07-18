"""
解析器模块，用于从HTML中提取有用信息，如文本、图片等。
"""
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from typing import Dict, List, Optional, Any


class Parser:
    """
    HTML内容解析器，负责从HTML中提取标题、正文、图片URL等信息。
    """
    
    def __init__(self):
        """
        初始化解析器
        """
        # 定义可能包含主要内容的CSS选择器
        self.content_selectors = [
            'div.Mid2L_con',  # 游民星空攻略内容区域
            'div.article-content',
            'div.content',
            'article',
            'div.main-content'
        ]
        
        # 定义需要过滤的元素选择器
        self.filter_selectors = [
            'div.adsbygoogle',
            'div.advertisement',
            'div.share',
            'div.comment',
            'div.related',
            'div.sidebar',
            'div.nav',
            'div.footer',
            'div.header',
            'script',
            'style',
            'iframe'
        ]
        
        # 定义需要过滤的文本内容关键词
        self.filter_keywords = [
            '更多相关内容请关注',
            '责任编辑',
            '友情提示：支持键盘',
            '翻页',
            '本文是否解决了您的问题',
            '已解决',
            '未解决',
            '文章内容导航',
            '上一页',
            '下一页',
        ]
        
    def parse_content(self, html: str) -> Optional[Dict[str, Any]]:
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
            如果解析失败，返回None
        """
        if not html:
            return None
            
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 移除不需要的元素
            self._remove_unwanted_elements(soup)
            
            # 提取标题
            title = self.extract_title(soup)
            
            # 提取内容（文本和图片）
            content = self.extract_content(soup)
            
            # 返回解析结果
            return {
                'title': title,
                'content': content
            }
        except Exception as e:
            print(f"解析HTML内容时出错: {e}")
            return None
            
    def _remove_unwanted_elements(self, soup: BeautifulSoup) -> None:
        """
        移除不需要的HTML元素，如广告、导航栏等
        
        参数:
            soup: BeautifulSoup对象
        """
        for selector in self.filter_selectors:
            for element in soup.select(selector):
                element.decompose()
                
    def extract_title(self, soup: BeautifulSoup) -> str:
        """
        从HTML中提取页面标题
        
        参数:
            soup: BeautifulSoup对象
            
        返回:
            页面标题
        """
        # 首先尝试从h1标签中提取标题
        h1 = soup.find('h1')
        if h1 and h1.text.strip():
            return h1.text.strip()
            
        # 尝试从title标签中提取标题
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.text.strip()
            # 处理标题，去除网站名称等
            if '-' in title:
                title = title.split('-')[0].strip()
            elif '_' in title:
                title = title.split('_')[0].strip()
            elif '|' in title:
                title = title.split('|')[0].strip()
            return title
            
        # 尝试从meta标签中提取标题
        meta_title = soup.find('meta', {'property': 'og:title'}) or soup.find('meta', {'name': 'title'})
        if meta_title and meta_title.get('content'):
            return meta_title['content'].strip()
            
        return "未知标题"
        
    def extract_content(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        从HTML中提取正文内容，包括文本和图片
        
        参数:
            soup: BeautifulSoup对象
            
        返回:
            内容元素列表，每个元素是一个字典，包含类型和值
        """
        content = []
        
        # 找到主要内容区域
        main_content = None
        for selector in self.content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
                
        # 如果没有找到主要内容区域，使用body作为备用
        if not main_content:
            main_content = soup.body
            
        if not main_content:
            return content
            
        # 提取内容元素
        for element in main_content.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'table', 'ul', 'ol']):
            # 跳过空元素
            if not element.text.strip() and not element.find('img'):
                continue
                
            # 处理图片
            if element.name == 'img' or element.find('img'):
                img_elements = [element] if element.name == 'img' else element.find_all('img')
                for img in img_elements:
                    img_info = self._extract_image_info(img)
                    if img_info:
                        content.append(img_info)
                        
            # 处理表格
            elif element.name == 'table':
                table_html = str(element)
                content.append({'type': 'table', 'value': table_html})
                
            # 处理列表
            elif element.name in ['ul', 'ol']:
                list_items = []
                for li in element.find_all('li'):
                    list_items.append(li.text.strip())
                if list_items:
                    list_type = 'ordered_list' if element.name == 'ol' else 'unordered_list'
                    content.append({'type': list_type, 'value': list_items})
                    
            # 处理标题
            elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                heading_text = element.text.strip()
                if heading_text:
                    heading_level = int(element.name[1])
                    content.append({'type': 'heading', 'value': heading_text, 'level': heading_level})
                    
            # 处理文本段落
            elif element.name == 'p' or (element.name == 'div' and not element.find(['div', 'p'])):
                text = element.text.strip()
                if text and not self._should_filter_text(text):
                    content.append({'type': 'text', 'value': text})
                    
        return content
        
    def extract_images(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        从HTML中提取图片URL和描述
        
        参数:
            soup: BeautifulSoup对象
            
        返回:
            图片信息列表，每个元素是一个字典，包含URL和描述
        """
        images = []
        
        # 找到主要内容区域
        main_content = None
        for selector in self.content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
                
        # 如果没有找到主要内容区域，使用body作为备用
        if not main_content:
            main_content = soup.body
            
        if not main_content:
            return images
            
        # 提取所有图片
        for img in main_content.find_all('img'):
            img_info = self._extract_image_info(img)
            if img_info:
                images.append(img_info)
                
        return images
        
    def _extract_image_info(self, img_tag) -> Optional[Dict[str, Any]]:
        """
        从img标签中提取图片信息
        
        参数:
            img_tag: img标签的BeautifulSoup对象
            
        返回:
            图片信息字典，包含URL和描述，如果提取失败则返回None
        """
        # 尝试获取图片URL
        img_url = None
        for attr in ['data-src', 'src', 'data-original']:
            if img_tag.get(attr):
                img_url = img_tag[attr]
                break
                
        if not img_url:
            return None
            
        # 处理游民星空的高清原图URL
        # 游民星空的缩略图URL格式：image001_S.jpg
        # 高清原图URL格式：image001.jpg
        if 'gamersky.com' in img_url and '_S.jpg' in img_url:
            img_url = img_url.replace('_S.jpg', '.jpg')
        elif 'gamersky.com' in img_url and '_S.png' in img_url:
            img_url = img_url.replace('_S.png', '.png')
            
        # 处理相对URL
        if not img_url.startswith(('http://', 'https://')):
            # 由于这里没有base_url参数，我们只能保留相对路径
            # 在实际使用时，需要在其他地方处理这个问题
            pass
            
        # 获取图片描述
        alt = img_tag.get('alt', '')
        title = img_tag.get('title', '')
        description = alt or title or ''
        
        # 过滤掉小图标、广告图片等
        # 通常这些图片的URL中会包含特定的关键词或文件名
        filter_keywords = ['icon', 'logo', 'banner', 'ad', 'advertisement']
        filter_filenames = ['banner923.jpg']
        
        # 检查URL中是否包含过滤关键词
        if any(keyword in img_url.lower() for keyword in filter_keywords):
            return None
            
        # 检查是否是特定的需要过滤的文件名
        if any(filename in img_url.lower() for filename in filter_filenames):
            return None
                
        return {'type': 'image', 'url': img_url, 'alt': description}
    
    def _should_filter_text(self, text: str) -> bool:
        """
        判断文本是否应该被过滤掉
        
        参数:
            text: 要检查的文本
            
        返回:
            True表示应该过滤，False表示保留
        """
        import re
        
        # 检查是否包含过滤关键词
        for keyword in self.filter_keywords:
            if keyword in text:
                return True
        
        # 检查是否是单独的页面标题（如"第1页：小妖-第一回-狼斥候"）
        # 这种格式应该保留，不过滤
        single_page_pattern = r'^第\d+页：[^第]*$'
        if re.match(single_page_pattern, text.strip()):
            return False  # 保留单独的页面标题
        
        # 检查是否是包含多个页码的长列表
        # 如果文本中包含多个"第X页："模式，则过滤掉
        page_matches = re.findall(r'第\d+页：', text)
        if len(page_matches) > 1:
            return True  # 过滤包含多个页码的文本
            
        # 检查是否是长页码列表（包含很多页码信息的文本）
        if len(text) > 200 and '第' in text and '页：' in text:
            return True
            
        # 检查是否只包含数字和空格（可能是页码）
        if re.match(r'^[\d\s]+$', text) and len(text.split()) > 3:
            return True
            
        return False