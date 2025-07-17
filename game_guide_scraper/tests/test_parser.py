"""
测试解析器模块的功能。
"""
import os
import sys
import unittest
from bs4 import BeautifulSoup

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from game_guide_scraper.parser.parser import Parser


class TestParser(unittest.TestCase):
    """测试Parser类的功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.parser = Parser()
        
        # 创建一个简单的HTML用于测试
        self.test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>黑神话悟空攻略 - 第一章 - 游民星空</title>
            <meta charset="utf-8">
        </head>
        <body>
            <div class="header">
                <div class="nav">导航栏内容</div>
            </div>
            
            <div class="Mid2L_con">
                <h1>黑神话悟空攻略 - 第一章</h1>
                
                <p>这是第一段文本内容，介绍了游戏的基本操作。</p>
                
                <div class="adsbygoogle">这是一个广告，应该被过滤掉。</div>
                
                <p>这是第二段文本内容，介绍了游戏的主要任务。</p>
                
                <div>
                    <img src="https://example.com/image1.jpg" alt="游戏截图1" />
                </div>
                
                <p>这是第三段文本内容，介绍了游戏的技能系统。</p>
                
                <h2>支线任务</h2>
                
                <p>这是关于支线任务的介绍。</p>
                
                <div>
                    <img src="https://example.com/image2.jpg" alt="游戏截图2" />
                    <p>图片说明：这是一张游戏截图。</p>
                </div>
                
                <table>
                    <tr>
                        <th>技能名称</th>
                        <th>技能效果</th>
                    </tr>
                    <tr>
                        <td>火眼金睛</td>
                        <td>提高侦察能力</td>
                    </tr>
                    <tr>
                        <td>筋斗云</td>
                        <td>提高移动速度</td>
                    </tr>
                </table>
                
                <ul>
                    <li>装备1：如意金箍棒</li>
                    <li>装备2：凤翅紫金冠</li>
                    <li>装备3：锁子黄金甲</li>
                </ul>
            </div>
            
            <div class="footer">
                <div class="copyright">版权信息</div>
            </div>
        </body>
        </html>
        """
        
    def test_extract_title(self):
        """测试标题提取功能"""
        soup = BeautifulSoup(self.test_html, 'html.parser')
        title = self.parser.extract_title(soup)
        self.assertEqual(title, "黑神话悟空攻略 - 第一章")
        
    def test_extract_content(self):
        """测试内容提取功能"""
        soup = BeautifulSoup(self.test_html, 'html.parser')
        content = self.parser.extract_content(soup)
        
        # 检查内容列表长度
        self.assertGreater(len(content), 0)
        
        # 检查是否包含文本内容
        text_items = [item for item in content if item['type'] == 'text']
        self.assertGreater(len(text_items), 0)
        
        # 检查是否包含图片内容
        image_items = [item for item in content if item['type'] == 'image']
        self.assertGreater(len(image_items), 0)
        
        # 检查是否包含标题内容
        heading_items = [item for item in content if item['type'] == 'heading']
        self.assertGreater(len(heading_items), 0)
        
        # 检查是否包含列表内容
        list_items = [item for item in content if item['type'] in ['ordered_list', 'unordered_list']]
        self.assertGreater(len(list_items), 0)
        
    def test_extract_images(self):
        """测试图片提取功能"""
        soup = BeautifulSoup(self.test_html, 'html.parser')
        images = self.parser.extract_images(soup)
        
        # 检查图片列表长度
        self.assertEqual(len(images), 2)
        
        # 检查图片URL
        self.assertEqual(images[0]['url'], 'https://example.com/image1.jpg')
        self.assertEqual(images[1]['url'], 'https://example.com/image2.jpg')
        
        # 检查图片描述
        self.assertEqual(images[0]['alt'], '游戏截图1')
        self.assertEqual(images[1]['alt'], '游戏截图2')
        
    def test_parse_content(self):
        """测试整体解析功能"""
        result = self.parser.parse_content(self.test_html)
        
        # 检查解析结果是否为字典
        self.assertIsInstance(result, dict)
        
        # 检查解析结果是否包含标题和内容
        self.assertIn('title', result)
        self.assertIn('content', result)
        
        # 检查标题
        self.assertEqual(result['title'], '黑神话悟空攻略 - 第一章')
        
        # 检查内容列表长度
        self.assertGreater(len(result['content']), 0)


if __name__ == '__main__':
    unittest.main()