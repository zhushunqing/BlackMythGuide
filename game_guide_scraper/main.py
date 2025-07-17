#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
黑神话悟空游戏攻略爬虫主程序

这个程序从指定的起始URL开始，抓取所有相关页面内容，
包括"下一页"链接指向的所有页面，并将内容整理成一本结构化的Markdown格式攻略书。
"""

import argparse
import os
import sys
import json
import time
import textwrap
from game_guide_scraper.controller.controller import Controller
from game_guide_scraper.utils.cli import ConfigWizard, prompt_yes_no, InteractiveController


def parse_arguments():
    """解析命令行参数"""
    # 创建一个自定义的描述文本，包含更多信息
    description = """
    黑神话悟空游戏攻略爬虫
    
    这个程序从指定的起始URL开始，抓取所有相关页面内容，
    包括"下一页"链接指向的所有页面，并将内容整理成一本结构化的Markdown格式攻略书。
    
    交互式控制：
      运行过程中可以使用以下按键控制爬虫：
      - 'q': 退出爬虫
      - 'p': 暂停/恢复爬虫
      - 's': 显示当前状态
      - 'h': 显示帮助信息
    """
    
    # 使用RawDescriptionHelpFormatter保留描述中的格式
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(description),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 基本参数
    parser.add_argument('--start-url', type=str, 
                        default='https://www.gamersky.com/handbook/202408/1803231.shtml',
                        help='起始URL，爬虫将从这个URL开始抓取')
    
    parser.add_argument('--output-dir', type=str, default='output',
                        help='输出目录，用于保存生成的Markdown文件和图片')
    
    parser.add_argument('--output-file', type=str, default='guide.md',
                        help='输出文件名，生成的Markdown文件的名称')
    
    # 图片相关参数
    img_group = parser.add_argument_group('图片选项')
    img_group.add_argument('--download-images', action='store_true', default=True,
                        help='是否下载图片')
    img_group.add_argument('--no-images', dest='download_images', action='store_false',
                        help='不下载图片')
    img_group.add_argument('--image-dir', type=str, default=None,
                        help='图片保存目录，默认为output_dir/images')
    img_group.add_argument('--image-delay', type=float, default=0.5,
                        help='图片下载间隔时间（秒）')
    img_group.add_argument('--image-quality', type=str, choices=['original', 'high', 'medium', 'low'], 
                        default='original',
                        help='图片质量，影响下载的图片大小')
    img_group.add_argument('--skip-existing-images', action='store_true', default=True,
                        help='跳过已存在的图片，避免重复下载')
    img_group.add_argument('--force-download-images', dest='skip_existing_images', 
                        action='store_false',
                        help='强制重新下载所有图片，即使已存在')
    
    # 爬虫行为参数
    crawler_group = parser.add_argument_group('爬虫选项')
    crawler_group.add_argument('--delay', type=float, default=1.0,
                        help='页面请求间隔时间（秒）')
    crawler_group.add_argument('--max-retries', type=int, default=3,
                        help='请求失败时的最大重试次数')
    crawler_group.add_argument('--retry-delay', type=float, default=2.0,
                        help='请求失败后的重试间隔时间（秒）')
    crawler_group.add_argument('--timeout', type=int, default=30,
                        help='请求超时时间（秒）')
    crawler_group.add_argument('--user-agent', type=str,
                        default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        help='HTTP请求的User-Agent')
    crawler_group.add_argument('--continue-on-error', action='store_true', default=True,
                        help='遇到错误时是否继续抓取')
    crawler_group.add_argument('--stop-on-error', dest='continue_on_error', action='store_false',
                        help='遇到错误时停止抓取')
    crawler_group.add_argument('--max-pages', type=int, default=0,
                        help='最大抓取页面数，0表示不限制')
    crawler_group.add_argument('--start-page', type=int, default=1,
                        help='开始抓取的页码，用于断点续传')
    crawler_group.add_argument('--cookies', type=str, default=None,
                        help='Cookie字符串，用于需要登录的网站')
    crawler_group.add_argument('--headers', type=str, default=None,
                        help='额外的HTTP请求头，JSON格式')
    
    # 输出和日志参数
    output_group = parser.add_argument_group('输出选项')
    output_group.add_argument('--show-progress-bar', action='store_true', default=True,
                        help='是否显示进度条')
    output_group.add_argument('--no-progress-bar', dest='show_progress_bar', action='store_false',
                        help='不显示进度条')
    output_group.add_argument('--log-file', type=str, default=None,
                        help='日志文件路径，不指定则只输出到控制台')
    output_group.add_argument('--log-level', type=str, 
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO', help='日志级别')
    output_group.add_argument('--quiet', action='store_true', default=False,
                        help='安静模式，只输出错误信息')
    output_group.add_argument('--verbose', action='store_true', default=False,
                        help='详细模式，输出更多调试信息')
    output_group.add_argument('--output-format', type=str, 
                        choices=['markdown', 'html', 'text'], default='markdown',
                        help='输出格式，默认为Markdown')
    
    # 内容过滤参数
    filter_group = parser.add_argument_group('内容过滤选项')
    filter_group.add_argument('--include-keywords', type=str, default=None,
                        help='包含关键词的内容才会被抓取，多个关键词用逗号分隔')
    filter_group.add_argument('--exclude-keywords', type=str, default=None,
                        help='排除包含关键词的内容，多个关键词用逗号分隔')
    filter_group.add_argument('--min-content-length', type=int, default=0,
                        help='最小内容长度，小于此长度的页面将被忽略')
    filter_group.add_argument('--remove-ads', action='store_true', default=True,
                        help='移除广告内容')
    filter_group.add_argument('--keep-ads', dest='remove_ads', action='store_false',
                        help='保留广告内容')
    
    # 配置文件参数
    config_group = parser.add_argument_group('配置选项')
    config_group.add_argument('--config', type=str,
                        help='配置文件路径，JSON格式，会覆盖命令行参数')
    config_group.add_argument('--generate-config', type=str,
                        help='生成配置文件模板到指定路径')
    config_group.add_argument('--wizard', action='store_true',
                        help='启动配置向导，交互式配置爬虫')
    config_group.add_argument('--save-config', type=str,
                        help='保存当前配置到指定路径')
    config_group.add_argument('--config-format', type=str, 
                        choices=['json', 'yaml', 'toml'], default='json',
                        help='配置文件格式，默认为JSON')
    
    # 其他选项
    other_group = parser.add_argument_group('其他选项')
    other_group.add_argument('--version', action='store_true',
                        help='显示版本信息')
    other_group.add_argument('--examples', action='store_true',
                        help='显示使用示例')
    other_group.add_argument('--check-url', type=str, default=None,
                        help='检查URL是否可访问，不执行爬取')
    other_group.add_argument('--preview', action='store_true', default=False,
                        help='预览模式，只抓取前几页进行预览')
    other_group.add_argument('--preview-pages', type=int, default=3,
                        help='预览模式下抓取的页面数')
    other_group.add_argument('--dry-run', action='store_true', default=False,
                        help='空运行，不实际抓取内容，只显示将要执行的操作')
    other_group.add_argument('--interactive', action='store_true', default=True,
                        help='交互式模式，允许用户在运行过程中控制爬虫')
    other_group.add_argument('--non-interactive', dest='interactive', action='store_false',
                        help='非交互式模式，适用于自动化脚本')
    
    return parser.parse_args()


def load_config(config_path):
    """
    加载配置文件
    
    参数:
        config_path: 配置文件路径
        
    返回:
        配置字典
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误: 配置文件 '{config_path}' 不存在")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"错误: 配置文件 '{config_path}' 不是有效的JSON格式")
        sys.exit(1)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        sys.exit(1)


def generate_config_template(output_path):
    """
    生成配置文件模板
    
    参数:
        output_path: 输出文件路径
    """
    config_template = {
        # 基本配置
        "start_url": "https://www.gamersky.com/handbook/202408/1803231.shtml",
        "output_dir": "output",
        "output_file": "guide.md",
        
        # 图片配置
        "download_images": True,
        "image_dir": "output/images",
        "image_delay": 0.5,
        "image_quality": "original",  # 可选值: original, high, medium, low
        "skip_existing_images": True,
        
        # 爬虫配置
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "delay": 1.0,
        "max_retries": 3,
        "retry_delay": 2.0,
        "timeout": 30,
        "continue_on_error": True,
        "max_pages": 0,  # 0表示不限制
        "start_page": 1,
        "cookies": None,
        "headers": {},
        
        # 输出配置
        "show_progress_bar": True,
        "log_file": "crawler.log",
        "log_level": "INFO",  # 可选值: DEBUG, INFO, WARNING, ERROR, CRITICAL
        "quiet": False,
        "verbose": False,
        "output_format": "markdown",  # 可选值: markdown, html, text
        
        # 内容过滤配置
        "include_keywords": None,  # 多个关键词用逗号分隔
        "exclude_keywords": None,  # 多个关键词用逗号分隔
        "min_content_length": 0,
        "remove_ads": True,
        
        # 其他配置
        "interactive": True,
        "preview": False,
        "preview_pages": 3,
        "dry_run": False
    }
    
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # 写入配置文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config_template, f, ensure_ascii=False, indent=4)
            
        print(f"配置文件模板已生成到: {output_path}")
        return True
    except Exception as e:
        print(f"生成配置文件模板失败: {e}")
        return False


def show_examples():
    """显示使用示例"""
    examples = """
使用示例:
  # 基本用法
  # --------
  # 使用默认参数抓取攻略
  python -m game_guide_scraper.main
  
  # 指定起始URL和输出目录
  python -m game_guide_scraper.main --start-url "https://www.gamersky.com/handbook/202408/1803231.shtml" --output-dir "my_output"
  
  # 配置文件操作
  # ------------
  # 生成配置文件模板
  python -m game_guide_scraper.main --generate-config "my_config.json"
  
  # 使用配置文件
  python -m game_guide_scraper.main --config "my_config.json"
  
  # 启动配置向导
  python -m game_guide_scraper.main --wizard
  
  # 保存当前配置到文件
  python -m game_guide_scraper.main --save-config "my_config.json"
  
  # 图片处理选项
  # ------------
  # 不下载图片
  python -m game_guide_scraper.main --no-images
  
  # 指定图片保存目录和下载间隔
  python -m game_guide_scraper.main --image-dir "images" --image-delay 1.0
  
  # 设置图片质量
  python -m game_guide_scraper.main --image-quality medium
  
  # 强制重新下载所有图片
  python -m game_guide_scraper.main --force-download-images
  
  # 爬虫行为控制
  # ------------
  # 调整爬虫行为
  python -m game_guide_scraper.main --delay 2.0 --max-retries 5 --timeout 60
  
  # 限制最大抓取页面数
  python -m game_guide_scraper.main --max-pages 10
  
  # 从指定页码开始抓取（断点续传）
  python -m game_guide_scraper.main --start-page 5
  
  # 遇到错误时停止抓取
  python -m game_guide_scraper.main --stop-on-error
  
  # 预览模式，只抓取前几页
  python -m game_guide_scraper.main --preview --preview-pages 2
  
  # 空运行模式，不实际抓取内容
  python -m game_guide_scraper.main --dry-run
  
  # 输出和日志选项
  # --------------
  # 保存日志到文件
  python -m game_guide_scraper.main --log-file "crawler.log"
  
  # 设置日志级别
  python -m game_guide_scraper.main --log-level DEBUG
  
  # 安静模式，只输出错误信息
  python -m game_guide_scraper.main --quiet
  
  # 详细模式，输出更多调试信息
  python -m game_guide_scraper.main --verbose
  
  # 不显示进度条
  python -m game_guide_scraper.main --no-progress-bar
  
  # 输出为HTML格式
  python -m game_guide_scraper.main --output-format html
  
  # 内容过滤选项
  # ------------
  # 只抓取包含特定关键词的内容
  python -m game_guide_scraper.main --include-keywords "攻略,技巧,boss"
  
  # 排除包含特定关键词的内容
  python -m game_guide_scraper.main --exclude-keywords "广告,活动"
  
  # 设置最小内容长度
  python -m game_guide_scraper.main --min-content-length 100
  
  # 保留广告内容
  python -m game_guide_scraper.main --keep-ads
  
  # 高级用法
  # --------
  # 非交互式模式，适用于自动化脚本
  python -m game_guide_scraper.main --non-interactive
  
  # 检查URL是否可访问，不执行爬取
  python -m game_guide_scraper.main --check-url "https://www.gamersky.com/handbook/202408/1803231.shtml"
  
  # 设置自定义HTTP请求头
  python -m game_guide_scraper.main --headers '{"Referer": "https://www.gamersky.com/"}'
  
  # 组合使用多个选项
  python -m game_guide_scraper.main --start-url "https://www.gamersky.com/handbook/202408/1803231.shtml" \\
                                  --output-dir "output" \\
                                  --delay 2.0 \\
                                  --max-retries 5 \\
                                  --log-file "crawler.log" \\
                                  --image-quality high
"""
    print(examples)


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 如果没有参数，显示帮助信息和示例
    if len(sys.argv) == 1:
        parser = argparse.ArgumentParser()
        parser.parse_args(['--help'])
        show_examples()
        return 0
    
    # 显示版本信息
    if args.version:
        print("黑神话悟空游戏攻略爬虫 v1.0.0")
        return 0
        
    # 显示使用示例
    if args.examples:
        show_examples()
        return 0
    
    # 如果指定了生成配置文件模板，则生成后退出
    if args.generate_config:
        success = generate_config_template(args.generate_config)
        return 0 if success else 1
    
    # 从命令行参数构建配置
    config = vars(args)  # 将命令行参数转换为字典
    
    # 如果指定了配置向导，则启动配置向导
    if args.wizard:
        print("启动配置向导...")
        wizard = ConfigWizard(config)
        wizard_config = wizard.run()
        
        if not wizard_config:
            print("配置向导已取消")
            return 0
            
        # 使用向导生成的配置
        config.update(wizard_config)
        
        # 如果指定了保存配置，则保存配置
        if args.save_config:
            if wizard.save_config(config, args.save_config):
                print(f"配置已保存到: {args.save_config}")
            else:
                print(f"保存配置失败")
                return 1
    
    # 如果提供了配置文件，则加载配置并覆盖命令行参数
    if args.config:
        print(f"正在加载配置文件: {args.config}")
        file_config = load_config(args.config)
        config.update(file_config)
        
    # 如果指定了保存配置，但没有使用向导，则保存当前配置
    if args.save_config and not args.wizard:
        try:
            # 确保目录存在
            save_dir = os.path.dirname(os.path.abspath(args.save_config))
            if save_dir:
                os.makedirs(save_dir, exist_ok=True)
                
            # 写入配置文件
            with open(args.save_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
                
            print(f"配置已保存到: {args.save_config}")
        except Exception as e:
            print(f"保存配置失败: {e}")
            return 1
    
    # 处理特殊配置
    if config['image_dir'] is None:
        config['image_dir'] = os.path.join(config['output_dir'], 'images')
    
    # 确保输出目录存在
    os.makedirs(config['output_dir'], exist_ok=True)
    if config['download_images']:
        os.makedirs(config['image_dir'], exist_ok=True)
    
    # 如果指定了日志文件，确保日志目录存在
    if config.get('log_file'):
        log_dir = os.path.dirname(os.path.abspath(config['log_file']))
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
    
    # 显示启动信息
    print("=" * 60)
    print("黑神话悟空游戏攻略爬虫")
    print("=" * 60)
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    print(f"起始URL: {config['start_url']}")
    print(f"输出目录: {config['output_dir']}")
    print(f"输出文件: {config['output_file']}")
    print(f"是否下载图片: {'是' if config['download_images'] else '否'}")
    if config['download_images']:
        print(f"图片保存目录: {config['image_dir']}")
    print("=" * 60)
    
    # 导入交互式控制器 (已在文件顶部导入)
    
    # 创建交互式控制器
    interactive = InteractiveController(config)
    
    # 创建并运行控制器
    try:
        # 设置进度回调函数
        config['progress_callback'] = interactive.update_progress
        
        # 创建控制器
        controller = Controller(config)
        
        # 启动交互式控制器
        interactive.start()
        
        # 注册回调函数
        def quit_callback():
            # 这里可以添加退出前的清理工作
            pass
        
        interactive.register_callback('quit', quit_callback)
        
        # 运行控制器
        result = controller.run()
        
        # 停止交互式控制器
        interactive.stop()
        
        # 显示结果摘要
        if result and result.get('success'):
            print("\n爬虫运行成功！")
            print(f"攻略已保存到: {result['output_file']}")
            print(f"处理页面数: {result['pages_processed']}")
            if config['download_images']:
                print(f"下载图片数: {result['images_processed']}")
                
            # 询问用户是否打开生成的文件
            if sys.platform.startswith('darwin'):  # macOS
                if prompt_yes_no("是否打开生成的攻略文件?"):
                    os.system(f"open '{result['output_file']}'")
            elif sys.platform.startswith('win'):  # Windows
                if prompt_yes_no("是否打开生成的攻略文件?"):
                    os.system(f'start "" "{result["output_file"]}"')
            elif sys.platform.startswith('linux'):  # Linux
                if prompt_yes_no("是否打开生成的攻略文件?"):
                    os.system(f"xdg-open '{result['output_file']}'")
        else:
            print("\n爬虫运行失败！")
            if result:
                print(f"处理页面数: {result.get('pages_processed', 0)}")
                if config['download_images']:
                    print(f"下载图片数: {result.get('images_processed', 0)}")
        
        return 0 if result and result.get('success') else 1
    
    except KeyboardInterrupt:
        print("\n用户中断，爬虫已停止")
        interactive.stop()
        return 130  # 标准的SIGINT退出码
    except Exception as e:
        print(f"\n爬虫运行出错: {e}")
        interactive.stop()
        return 1


if __name__ == '__main__':
    sys.exit(main())