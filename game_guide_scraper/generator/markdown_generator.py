"""
Markdown生成器模块，负责将结构化内容转换为Markdown格式。
"""
import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class MarkdownGenerator:
    """
    Markdown生成器类，负责将结构化内容转换为Markdown格式。
    """
    
    def __init__(self, image_path_mapping: Optional[Dict[str, str]] = None):
        """
        初始化Markdown生成器
        
        参数:
            image_path_mapping: 图片URL到本地路径的映射字典
        """
        self.image_path_mapping = image_path_mapping or {}
        
    def generate_markdown(self, content: Dict[str, Any]) -> str:
        """
        生成Markdown文档
        
        参数:
            content: 结构化内容字典，包含title、source_url、toc和chapters等字段
            
        返回:
            Markdown格式的文档字符串
        """
        if not content:
            logger.warning("尝试生成空内容的Markdown")
            return "# 空文档\n\n*没有内容可显示*"
            
        markdown = []
        
        # 添加文档标题
        title = content.get('title', '未知标题')
        markdown.append(f"# {title}\n")
        
        # 添加来源信息
        source_url = content.get('source_url', '')
        if source_url:
            markdown.append(f"*来源: [{source_url}]({source_url})*\n")
            
        # 添加目录
        toc = content.get('toc', [])
        if toc:
            markdown.append("## 目录\n")
            markdown.append(self.generate_toc_markdown(toc))
            markdown.append("\n---\n")
            
        # 添加章节内容
        chapters = content.get('chapters', [])
        for i, chapter in enumerate(chapters):
            chapter_num = i + 1
            chapter_title = chapter.get('title', f"章节 {chapter_num}")
            chapter_id = chapter.get('id', f"chapter-{chapter_num}")
            
            # 添加章节标题
            markdown.append(f"## {chapter_num}. {chapter_title} <a id=\"{chapter_id}\"></a>\n")
            
            # 添加章节内容
            chapter_content = chapter.get('content', [])
            markdown.append(self.generate_content_markdown(chapter_content))
            
            # 添加小节内容
            sections = chapter.get('sections', [])
            for j, section in enumerate(sections):
                section_num = f"{chapter_num}.{j + 1}"
                section_title = section.get('title', f"小节 {section_num}")
                section_id = section.get('id', f"section-{chapter_num}-{j + 1}")
                
                # 添加小节标题
                markdown.append(f"### {section_num} {section_title} <a id=\"{section_id}\"></a>\n")
                
                # 添加小节内容
                section_content = section.get('content', [])
                markdown.append(self.generate_content_markdown(section_content))
                
        return '\n'.join(markdown)
        
    def generate_content_markdown(self, content_list: List[Dict[str, Any]]) -> str:
        """
        生成内容的Markdown
        
        参数:
            content_list: 内容元素列表
            
        返回:
            内容的Markdown字符串
        """
        markdown = []
        
        for item in content_list:
            item_type = item.get('type', '')
            
            if item_type == 'text':
                # 处理文本内容
                value = item.get('value', '')
                if value:
                    markdown.append(f"{value}\n")
                    
            elif item_type == 'image':
                # 处理图片内容
                url = item.get('url', '')
                alt = item.get('alt', '')
                
                if url:
                    # 优先使用本地路径
                    if url in self.image_path_mapping:
                        local_path = self.image_path_mapping[url]
                        # 使用相对路径
                        rel_path = os.path.basename(local_path)
                        markdown.append(f"![{alt}](images/{rel_path})\n")
                    else:
                        # 使用原始URL
                        markdown.append(f"![{alt}]({url})\n")
                        
            elif item_type == 'heading':
                # 处理标题内容
                level = item.get('level', 3)  # 默认为h3
                value = item.get('value', '')
                id_str = item.get('id', '')
                
                if value:
                    # 根据级别添加不同数量的#
                    heading_prefix = '#' * (level + 1)  # +1是因为在章节和小节下，标题级别需要增加
                    
                    if id_str:
                        markdown.append(f"{heading_prefix} {value} <a id=\"{id_str}\"></a>\n")
                    else:
                        markdown.append(f"{heading_prefix} {value}\n")
                        
            elif item_type == 'list':
                # 处理列表内容
                items = item.get('items', [])
                ordered = item.get('ordered', False)
                
                if items:
                    markdown.append("\n")
                    for i, list_item in enumerate(items):
                        if ordered:
                            markdown.append(f"{i + 1}. {list_item}\n")
                        else:
                            markdown.append(f"- {list_item}\n")
                    markdown.append("\n")
                    
            elif item_type == 'table':
                # 处理表格内容
                headers = item.get('headers', [])
                rows = item.get('rows', [])
                
                if headers and rows:
                    # 添加表头
                    markdown.append("| " + " | ".join(headers) + " |\n")
                    # 添加分隔线
                    markdown.append("| " + " | ".join(["---"] * len(headers)) + " |\n")
                    # 添加表格内容
                    for row in rows:
                        markdown.append("| " + " | ".join(row) + " |\n")
                    markdown.append("\n")
                    
            elif item_type == 'code':
                # 处理代码内容
                value = item.get('value', '')
                language = item.get('language', '')
                
                if value:
                    if language:
                        markdown.append(f"```{language}\n{value}\n```\n")
                    else:
                        markdown.append(f"```\n{value}\n```\n")
                        
            elif item_type == 'quote':
                # 处理引用内容
                value = item.get('value', '')
                
                if value:
                    # 为每一行添加>前缀
                    lines = value.split('\n')
                    for line in lines:
                        markdown.append(f"> {line}\n")
                    markdown.append("\n")
                    
        return '\n'.join(markdown)
        
    def generate_toc_markdown(self, toc: List[Dict[str, Any]]) -> str:
        """
        生成目录的Markdown
        
        参数:
            toc: 目录项列表
            
        返回:
            目录的Markdown字符串
        """
        markdown = []
        
        for item in toc:
            level = item.get('level', 0)
            title = item.get('title', '')
            id_str = item.get('id', '')
            
            if title and id_str:
                # 根据级别添加缩进
                indent = '  ' * level
                markdown.append(f"{indent}- [{title}](#{id_str})")
                
        return '\n'.join(markdown)
        
    def save_markdown(self, markdown: str, output_file: str) -> bool:
        """
        保存Markdown到文件
        
        参数:
            markdown: Markdown字符串
            output_file: 输出文件路径
            
        返回:
            保存成功返回True，否则返回False
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                
            # 写入文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
                
            logger.info(f"Markdown已保存到: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存Markdown时出错: {e}")
            return False