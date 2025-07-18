"""
内容组织器模块，负责将解析后的内容组织成结构化的文档。
"""
import re
import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ContentOrganizer:
    """
    内容组织器类，负责将多个页面的内容组织成结构化的文档。
    """
    
    def __init__(self):
        """
        初始化内容组织器
        """
        self.pages = []  # 存储所有页面内容
        self.title = ""  # 文档标题
        self.source_url = ""  # 原始URL
        
    def add_page_content(self, page_content: Dict[str, Any]) -> None:
        """
        添加一个页面的内容
        
        参数:
            page_content: 页面内容字典，包含url、title、page_number和content等字段
        """
        if not page_content:
            logger.warning("尝试添加空的页面内容")
            return
            
        # 确保页面内容包含必要的字段
        required_fields = ['url', 'title', 'content']
        for field in required_fields:
            if field not in page_content:
                logger.warning(f"页面内容缺少必要的字段: {field}")
                return
                
        # 如果是第一个页面，设置文档标题和源URL
        if not self.pages:
            self.title = page_content['title']
            self.source_url = page_content['url']
            
        # 检查是否已存在相同URL的页面，避免重复添加
        for existing_page in self.pages:
            if existing_page.get('url') == page_content['url']:
                logger.warning(f"页面已存在，跳过添加: {page_content['url']}")
                return
                
        # 处理内容中的图片路径
        for item in page_content.get('content', []):
            if item.get('type') == 'image' and 'local_path' in item:
                # 确保本地路径是相对路径，便于后续生成Markdown
                item['relative_path'] = os.path.basename(item['local_path'])
                
        # 添加页面内容到列表中
        self.pages.append(page_content)
        
        # 按页码排序
        if 'page_number' in page_content:
            self.pages.sort(key=lambda p: p.get('page_number', 0))
        else:
            # 如果没有页码，则按添加顺序排序
            page_content['page_number'] = len(self.pages)
            
        logger.info(f"添加了页面内容: {page_content['title']} (页码: {page_content.get('page_number', '未知')})")
        
    def organize_content(self) -> Dict[str, Any]:
        """
        组织所有内容，生成结构化文档
        
        返回:
            结构化文档字典，包含title、source_url、toc和chapters等字段
        """
        if not self.pages:
            logger.warning("没有页面内容可组织")
            return {
                'title': "空文档",
                'source_url': "",
                'toc': [],
                'chapters': []
            }
            
        # 创建结构化文档
        document = {
            'title': self.title,
            'source_url': self.source_url,
            'chapters': [],
            'toc': [],
            'page_titles': []  # 添加页面标题列表
        }
        
        # 确保页面按页码排序
        self.pages.sort(key=lambda p: p.get('page_number', 0))
        
        # 收集页面标题信息
        page_titles = self._extract_page_titles()
        document['page_titles'] = page_titles
        
        # 创建单个章节包含所有内容
        chapter = {
            'title': self.title,
            'id': self._generate_id(self.title),
            'content': [],
            'sections': []
        }
        
        # 合并所有页面的内容
        for page in self.pages:
            chapter['content'].extend(page.get('content', []))
            
        document['chapters'].append(chapter)
        
        # 生成目录（基于页面标题）
        document['toc'] = self.generate_page_based_toc(page_titles)
        
        return document
        
    def _identify_chapter_structure(self) -> List[Dict[str, Any]]:
        """
        分析页面标题，识别章节和小节结构
        
        返回:
            章节结构列表，每个章节包含标题、页面列表和小节列表
        """
        if not self.pages:
            return []
            
        # 初始化章节列表
        chapters = []
        current_chapter = None
        
        # 第一遍：识别章节
        for page in self.pages:
            page_title = page.get('title', '')
            
            # 检查是否是新章节
            is_new_chapter = False
            if not current_chapter:
                is_new_chapter = True
            elif self._is_new_chapter(page_title, current_chapter['title']):
                is_new_chapter = True
                
            if is_new_chapter:
                # 创建新章节
                current_chapter = {
                    'title': page_title,
                    'pages': [page],
                    'sections': []
                }
                chapters.append(current_chapter)
            else:
                # 将页面添加到当前章节
                current_chapter['pages'].append(page)
        
        # 第二遍：识别小节
        for chapter in chapters:
            chapter_title = chapter['title']
            chapter_pages = chapter['pages']
            
            # 如果章节只有一个页面，不需要进一步处理
            if len(chapter_pages) <= 1:
                continue
                
            # 查找可能的小节
            current_section = None
            for page in chapter_pages[1:]:  # 跳过第一个页面，因为它是章节标题页
                page_title = page.get('title', '')
                
                # 检查是否是小节
                if self._is_section(page_title, chapter_title):
                    # 创建新小节
                    current_section = {
                        'title': page_title,
                        'pages': [page]
                    }
                    chapter['sections'].append(current_section)
                elif current_section:
                    # 将页面添加到当前小节
                    current_section['pages'].append(page)
        
        return chapters
        
    def generate_toc(self, chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        生成目录
        
        参数:
            chapters: 章节列表
            
        返回:
            目录项列表
        """
        toc = []
        
        # 添加文档标题作为顶级目录项
        if self.title:
            toc.append({
                'level': 0,
                'title': self.title,
                'id': 'document-title'
            })
        
        for i, chapter in enumerate(chapters):
            # 添加章节到目录，包含章节序号
            chapter_num = i + 1
            chapter_title = f"{chapter_num}. {chapter['title']}"
            
            toc.append({
                'level': 1,
                'title': chapter_title,
                'id': chapter['id'],
                'number': chapter_num
            })
            
            # 添加小节到目录，包含小节序号
            for j, section in enumerate(chapter.get('sections', [])):
                section_num = f"{chapter_num}.{j + 1}"
                section_title = f"{section_num} {section['title']}"
                
                toc.append({
                    'level': 2,
                    'title': section_title,
                    'id': section['id'],
                    'number': section_num
                })
                
                # 检查是否有子小节（通过分析内容中的标题元素）
                subsections = self._extract_subsections_from_content(section.get('content', []))
                for k, subsection in enumerate(subsections):
                    subsection_num = f"{section_num}.{k + 1}"
                    subsection_title = f"{subsection_num} {subsection['title']}"
                    
                    toc.append({
                        'level': 3,
                        'title': subsection_title,
                        'id': subsection['id'],
                        'number': subsection_num
                    })
                
        return toc
        
    def _extract_subsections_from_content(self, content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        从内容中提取子小节（通过分析标题元素）
        
        参数:
            content: 内容元素列表
            
        返回:
            子小节列表
        """
        subsections = []
        
        for item in content:
            # 查找标题元素，level为3或4的标题可能是子小节
            if item.get('type') == 'heading' and item.get('level', 0) in [3, 4]:
                title = item.get('value', '')
                if title:
                    subsections.append({
                        'title': title,
                        'id': self._generate_id(title)
                    })
                    
        return subsections
    
    def _extract_page_titles(self) -> List[Dict[str, Any]]:
        """
        从页面内容中提取页面标题
        
        返回:
            页面标题列表，每个元素包含页码、标题和ID
        """
        page_titles = []
        
        for page in self.pages:
            page_number = page.get('page_number', 0)
            
            # 在页面内容中查找页面标题（格式如"第X页：标题"）
            content = page.get('content', [])
            for item in content:
                if item.get('type') == 'text':
                    text = item.get('value', '')
                    # 匹配"第X页：标题"格式
                    import re
                    match = re.match(r'^第(\d+)页：(.+)$', text.strip())
                    if match:
                        page_num = int(match.group(1))
                        title = match.group(2).strip()
                        
                        page_titles.append({
                            'page_number': page_num,
                            'title': title,
                            'full_title': text.strip(),
                            'id': self._generate_id(f"page-{page_num}-{title}"),
                            'url': page.get('url', '')
                        })
                        break  # 找到页面标题后跳出循环
        
        # 按页码排序
        page_titles.sort(key=lambda x: x['page_number'])
        return page_titles
    
    def generate_page_based_toc(self, page_titles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        基于页面标题生成目录
        
        参数:
            page_titles: 页面标题列表
            
        返回:
            目录项列表
        """
        toc = []
        
        # 添加文档标题作为顶级目录项
        if self.title:
            toc.append({
                'level': 0,
                'title': self.title,
                'id': 'document-title'
            })
        
        # 添加每个页面标题到目录
        for page_info in page_titles:
            toc.append({
                'level': 1,
                'title': page_info['full_title'],
                'id': page_info['id'],
                'page_number': page_info['page_number']
            })
        
        return toc
        
    def _generate_id(self, title: str) -> str:
        """
        根据标题生成ID
        
        参数:
            title: 标题
            
        返回:
            生成的ID
        """
        # 移除特殊字符，将空格替换为连字符
        id_str = re.sub(r'[^\w\s-]', '', title.lower())
        id_str = re.sub(r'[\s-]+', '-', id_str).strip('-')
        return id_str
        
    def _is_new_chapter(self, title: str, current_chapter_title: str) -> bool:
        """
        判断标题是否代表新章节
        
        参数:
            title: 当前标题
            current_chapter_title: 当前章节标题
            
        返回:
            如果是新章节则返回True，否则返回False
        """
        # 如果标题包含章节关键词，则认为是新章节
        chapter_keywords = ['章', '篇', 'Chapter', '攻略']
        
        # 检查标题是否包含章节关键词
        for keyword in chapter_keywords:
            if keyword in title and keyword not in current_chapter_title:
                return True
                
        # 检查标题是否与当前章节标题有显著差异
        # 如果标题差异超过50%，则认为是新章节
        common_chars = set(title) & set(current_chapter_title)
        similarity = len(common_chars) / max(len(set(title)), len(set(current_chapter_title)))
        
        return similarity < 0.5
        
    def _is_section(self, title: str, chapter_title: str) -> bool:
        """
        判断标题是否代表小节
        
        参数:
            title: 当前标题
            chapter_title: 当前章节标题
            
        返回:
            如果是小节则返回True，否则返回False
        """
        # 如果标题是章节标题的子集，则认为是小节
        if title in chapter_title:
            return False
            
        # 如果标题包含小节关键词，则认为是小节
        section_keywords = ['节', '部分', 'Section', '技巧', '心得']
        
        for keyword in section_keywords:
            if keyword in title:
                return True
                
        # 检查标题是否与章节标题有一定相似性
        # 如果标题与章节标题有30%-70%的相似性，则认为是小节
        common_chars = set(title) & set(chapter_title)
        similarity = len(common_chars) / max(len(set(title)), len(set(chapter_title)))
        
        return 0.3 <= similarity < 0.7