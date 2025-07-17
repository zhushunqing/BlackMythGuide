"""
图片下载器模块，负责下载和保存图片文件。
"""

import os
import time
import hashlib
import requests
from urllib.parse import urlparse
from typing import Dict, List, Optional, Any

class ImageDownloader:
    """
    图片下载器类，用于下载和保存图片文件。
    """
    
    def __init__(self, output_dir, delay=0.5):
        """
        初始化图片下载器
        
        参数:
            output_dir: 图片保存目录
            delay: 下载间隔时间（秒）
        """
        self.output_dir = output_dir
        self.delay = delay
        self.last_download_time = 0
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
    
    def download_image(self, url, filename=None):
        """
        下载图片并保存到本地
        
        参数:
            url: 图片URL
            filename: 保存的文件名，如果为None则自动生成
            
        返回:
            保存后的本地文件路径，如果下载失败则返回None
        """
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
        
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image {url}: {e}")
            return None
        except IOError as e:
            print(f"Error saving image {url} to {local_path}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error when downloading image {url}: {e}")
            return None
            
    def download_all_images(self, image_list: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        批量下载图片
        
        参数:
            image_list: 图片信息列表，每个元素应该是一个字典，至少包含'url'键
            
        返回:
            图片URL到本地路径的映射字典，如果某张图片下载失败，则不会出现在结果中
        """
        result = {}
        total_images = len(image_list)
        
        print(f"开始下载 {total_images} 张图片...")
        
        for i, image_info in enumerate(image_list):
            # 检查图片信息是否有效
            if not isinstance(image_info, dict) or 'url' not in image_info:
                print(f"跳过无效的图片信息: {image_info}")
                continue
                
            url = image_info['url']
            print(f"下载图片 {i+1}/{total_images}: {url}")
            
            # 下载图片
            local_path = self.download_image(url)
            
            # 如果下载成功，更新映射和图片信息
            if local_path:
                result[url] = local_path
                image_info['local_path'] = local_path
                print(f"图片已保存到: {local_path}")
            else:
                print(f"图片下载失败: {url}")
                
        print(f"图片下载完成。成功: {len(result)}/{total_images}")
        return result