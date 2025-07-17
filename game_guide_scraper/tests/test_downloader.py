"""
测试图片下载器模块的功能。
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from game_guide_scraper.downloader.downloader import ImageDownloader


class TestImageDownloader(unittest.TestCase):
    """测试ImageDownloader类的功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 使用临时目录作为输出目录
        self.output_dir = os.path.join(os.path.dirname(__file__), 'temp_images')
        # 创建下载器实例
        self.downloader = ImageDownloader(self.output_dir, delay=0.01)  # 使用较短的延迟以加快测试
        
        # 测试用的图片信息列表
        self.test_images = [
            {'type': 'image', 'url': 'https://example.com/image1.jpg', 'alt': '测试图片1'},
            {'type': 'image', 'url': 'https://example.com/image2.png', 'alt': '测试图片2'},
            {'type': 'image', 'url': 'https://example.com/image3.gif', 'alt': '测试图片3'},
            {'type': 'text', 'value': '这不是图片'},  # 这个应该被跳过
            {'type': 'image', 'alt': '没有URL的图片'}  # 这个应该被跳过
        ]
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除测试过程中创建的临时文件和目录
        if os.path.exists(self.output_dir):
            for file in os.listdir(self.output_dir):
                os.remove(os.path.join(self.output_dir, file))
            try:
                os.rmdir(self.output_dir)
            except OSError:
                pass  # 如果目录不为空或有其他问题，忽略错误
    
    @patch('requests.get')
    def test_download_image(self, mock_get):
        """测试单个图片下载功能"""
        # 模拟请求响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_content.return_value = [b'fake image data']
        mock_get.return_value = mock_response
        
        # 测试下载图片
        url = 'https://example.com/test.jpg'
        result = self.downloader.download_image(url)
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.startswith(self.output_dir))
        
        # 验证请求是否正确发送
        mock_get.assert_called_once_with(url, stream=True, timeout=10)
    
    @patch('requests.get')
    def test_download_image_with_error(self, mock_get):
        """测试图片下载失败的情况"""
        # 模拟请求异常
        mock_get.side_effect = Exception("模拟下载失败")
        
        # 测试下载图片
        url = 'https://example.com/test.jpg'
        result = self.downloader.download_image(url)
        
        # 验证结果
        self.assertIsNone(result)
    
    @patch('game_guide_scraper.downloader.downloader.ImageDownloader.download_image')
    def test_download_all_images(self, mock_download_image):
        """测试批量下载图片功能"""
        # 模拟download_image方法的行为
        def side_effect(url):
            if 'image1' in url:
                return os.path.join(self.output_dir, 'image1.jpg')
            elif 'image2' in url:
                return os.path.join(self.output_dir, 'image2.png')
            elif 'image3' in url:
                return None  # 模拟下载失败
            return None
        
        mock_download_image.side_effect = side_effect
        
        # 测试批量下载图片
        result = self.downloader.download_all_images(self.test_images)
        
        # 验证结果
        self.assertEqual(len(result), 2)  # 应该只有2个成功的下载
        self.assertIn('https://example.com/image1.jpg', result)
        self.assertIn('https://example.com/image2.png', result)
        self.assertNotIn('https://example.com/image3.gif', result)  # 这个应该下载失败
        
        # 验证download_image被调用的次数
        self.assertEqual(mock_download_image.call_count, 3)  # 应该调用3次（跳过非图片和没有URL的项）
    
    @patch('game_guide_scraper.downloader.downloader.ImageDownloader.download_image')
    def test_download_all_images_updates_image_info(self, mock_download_image):
        """测试批量下载图片时是否正确更新图片信息"""
        # 模拟download_image方法的行为
        local_path = os.path.join(self.output_dir, 'image1.jpg')
        mock_download_image.return_value = local_path
        
        # 创建一个图片信息的副本用于测试
        test_image = {'type': 'image', 'url': 'https://example.com/image1.jpg', 'alt': '测试图片'}
        test_images = [test_image]
        
        # 测试批量下载图片
        self.downloader.download_all_images(test_images)
        
        # 验证图片信息是否被更新
        self.assertIn('local_path', test_image)
        self.assertEqual(test_image['local_path'], local_path)


if __name__ == '__main__':
    unittest.main()