#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
控制器模块

这个模块包含Controller类，负责协调各组件工作，管理整个抓取和生成过程。
"""

import os
import time
from game_guide_scraper.scraper.scraper import Scraper
from game_guide_scraper.parser.parser import Parser
from game_guide_scraper.downloader.downloader import ImageDownloader
from game_guide_scraper.organizer.organizer import ContentOrganizer
from game_guide_scraper.generator.markdown_generator import MarkdownGenerator


class Controller:
    """控制器类，协调各组件工作，管理整个抓取和生成过程"""
    
    def __init__(self, config=None):
        """
        初始化控制器
        
        参数:
            config: 配置字典，如果为None则使用默认配置
        """
        # 处理配置
        self.config = self._process_config(config or {})
        
        # 初始化各组件
        self.scraper = Scraper(
            user_agent=self.config['user_agent'],
            delay=self.config['delay'],
            max_retries=self.config['max_retries'],
            retry_delay=self.config['retry_delay']
        )
        
        self.parser = Parser()
        self.content_organizer = ContentOrganizer()
        
        # 如果配置了下载图片，则初始化图片下载器
        if self.config['download_images']:
            self.image_downloader = ImageDownloader(
                output_dir=self.config['image_dir'],
                delay=self.config['image_delay']
            )
        else:
            self.image_downloader = None
            
    def _process_config(self, user_config):
        """
        处理用户配置，设置默认值
        
        参数:
            user_config: 用户提供的配置字典
            
        返回:
            处理后的配置字典
        """
        # 默认配置
        default_config = {
            # 基本配置
            'start_url': None,  # 必须由用户提供
            'output_dir': 'output',
            'output_file': 'guide.md',
            
            # 爬虫配置
            'user_agent': 'GameGuideScraper/1.0',
            'delay': 1.0,  # 请求间隔时间（秒）
            'max_retries': 3,  # 最大重试次数
            'retry_delay': 2.0,  # 重试间隔时间（秒）
            
            # 图片配置
            'download_images': True,  # 是否下载图片
            'image_dir': None,  # 图片保存目录，如果为None则使用output_dir/images
            'image_delay': 0.5,  # 图片下载间隔时间（秒）
            'skip_existing_images': True,  # 是否跳过已存在的图片文件
            
            # 进度报告配置
            'show_progress_bar': True,  # 是否显示进度条
            'log_file': None,  # 日志文件路径
            'progress_callback': None,  # 进度回调函数
            
            # 高级配置
            'timeout': 30,  # 请求超时时间（秒）
            'encoding': 'utf-8',  # 网页编码
            'headers': {},  # 额外的HTTP请求头
            'proxies': None,  # 代理设置
        }
        
        # 合并用户配置和默认配置
        config = {**default_config, **user_config}
        
        # 处理依赖配置
        if config['image_dir'] is None:
            config['image_dir'] = os.path.join(config['output_dir'], 'images')
            
        # 验证必要的配置
        if config['start_url'] is None:
            print("警告: 未指定起始URL，请在运行前设置start_url")
            
        return config
    
    def run(self):
        """运行爬虫，协调各组件完成抓取和生成过程"""
        start_time = time.time()
        self.report_progress("开始运行爬虫")
        
        # 输出配置信息
        self.report_progress(f"起始URL: {self.config['start_url'] or '未指定'}")
        self.report_progress(f"输出目录: {self.config['output_dir']}")
        self.report_progress(f"输出文件: {self.config['output_file']}")
        self.report_progress(f"是否下载图片: {self.config['download_images']}")
        self.report_progress(f"请求间隔时间: {self.config['delay']}秒")
        
        # 确保输出目录存在
        os.makedirs(self.config['output_dir'], exist_ok=True)
        
        # 如果下载图片，确保图片目录存在
        if self.config['download_images']:
            os.makedirs(self.config['image_dir'], exist_ok=True)
            
        # 确保日志目录存在
        if self.config['log_file']:
            log_dir = os.path.dirname(self.config['log_file'])
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
        
        # 获取起始URL
        url = self.config['start_url']
        if not url:
            self.report_progress("错误: 未指定起始URL", 0)
            return
        
        # 初始化页码计数器和统计信息
        page_number = 1
        total_pages_processed = 0
        total_images_processed = 0
        failed_pages = []
        failed_images = []
        
        # 抓取和处理页面
        while url:
            # 检查预览模式限制
            if self.config.get('preview', False):
                preview_pages = self.config.get('preview_pages', 3)
                if total_pages_processed >= preview_pages:
                    self.report_progress(f"预览模式：已抓取 {preview_pages} 页，停止抓取")
                    break
            
            # 报告进度
            self.report_progress(f"正在抓取第 {page_number} 页: {url}")
            
            try:
                # 抓取页面
                html = self.scraper.fetch_page(url)
                if not html:
                    self.report_progress(f"无法抓取页面: {url}")
                    failed_pages.append({'url': url, 'reason': '无法获取HTML内容'})
                    if self.config.get('continue_on_error', True):
                        # 如果配置了继续处理，则尝试获取下一页
                        next_url = None
                        try:
                            next_url = self.scraper.get_next_page_url(html, url)
                        except:
                            pass
                        
                        if next_url and next_url != url:
                            url = next_url
                            page_number += 1
                            continue
                        else:
                            break
                    else:
                        break
                
                # 解析内容
                content = self.parser.parse_content(html)
                if not content:
                    self.report_progress(f"无法解析页面内容: {url}")
                    failed_pages.append({'url': url, 'reason': '无法解析页面内容'})
                    if not self.config.get('continue_on_error', True):
                        break
                    
                    # 尝试获取下一页并继续
                    next_url = self.scraper.get_next_page_url(html, url)
                    if next_url and next_url != url:
                        url = next_url
                        page_number += 1
                        continue
                    else:
                        break
                
                # 添加页面信息
                content['url'] = url
                content['page_number'] = page_number
                
                # 下载图片（如果需要）
                if self.image_downloader:
                    image_items = [item for item in content.get('content', []) if item.get('type') == 'image']
                    if image_items:
                        self.report_progress(f"正在下载第 {page_number} 页的图片 ({len(image_items)} 张)")
                        skip_existing = self.config.get('skip_existing_images', True)
                        download_results = self.image_downloader.download_all_images(image_items, skip_existing=skip_existing)
                        
                        # 统计图片下载结果
                        successful_downloads = sum(1 for item in image_items if 'local_path' in item)
                        total_images_processed += successful_downloads
                        
                        # 记录失败的图片
                        for item in image_items:
                            if item.get('type') == 'image' and 'url' in item and 'local_path' not in item:
                                failed_images.append({'url': item['url'], 'page': url})
                        
                        if successful_downloads < len(image_items):
                            self.report_progress(f"警告: 第 {page_number} 页有 {len(image_items) - successful_downloads} 张图片下载失败")
                
                # 添加到内容组织器
                self.content_organizer.add_page_content(content)
                
                # 获取下一页URL
                next_url = self.scraper.get_next_page_url(html, url)
                
                # 避免无限循环
                if next_url == url:
                    self.report_progress(f"检测到循环链接，停止抓取: {url}")
                    break
                
                # 更新URL和页码
                url = next_url
                page_number += 1
                total_pages_processed += 1
                
                # 计算并报告总体进度
                # 由于我们不知道总页数，所以无法准确计算百分比
                # 这里只报告已处理的页数
                self.report_progress(f"已处理 {total_pages_processed} 个页面")
                
                # 如果没有下一页，结束循环
                if not url:
                    self.report_progress("已到达最后一页")
                    
            except Exception as e:
                # 捕获所有异常，确保爬虫不会因为单个页面的错误而完全停止
                self.report_progress(f"处理页面 {url} 时出错: {str(e)}")
                failed_pages.append({'url': url, 'reason': str(e)})
                
                if self.config.get('continue_on_error', True):
                    # 尝试获取下一页并继续
                    try:
                        next_url = self.scraper.get_next_page_url(html, url)
                        if next_url and next_url != url:
                            url = next_url
                            page_number += 1
                            continue
                        else:
                            break
                    except:
                        # 如果无法获取下一页，则停止抓取
                        self.report_progress("无法获取下一页，停止抓取")
                        break
                else:
                    break
        
        # 组织内容
        self.report_progress("正在组织内容...")
        organized_content = self.content_organizer.organize_content()
        
        # 收集图片映射
        image_mapping = {}
        if self.image_downloader:
            # 从所有章节和小节中收集图片映射
            for chapter in organized_content.get('chapters', []):
                for item in chapter.get('content', []):
                    if item.get('type') == 'image' and 'url' in item and 'local_path' in item:
                        image_mapping[item['url']] = item['local_path']
                
                for section in chapter.get('sections', []):
                    for item in section.get('content', []):
                        if item.get('type') == 'image' and 'url' in item and 'local_path' in item:
                            image_mapping[item['url']] = item['local_path']
        
        # 生成Markdown
        self.report_progress("正在生成Markdown...")
        markdown_generator = MarkdownGenerator(image_mapping)
        markdown = markdown_generator.generate_markdown(organized_content)
        
        # 保存Markdown
        output_file = os.path.join(
            self.config['output_dir'],
            self.config['output_file']
        )
        self.report_progress(f"正在保存Markdown到 {output_file}...")
        success = markdown_generator.save_markdown(markdown, output_file)
        
        # 计算运行时间
        end_time = time.time()
        run_time = end_time - start_time
        hours, remainder = divmod(run_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = ""
        if hours > 0:
            time_str += f"{int(hours)}小时"
        if minutes > 0:
            time_str += f"{int(minutes)}分钟"
        time_str += f"{int(seconds)}秒"
        
        # 输出统计信息
        self.report_progress("爬虫运行完成", 100)
        self.report_progress(f"总运行时间: {time_str}")
        self.report_progress(f"处理页面数: {total_pages_processed}")
        
        if self.config['download_images']:
            self.report_progress(f"下载图片数: {total_images_processed}")
            if failed_images:
                self.report_progress(f"图片下载失败数: {len(failed_images)}")
        
        if failed_pages:
            self.report_progress(f"页面处理失败数: {len(failed_pages)}")
            for i, failed_page in enumerate(failed_pages[:10], 1):  # 只显示前10个失败页面
                self.report_progress(f"  失败页面 {i}: {failed_page['url']} - 原因: {failed_page['reason']}")
            if len(failed_pages) > 10:
                self.report_progress(f"  ... 以及其他 {len(failed_pages) - 10} 个失败页面")
        
        # 返回结果摘要
        result_summary = {
            'success': success,
            'output_file': output_file if success else None,
            'pages_processed': total_pages_processed,
            'images_processed': total_images_processed,
            'failed_pages': failed_pages,
            'failed_images': failed_images,
            'run_time': run_time
        }
        
        if success:
            self.report_progress(f"攻略已成功保存到 {output_file}", 100)
        else:
            self.report_progress(f"保存攻略时出错", 100)
            
        return result_summary
    
    def report_progress(self, message, percentage=None):
        """
        报告进度
        
        参数:
            message: 进度消息
            percentage: 完成百分比（0-100）
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        progress_str = f"[{timestamp}] {message}"
        
        if percentage is not None:
            progress_str += f" ({percentage:.1f}%)"
        
        # 如果提供了回调函数，则优先调用回调函数
        progress_callback = self.config.get('progress_callback')
        if progress_callback and callable(progress_callback):
            try:
                progress_callback(message, percentage)
                # 如果有回调函数，则不再直接输出到控制台
                log_only = True
            except Exception as e:
                print(f"调用进度回调函数时出错: {e}")
                log_only = False
        else:
            log_only = False
            
        # 如果没有回调函数或回调函数出错，则直接输出到控制台
        if not log_only:
            # 如果配置了进度条显示，则显示进度条
            if percentage is not None and self.config.get('show_progress_bar', True):
                bar_length = 30
                filled_length = int(bar_length * percentage / 100)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                progress_str += f"\n[{bar}]"
                
            # 输出到控制台
            print(progress_str)
        
        # 无论是否有回调函数，都写入日志文件（如果配置了）
        log_file = self.config.get('log_file')
        if log_file:
            try:
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(progress_str + '\n')
            except Exception as e:
                print(f"写入日志文件时出错: {e}")