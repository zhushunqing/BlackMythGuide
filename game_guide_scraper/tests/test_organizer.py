"""
测试内容组织器模块
"""
import unittest
from game_guide_scraper.organizer.organizer import ContentOrganizer

class TestContentOrganizer(unittest.TestCase):
    """测试ContentOrganizer类"""
    
    def setUp(self):
        """设置测试环境"""
        self.organizer = ContentOrganizer()
        
    def test_add_page_content(self):
        """测试添加页面内容功能"""
        # 创建测试页面内容
        page1 = {
            'url': 'https://example.com/page1',
            'title': '黑神话悟空攻略 - 第一章',
            'page_number': 1,
            'content': [
                {'type': 'text', 'value': '这是第一章的内容'},
                {'type': 'image', 'url': 'https://example.com/image1.jpg', 'alt': '图片1'}
            ]
        }
        
        # 添加页面内容
        self.organizer.add_page_content(page1)
        
        # 验证页面内容已添加
        self.assertEqual(len(self.organizer.pages), 1)
        self.assertEqual(self.organizer.title, '黑神话悟空攻略 - 第一章')
        self.assertEqual(self.organizer.source_url, 'https://example.com/page1')
        
        # 添加第二个页面
        page2 = {
            'url': 'https://example.com/page2',
            'title': '黑神话悟空攻略 - 第二章',
            'page_number': 2,
            'content': [
                {'type': 'text', 'value': '这是第二章的内容'},
                {'type': 'image', 'url': 'https://example.com/image2.jpg', 'alt': '图片2'}
            ]
        }
        
        self.organizer.add_page_content(page2)
        
        # 验证第二个页面已添加，并且页面按页码排序
        self.assertEqual(len(self.organizer.pages), 2)
        self.assertEqual(self.organizer.pages[0]['page_number'], 1)
        self.assertEqual(self.organizer.pages[1]['page_number'], 2)
        
        # 测试添加无效页面内容
        self.organizer.add_page_content(None)
        self.assertEqual(len(self.organizer.pages), 2)  # 页面数量不变
        
        # 测试添加缺少必要字段的页面内容
        invalid_page = {'title': '无效页面'}
        self.organizer.add_page_content(invalid_page)
        self.assertEqual(len(self.organizer.pages), 2)  # 页面数量不变
        
    def test_organize_content_single_chapter(self):
        """测试组织单章节内容"""
        # 创建测试页面内容
        page1 = {
            'url': 'https://example.com/page1',
            'title': '黑神话悟空攻略',
            'page_number': 1,
            'content': [
                {'type': 'text', 'value': '这是第一页的内容'},
                {'type': 'image', 'url': 'https://example.com/image1.jpg', 'alt': '图片1'}
            ]
        }
        
        page2 = {
            'url': 'https://example.com/page2',
            'title': '黑神话悟空攻略',
            'page_number': 2,
            'content': [
                {'type': 'text', 'value': '这是第二页的内容'},
                {'type': 'image', 'url': 'https://example.com/image2.jpg', 'alt': '图片2'}
            ]
        }
        
        # 添加页面内容
        self.organizer.add_page_content(page1)
        self.organizer.add_page_content(page2)
        
        # 组织内容
        document = self.organizer.organize_content()
        
        # 验证结果
        self.assertEqual(document['title'], '黑神话悟空攻略')
        self.assertEqual(document['source_url'], 'https://example.com/page1')
        self.assertEqual(len(document['chapters']), 1)
        self.assertEqual(len(document['chapters'][0]['content']), 4)  # 两页内容合并
        self.assertEqual(len(document['toc']), 1)  # 只有一个章节
        
    def test_organize_content_multiple_chapters(self):
        """测试组织多章节内容"""
        # 创建测试页面内容
        page1 = {
            'url': 'https://example.com/page1',
            'title': '黑神话悟空攻略 - 第一章',
            'page_number': 1,
            'content': [
                {'type': 'text', 'value': '这是第一章的内容'},
                {'type': 'image', 'url': 'https://example.com/image1.jpg', 'alt': '图片1'}
            ]
        }
        
        page2 = {
            'url': 'https://example.com/page2',
            'title': '黑神话悟空攻略 - 第二章',
            'page_number': 2,
            'content': [
                {'type': 'text', 'value': '这是第二章的内容'},
                {'type': 'image', 'url': 'https://example.com/image2.jpg', 'alt': '图片2'}
            ]
        }
        
        page3 = {
            'url': 'https://example.com/page3',
            'title': '黑神话悟空攻略 - 第二章 - 技巧',
            'page_number': 3,
            'content': [
                {'type': 'text', 'value': '这是第二章技巧部分的内容'},
                {'type': 'image', 'url': 'https://example.com/image3.jpg', 'alt': '图片3'}
            ]
        }
        
        # 添加页面内容
        self.organizer.add_page_content(page1)
        self.organizer.add_page_content(page2)
        self.organizer.add_page_content(page3)
        
        # 组织内容
        document = self.organizer.organize_content()
        
        # 验证结果
        self.assertEqual(document['title'], '黑神话悟空攻略 - 第一章')
        self.assertEqual(document['source_url'], 'https://example.com/page1')
        self.assertEqual(len(document['chapters']), 2)  # 两个章节
        self.assertEqual(document['chapters'][0]['title'], '黑神话悟空攻略 - 第一章')
        self.assertEqual(document['chapters'][1]['title'], '黑神话悟空攻略 - 第二章')
        self.assertEqual(len(document['chapters'][1]['sections']), 1)  # 第二章有一个小节
        self.assertEqual(document['chapters'][1]['sections'][0]['title'], '黑神话悟空攻略 - 第二章 - 技巧')
        self.assertEqual(len(document['toc']), 3)  # 两个章节加一个小节
        
    def test_generate_toc(self):
        """测试生成目录功能"""
        # 创建测试章节
        chapters = [
            {
                'title': '第一章',
                'id': 'chapter-1',
                'content': [],
                'sections': [
                    {'title': '第一节', 'id': 'section-1', 'content': []},
                    {'title': '第二节', 'id': 'section-2', 'content': []}
                ]
            },
            {
                'title': '第二章',
                'id': 'chapter-2',
                'content': [],
                'sections': []
            }
        ]
        
        # 生成目录
        toc = self.organizer.generate_toc(chapters)
        
        # 验证结果
        self.assertEqual(len(toc), 4)  # 两个章节加两个小节
        self.assertEqual(toc[0]['level'], 1)
        self.assertEqual(toc[0]['title'], '第一章')
        self.assertEqual(toc[1]['level'], 2)
        self.assertEqual(toc[1]['title'], '第一节')
        self.assertEqual(toc[2]['level'], 2)
        self.assertEqual(toc[2]['title'], '第二节')
        self.assertEqual(toc[3]['level'], 1)
        self.assertEqual(toc[3]['title'], '第二章')
        
    def test_generate_id(self):
        """测试生成ID功能"""
        # 测试中文标题
        title1 = '黑神话悟空攻略 - 第一章'
        id1 = self.organizer._generate_id(title1)
        self.assertEqual(id1, '黑神话悟空攻略-第一章')
        
        # 测试英文标题
        title2 = 'Black Myth: Wukong Guide - Chapter 1'
        id2 = self.organizer._generate_id(title2)
        self.assertEqual(id2, 'black-myth-wukong-guide-chapter-1')
        
        # 测试包含特殊字符的标题
        title3 = '黑神话悟空攻略：第一章（入门篇）'
        id3 = self.organizer._generate_id(title3)
        self.assertEqual(id3, '黑神话悟空攻略第一章入门篇')
        
    def test_empty_content(self):
        """测试没有内容时的行为"""
        # 不添加任何页面内容
        document = self.organizer.organize_content()
        
        # 验证结果
        self.assertEqual(document['title'], '空文档')
        self.assertEqual(document['source_url'], '')
        self.assertEqual(len(document['chapters']), 0)
        self.assertEqual(len(document['toc']), 0)

if __name__ == '__main__':
    unittest.main()