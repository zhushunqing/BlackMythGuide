"""
测试网页抓取器模块的功能。
"""
import os
import sys
import unittest
import time
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from game_guide_scraper.scraper.scraper import Scraper


class TestScraper(unittest.TestCase):
    """测试Scraper类的功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        self.scraper = Scraper(self.user_agent, delay=0.01)  # 使用较短的延迟以加快测试
        
        # 测试用的HTML内容
        self.test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>测试页面</title>
        </head>
        <body>
            <div class="content">
                <p>这是测试内容</p>
                <a href="page2.html">下一页</a>
            </div>
        </body>
        </html>
        """
        
        self.test_html_with_absolute_link = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>测试页面</title>
        </head>
        <body>
            <div class="content">
                <p>这是测试内容</p>
                <a href="https://example.com/page2.html">下一页</a>
            </div>
        </body>
        </html>
        """
        
        self.test_html_no_next = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>测试页面</title>
        </head>
        <body>
            <div class="content">
                <p>这是最后一页的内容</p>
            </div>
        </body>
        </html>
        """
    
    @patch('requests.Session.get')
    def test_fetch_page_success(self, mock_get):
        """测试成功抓取页面的情况"""
        # 模拟成功的HTTP响应
        mock_response = MagicMock()
        mock_response.text = self.test_html
        mock_response.raise_for_status.return_value = None
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response
        
        # 测试抓取页面
        url = 'https://example.com/test.html'
        result = self.scraper.fetch_page(url)
        
        # 验证结果
        self.assertEqual(result, self.test_html)
        mock_get.assert_called_once_with(url, timeout=10)
        mock_response.raise_for_status.assert_called_once()
    
    @patch('requests.Session.get')
    def test_fetch_page_http_error(self, mock_get):
        """测试HTTP错误的情况"""
        # 模拟HTTP错误
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        
        # 测试抓取页面
        url = 'https://example.com/notfound.html'
        result = self.scraper.fetch_page(url)
        
        # 验证结果
        self.assertIsNone(result)
    
    @patch('requests.Session.get')
    @patch('time.sleep')  # 模拟sleep以加快测试
    def test_fetch_page_server_error_with_retry(self, mock_sleep, mock_get):
        """测试服务器错误时的重试机制"""
        # 模拟服务器错误
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        
        # 测试抓取页面
        url = 'https://example.com/server_error.html'
        result = self.scraper.fetch_page(url)
        
        # 验证结果
        self.assertIsNone(result)
        # 验证重试次数（初始请求 + 3次重试 = 4次）
        self.assertEqual(mock_get.call_count, 4)
        # 验证sleep被调用了3次（每次重试前）
        self.assertEqual(mock_sleep.call_count, 3)
    
    @patch('requests.Session.get')
    def test_fetch_page_connection_error(self, mock_get):
        """测试连接错误的情况"""
        # 模拟连接错误
        mock_get.side_effect = requests.exceptions.ConnectionError("连接失败")
        
        # 测试抓取页面
        url = 'https://example.com/test.html'
        result = self.scraper.fetch_page(url)
        
        # 验证结果
        self.assertIsNone(result)
        # 验证重试次数（初始请求 + 3次重试 = 4次）
        self.assertEqual(mock_get.call_count, 4)
    
    @patch('requests.Session.get')
    def test_fetch_page_timeout_error(self, mock_get):
        """测试超时错误的情况"""
        # 模拟超时错误
        mock_get.side_effect = requests.exceptions.Timeout("请求超时")
        
        # 测试抓取页面
        url = 'https://example.com/test.html'
        result = self.scraper.fetch_page(url)
        
        # 验证结果
        self.assertIsNone(result)
        # 验证重试次数（初始请求 + 3次重试 = 4次）
        self.assertEqual(mock_get.call_count, 4)
    
    @patch('requests.Session.get')
    def test_fetch_page_other_request_error(self, mock_get):
        """测试其他请求错误的情况"""
        # 模拟其他请求异常
        mock_get.side_effect = requests.exceptions.RequestException("其他请求错误")
        
        # 测试抓取页面
        url = 'https://example.com/test.html'
        result = self.scraper.fetch_page(url)
        
        # 验证结果
        self.assertIsNone(result)
        # 验证只调用了一次（不重试）
        self.assertEqual(mock_get.call_count, 1)
    
    @patch('time.sleep')
    def test_request_delay(self, mock_sleep):
        """测试请求延迟机制"""
        # 设置较长的延迟时间
        scraper = Scraper(self.user_agent, delay=1.0)
        
        with patch('requests.Session.get') as mock_get:
            # 模拟成功的HTTP响应
            mock_response = MagicMock()
            mock_response.text = self.test_html
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # 连续发送两个请求
            scraper.fetch_page('https://example.com/page1.html')
            scraper.fetch_page('https://example.com/page2.html')
            
            # 验证sleep被调用（第二个请求应该有延迟）
            mock_sleep.assert_called()
    
    def test_get_next_page_url_relative_link(self):
        """测试提取相对链接的下一页URL"""
        base_url = 'https://example.com/page1.html'
        next_url = self.scraper.get_next_page_url(self.test_html, base_url)
        
        # 验证结果
        self.assertEqual(next_url, 'https://example.com/page2.html')
    
    def test_get_next_page_url_absolute_link(self):
        """测试提取绝对链接的下一页URL"""
        base_url = 'https://example.com/page1.html'
        next_url = self.scraper.get_next_page_url(self.test_html_with_absolute_link, base_url)
        
        # 验证结果
        self.assertEqual(next_url, 'https://example.com/page2.html')
    
    def test_get_next_page_url_no_next_page(self):
        """测试没有下一页链接的情况"""
        base_url = 'https://example.com/page1.html'
        next_url = self.scraper.get_next_page_url(self.test_html_no_next, base_url)
        
        # 验证结果
        self.assertIsNone(next_url)
    
    def test_get_next_page_url_empty_html(self):
        """测试空HTML的情况"""
        base_url = 'https://example.com/page1.html'
        next_url = self.scraper.get_next_page_url('', base_url)
        
        # 验证结果
        self.assertIsNone(next_url)
    
    def test_get_next_page_url_none_html(self):
        """测试None HTML的情况"""
        base_url = 'https://example.com/page1.html'
        next_url = self.scraper.get_next_page_url(None, base_url)
        
        # 验证结果
        self.assertIsNone(next_url)
    
    def test_get_next_page_url_circular_link(self):
        """测试循环链接检测"""
        # 创建一个指向自己的HTML
        circular_html = """
        <!DOCTYPE html>
        <html>
        <body>
            <a href="https://example.com/page1.html">下一页</a>
        </body>
        </html>
        """
        
        base_url = 'https://example.com/page1.html'
        next_url = self.scraper.get_next_page_url(circular_html, base_url)
        
        # 验证结果（应该检测到循环并返回None）
        self.assertIsNone(next_url)
    
    def test_get_next_page_url_alternative_patterns(self):
        """测试其他"下一页"链接模式"""
        # 测试包含"下一页"的文本
        html_with_text = """
        <!DOCTYPE html>
        <html>
        <body>
            <a href="page2.html">查看下一页内容</a>
        </body>
        </html>
        """
        
        base_url = 'https://example.com/page1.html'
        next_url = self.scraper.get_next_page_url(html_with_text, base_url)
        
        # 验证结果
        self.assertEqual(next_url, 'https://example.com/page2.html')
        
        # 测试带有next class的链接
        html_with_class = """
        <!DOCTYPE html>
        <html>
        <body>
            <a href="page3.html" class="next-page">Next</a>
        </body>
        </html>
        """
        
        next_url = self.scraper.get_next_page_url(html_with_class, base_url)
        
        # 验证结果
        self.assertEqual(next_url, 'https://example.com/page3.html')


if __name__ == '__main__':
    # 导入requests模块用于测试
    import requests
    unittest.main()