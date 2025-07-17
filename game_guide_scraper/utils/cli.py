#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
命令行交互工具模块

这个模块提供了命令行交互功能，包括进度条显示、用户输入处理等。
"""

import sys
import time
import threading
import shutil
import os
import json
from typing import Callable, Optional, Dict, Any, List, Tuple


class ProgressBar:
    """进度条类，用于在命令行中显示进度"""
    
    def __init__(self, total: int = 100, prefix: str = '', suffix: str = '', 
                 decimals: int = 1, length: int = 50, fill: str = '█', 
                 print_end: str = '\r'):
        """
        初始化进度条
        
        参数:
            total: 总进度值
            prefix: 进度条前缀字符串
            suffix: 进度条后缀字符串
            decimals: 百分比小数位数
            length: 进度条长度
            fill: 进度条填充字符
            print_end: 打印结束字符
        """
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill
        self.print_end = print_end
        self.current = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.update_interval = 0.1  # 更新间隔（秒）
        
        # 获取终端宽度
        self.terminal_width = shutil.get_terminal_size().columns
        
    def update(self, current: int, prefix: Optional[str] = None, suffix: Optional[str] = None):
        """
        更新进度条
        
        参数:
            current: 当前进度值
            prefix: 进度条前缀字符串（可选）
            suffix: 进度条后缀字符串（可选）
        """
        self.current = current
        
        # 限制更新频率
        current_time = time.time()
        if current_time - self.last_update_time < self.update_interval and current < self.total:
            return
        self.last_update_time = current_time
        
        # 更新前缀和后缀
        if prefix is not None:
            self.prefix = prefix
        if suffix is not None:
            self.suffix = suffix
            
        # 计算进度百分比
        percent = ('{0:.' + str(self.decimals) + 'f}').format(100 * (current / float(self.total)))
        
        # 计算已用时间和预估剩余时间
        elapsed_time = current_time - self.start_time
        if current > 0:
            eta = elapsed_time * (self.total / current - 1)
            time_info = f" {format_time(elapsed_time)} / {format_time(eta)}"
        else:
            time_info = f" {format_time(elapsed_time)} / ?"
            
        # 计算进度条填充长度
        filled_length = int(self.length * current // self.total)
        bar = self.fill * filled_length + '░' * (self.length - filled_length)
        
        # 构建进度条字符串
        progress_bar = f'{self.prefix} |{bar}| {percent}% {self.suffix}{time_info}'
        
        # 如果字符串太长，截断它
        if len(progress_bar) > self.terminal_width - 1:
            progress_bar = progress_bar[:self.terminal_width - 4] + '...'
            
        # 打印进度条
        print(f'\r{progress_bar}', end=self.print_end)
        sys.stdout.flush()
        
        # 如果完成，打印换行符
        if current >= self.total:
            print()
            
    def finish(self):
        """完成进度条"""
        self.update(self.total)


class InteractiveController:
    """交互式控制器类，用于处理用户输入和显示进度"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化交互式控制器
        
        参数:
            config: 配置字典
        """
        self.config = config
        self.running = False
        self.paused = False
        self.progress_bar = None
        self.input_thread = None
        self.current_page = 0
        self.total_pages = 0  # 未知总页数时为0
        self.current_images = 0
        self.total_images = 0
        self.start_time = None
        self.callbacks = {}
        
    def start(self):
        """启动交互式控制器"""
        self.running = True
        self.paused = False
        self.start_time = time.time()
        
        # 启动输入处理线程
        self.input_thread = threading.Thread(target=self._input_handler)
        self.input_thread.daemon = True
        self.input_thread.start()
        
        # 显示帮助信息
        self._show_help()
        
    def stop(self):
        """停止交互式控制器"""
        self.running = False
        if self.input_thread and self.input_thread.is_alive():
            self.input_thread.join(1.0)  # 等待输入线程结束，最多1秒
            
    def pause(self):
        """暂停爬虫"""
        self.paused = True
        print("\n爬虫已暂停。按 'c' 继续，按 'h' 查看帮助。")
        
    def resume(self):
        """恢复爬虫"""
        self.paused = False
        print("\n爬虫已恢复运行。")
        
    def update_progress(self, message: str, percentage: Optional[float] = None):
        """
        更新进度信息
        
        参数:
            message: 进度消息
            percentage: 完成百分比（0-100）
        """
        # 如果是页面进度更新
        if "正在抓取第" in message and "页" in message:
            try:
                self.current_page = int(message.split("第")[1].split("页")[0].strip())
                if self.progress_bar is None and self.config.get('show_progress_bar', True):
                    self.progress_bar = ProgressBar(
                        total=100,  # 假设总进度为100
                        prefix="抓取进度:",
                        suffix=f"第 {self.current_page} 页",
                        length=30
                    )
                elif self.progress_bar:
                    # 更新进度条
                    progress = self.current_page if self.total_pages == 0 else min(100, int(100 * self.current_page / self.total_pages))
                    self.progress_bar.update(
                        current=progress,
                        suffix=f"第 {self.current_page} 页" + (f" / {self.total_pages}" if self.total_pages > 0 else "")
                    )
            except:
                pass
                
        # 如果是图片下载进度更新
        elif "正在下载第" in message and "页的图片" in message:
            try:
                page = int(message.split("第")[1].split("页")[0].strip())
                images = int(message.split("(")[1].split("张")[0].strip())
                self.current_images += images
                if self.progress_bar:
                    self.progress_bar.suffix = f"第 {self.current_page} 页 - 已下载 {self.current_images} 张图片"
            except:
                pass
                
        # 如果是完成消息
        elif percentage == 100:
            if self.progress_bar:
                self.progress_bar.finish()
                self.progress_bar = None
            print(message)
            
        # 其他消息直接打印
        else:
            # 如果有进度条，先清除进度条
            if self.progress_bar and percentage is not None:
                print()
            print(message)
            # 如果有进度条，重新显示进度条
            if self.progress_bar and percentage is not None:
                self.progress_bar.update(
                    current=int(percentage),
                    suffix=f"第 {self.current_page} 页" + (f" / {self.total_pages}" if self.total_pages > 0 else "")
                )
                
    def register_callback(self, name: str, callback: Callable):
        """
        注册回调函数
        
        参数:
            name: 回调函数名称
            callback: 回调函数
        """
        self.callbacks[name] = callback
        
    def _input_handler(self):
        """输入处理线程函数"""
        while self.running:
            try:
                # 非阻塞式输入（仅在Unix系统上有效）
                import select
                import termios
                import tty
                
                # 保存终端设置
                old_settings = termios.tcgetattr(sys.stdin)
                try:
                    # 设置终端为原始模式
                    tty.setcbreak(sys.stdin.fileno())
                    
                    # 检查是否有输入
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1)
                        self._process_key(key)
                finally:
                    # 恢复终端设置
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except (ImportError, AttributeError, termios.error):
                # 在Windows或其他不支持的系统上，使用阻塞式输入
                try:
                    import msvcrt
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8')
                        self._process_key(key)
                    time.sleep(0.1)
                except ImportError:
                    # 如果都不支持，则退出输入处理
                    print("警告: 当前系统不支持交互式控制")
                    break
                    
            time.sleep(0.1)
            
    def _process_key(self, key: str):
        """
        处理按键输入
        
        参数:
            key: 按键字符
        """
        if key == 'q':
            # 退出
            print("\n用户请求退出，正在停止爬虫...")
            if 'quit' in self.callbacks:
                self.callbacks['quit']()
            else:
                self.running = False
                
        elif key == 'p':
            # 暂停/恢复
            if self.paused:
                self.resume()
                if 'resume' in self.callbacks:
                    self.callbacks['resume']()
            else:
                self.pause()
                if 'pause' in self.callbacks:
                    self.callbacks['pause']()
                    
        elif key == 'c' and self.paused:
            # 继续
            self.resume()
            if 'resume' in self.callbacks:
                self.callbacks['resume']()
                
        elif key == 's':
            # 显示状态
            self._show_status()
            
        elif key == 'h':
            # 显示帮助
            self._show_help()
            
        elif key == 'i':
            # 显示当前页面信息
            self._show_page_info()
            
        elif key == 'd':
            # 显示下载统计
            self._show_download_stats()
            
        elif key == 'o':
            # 打开输出目录
            self._open_output_dir()
            
        elif key == '+' or key == '=':
            # 增加请求延迟
            self._adjust_delay(0.5)
            
        elif key == '-':
            # 减少请求延迟
            self._adjust_delay(-0.5)
            
        elif key == 'l':
            # 显示日志
            self._show_log()
            
    def _show_help(self):
        """显示帮助信息"""
        print("\n--- 交互式控制帮助 ---")
        print("按 'q' 退出爬虫")
        print("按 'p' 暂停/恢复爬虫")
        print("按 'c' 继续（当爬虫暂停时）")
        print("按 's' 显示当前状态")
        print("按 'i' 显示当前页面信息")
        print("按 'd' 显示下载统计")
        print("按 'o' 打开输出目录")
        print("按 '+' 增加请求延迟（减慢爬取速度）")
        print("按 '-' 减少请求延迟（加快爬取速度）")
        print("按 'l' 显示最近的日志")
        print("按 'h' 显示此帮助信息")
        print("----------------------")
        
    def _show_status(self):
        """显示当前状态"""
        if not self.start_time:
            return
            
        elapsed_time = time.time() - self.start_time
        
        print("\n--- 爬虫状态 ---")
        print(f"运行时间: {format_time(elapsed_time)}")
        print(f"当前页面: {self.current_page}" + (f" / {self.total_pages}" if self.total_pages > 0 else ""))
        print(f"已下载图片: {self.current_images}" + (f" / {self.total_images}" if self.total_images > 0 else ""))
        print(f"状态: {'暂停' if self.paused else '运行中'}")
        
        # 计算速度
        if elapsed_time > 0:
            pages_per_second = self.current_page / elapsed_time
            images_per_second = self.current_images / elapsed_time
            print(f"页面抓取速度: {pages_per_second:.2f} 页/秒")
            print(f"图片下载速度: {images_per_second:.2f} 张/秒")
            
        # 估计剩余时间
        if self.total_pages > 0 and self.current_page > 0:
            remaining_pages = self.total_pages - self.current_page
            time_per_page = elapsed_time / self.current_page
            eta = remaining_pages * time_per_page
            print(f"预计剩余时间: {format_time(eta)}")
            
        print("----------------")
        
    def _show_page_info(self):
        """显示当前页面信息"""
        print("\n--- 当前页面信息 ---")
        print(f"当前页面: {self.current_page}")
        if self.total_pages > 0:
            print(f"总页面数: {self.total_pages}")
            print(f"进度: {self.current_page}/{self.total_pages} ({100 * self.current_page / self.total_pages:.1f}%)")
        else:
            print("总页面数: 未知")
        print("--------------------")
        
    def _show_download_stats(self):
        """显示下载统计"""
        if not self.start_time:
            return
            
        elapsed_time = time.time() - self.start_time
        
        print("\n--- 下载统计 ---")
        print(f"已下载图片: {self.current_images}")
        if self.total_images > 0:
            print(f"总图片数: {self.total_images}")
            print(f"下载进度: {self.current_images}/{self.total_images} ({100 * self.current_images / self.total_images:.1f}%)")
        else:
            print("总图片数: 未知")
            
        if elapsed_time > 0 and self.current_images > 0:
            download_speed = self.current_images / elapsed_time
            print(f"平均下载速度: {download_speed:.2f} 张/秒")
            
            if self.total_images > 0:
                remaining_images = self.total_images - self.current_images
                eta = remaining_images / download_speed
                print(f"预计剩余时间: {format_time(eta)}")
                
        print("----------------")
        
    def _open_output_dir(self):
        """打开输出目录"""
        output_dir = self.config.get('output_dir', 'output')
        
        if not os.path.exists(output_dir):
            print(f"\n输出目录不存在: {output_dir}")
            return
            
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Windows":
                subprocess.run(['explorer', output_dir])
            elif system == "Darwin":  # macOS
                subprocess.run(['open', output_dir])
            elif system == "Linux":
                subprocess.run(['xdg-open', output_dir])
            else:
                print(f"\n不支持的操作系统: {system}")
                print(f"请手动打开目录: {os.path.abspath(output_dir)}")
                return
                
            print(f"\n已打开输出目录: {os.path.abspath(output_dir)}")
        except Exception as e:
            print(f"\n打开输出目录失败: {e}")
            print(f"请手动打开目录: {os.path.abspath(output_dir)}")
            
    def _adjust_delay(self, adjustment: float):
        """
        调整请求延迟
        
        参数:
            adjustment: 延迟调整量（秒）
        """
        current_delay = self.config.get('delay', 1.0)
        new_delay = max(0.1, current_delay + adjustment)  # 最小延迟0.1秒
        self.config['delay'] = new_delay
        
        print(f"\n请求延迟已调整: {current_delay:.1f}秒 -> {new_delay:.1f}秒")
        
        # 如果有调整延迟的回调函数，则调用它
        if 'adjust_delay' in self.callbacks:
            self.callbacks['adjust_delay'](new_delay)
            
    def _show_log(self):
        """显示最近的日志"""
        log_file = self.config.get('log_file')
        
        if not log_file or not os.path.exists(log_file):
            print("\n没有日志文件或日志文件不存在")
            return
            
        try:
            print("\n--- 最近的日志 (最后20行) ---")
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # 显示最后20行
                for line in lines[-20:]:
                    print(line.rstrip())
            print("---------------------------")
        except Exception as e:
            print(f"\n读取日志文件失败: {e}")


def format_time(seconds: float) -> str:
    """
    格式化时间
    
    参数:
        seconds: 秒数
        
    返回:
        格式化后的时间字符串
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"


def prompt_yes_no(question: str, default: bool = True) -> bool:
    """
    提示用户回答Y/N问题
    
    参数:
        question: 问题
        default: 默认答案
        
    返回:
        用户的回答（True表示是，False表示否）
    """
    default_prompt = "Y" if default else "N"
    prompt = f"{question} [Y/N] (默认: {default_prompt}): "
    
    while True:
        response = input(prompt).strip().lower()
        
        if not response:
            return default
            
        if response in ['y', 'yes', '是', '是的', 'true', 't', '1']:
            return True
            
        if response in ['n', 'no', '否', '不', 'false', 'f', '0']:
            return False
            
        print("请输入 'Y' 或 'N'")


def prompt_choice(question: str, choices: List[Tuple[str, str]], default: Optional[str] = None) -> str:
    """
    提示用户从多个选项中选择
    
    参数:
        question: 问题
        choices: 选项列表，每个选项是一个元组 (值, 描述)
        default: 默认选项值
        
    返回:
        用户选择的选项值
    """
    print(f"{question}")
    
    for i, (value, desc) in enumerate(choices, 1):
        default_mark = " (默认)" if value == default else ""
        print(f"{i}. {desc}{default_mark}")
        
    default_index = next((i for i, (value, _) in enumerate(choices, 1) if value == default), None)
    default_prompt = f"(默认: {default_index})" if default_index else ""
    
    while True:
        response = input(f"请选择 (1-{len(choices)}) {default_prompt}: ").strip()
        
        if not response and default is not None:
            return default
            
        try:
            index = int(response)
            if 1 <= index <= len(choices):
                return choices[index - 1][0]
        except ValueError:
            pass
            
        print(f"请输入一个有效的数字 (1-{len(choices)})")


def prompt_input(question: str, default: Optional[str] = None) -> str:
    """
    提示用户输入文本
    
    参数:
        question: 问题
        default: 默认值
        
    返回:
        用户输入的文本
    """
    default_prompt = f" (默认: {default})" if default is not None else ""
    prompt = f"{question}{default_prompt}: "
    
    response = input(prompt).strip()
    
    if not response and default is not None:
        return default
        
    return response


def prompt_integer(question: str, default: Optional[int] = None, min_value: Optional[int] = None, 
                  max_value: Optional[int] = None) -> int:
    """
    提示用户输入整数
    
    参数:
        question: 问题
        default: 默认值
        min_value: 最小值
        max_value: 最大值
        
    返回:
        用户输入的整数
    """
    constraints = []
    if min_value is not None and max_value is not None:
        constraints.append(f"范围: {min_value}-{max_value}")
    elif min_value is not None:
        constraints.append(f"最小值: {min_value}")
    elif max_value is not None:
        constraints.append(f"最大值: {max_value}")
        
    constraints_str = f" ({', '.join(constraints)})" if constraints else ""
    default_prompt = f" (默认: {default})" if default is not None else ""
    prompt = f"{question}{constraints_str}{default_prompt}: "
    
    while True:
        response = input(prompt).strip()
        
        if not response and default is not None:
            return default
            
        try:
            value = int(response)
            if min_value is not None and value < min_value:
                print(f"请输入不小于 {min_value} 的整数")
                continue
            if max_value is not None and value > max_value:
                print(f"请输入不大于 {max_value} 的整数")
                continue
            return value
        except ValueError:
            print("请输入有效的整数")


def prompt_float(question: str, default: Optional[float] = None, min_value: Optional[float] = None, 
                max_value: Optional[float] = None) -> float:
    """
    提示用户输入浮点数
    
    参数:
        question: 问题
        default: 默认值
        min_value: 最小值
        max_value: 最大值
        
    返回:
        用户输入的浮点数
    """
    constraints = []
    if min_value is not None and max_value is not None:
        constraints.append(f"范围: {min_value}-{max_value}")
    elif min_value is not None:
        constraints.append(f"最小值: {min_value}")
    elif max_value is not None:
        constraints.append(f"最大值: {max_value}")
        
    constraints_str = f" ({', '.join(constraints)})" if constraints else ""
    default_prompt = f" (默认: {default})" if default is not None else ""
    prompt = f"{question}{constraints_str}{default_prompt}: "
    
    while True:
        response = input(prompt).strip()
        
        if not response and default is not None:
            return default
            
        try:
            value = float(response)
            if min_value is not None and value < min_value:
                print(f"请输入不小于 {min_value} 的数值")
                continue
            if max_value is not None and value > max_value:
                print(f"请输入不大于 {max_value} 的数值")
                continue
            return value
        except ValueError:
            print("请输入有效的数值")


class ConfigWizard:
    """配置向导类，用于引导用户交互式配置爬虫"""
    
    def __init__(self, default_config=None):
        """
        初始化配置向导
        
        参数:
            default_config: 默认配置字典
        """
        self.default_config = default_config or {}
        
    def run(self):
        """
        运行配置向导
        
        返回:
            用户配置的字典
        """
        print("\n" + "=" * 60)
        print("黑神话悟空游戏攻略爬虫配置向导")
        print("=" * 60)
        print("请回答以下问题来配置爬虫。按Enter键使用默认值。")
        
        config = {}
        
        # 配置模式选择
        print("\n--- 配置模式 ---")
        config_mode = prompt_choice(
            "请选择配置模式",
            [
                ('basic', '基本配置（仅配置必要选项）'),
                ('advanced', '高级配置（配置所有选项）'),
                ('expert', '专家配置（包括实验性功能）')
            ],
            default='basic'
        )
        
        # 基本配置
        print("\n--- 基本配置 ---")
        config['start_url'] = prompt_input(
            "起始URL",
            default=self.default_config.get('start_url', 'https://www.gamersky.com/handbook/202408/1803231.shtml')
        )
        
        config['output_dir'] = prompt_input(
            "输出目录",
            default=self.default_config.get('output_dir', 'output')
        )
        
        config['output_file'] = prompt_input(
            "输出文件名",
            default=self.default_config.get('output_file', 'guide.md')
        )
        
        # 图片配置
        print("\n--- 图片配置 ---")
        config['download_images'] = prompt_yes_no(
            "是否下载图片",
            default=self.default_config.get('download_images', True)
        )
        
        if config['download_images']:
            default_image_dir = self.default_config.get('image_dir')
            if not default_image_dir:
                default_image_dir = os.path.join(config['output_dir'], 'images')
                
            config['image_dir'] = prompt_input(
                "图片保存目录",
                default=default_image_dir
            )
            
            config['image_delay'] = prompt_float(
                "图片下载间隔时间（秒）",
                default=self.default_config.get('image_delay', 0.5),
                min_value=0.1
            )
            
            if config_mode in ['advanced', 'expert']:
                config['image_quality'] = prompt_choice(
                    "图片质量",
                    [
                        ('original', '原始质量（保持原图）'),
                        ('high', '高质量（轻微压缩）'),
                        ('medium', '中等质量（中度压缩）'),
                        ('low', '低质量（高度压缩，节省空间）')
                    ],
                    default=self.default_config.get('image_quality', 'original')
                )
                
                config['skip_existing_images'] = prompt_yes_no(
                    "是否跳过已存在的图片（避免重复下载）",
                    default=self.default_config.get('skip_existing_images', True)
                )
        
        # 爬虫配置
        print("\n--- 爬虫配置 ---")
        config['delay'] = prompt_float(
            "页面请求间隔时间（秒）",
            default=self.default_config.get('delay', 1.0),
            min_value=0.5
        )
        
        config['max_retries'] = prompt_integer(
            "请求失败时的最大重试次数",
            default=self.default_config.get('max_retries', 3),
            min_value=0
        )
        
        config['retry_delay'] = prompt_float(
            "请求失败后的重试间隔时间（秒）",
            default=self.default_config.get('retry_delay', 2.0),
            min_value=0.5
        )
        
        config['timeout'] = prompt_integer(
            "请求超时时间（秒）",
            default=self.default_config.get('timeout', 30),
            min_value=5
        )
        
        config['user_agent'] = prompt_input(
            "HTTP请求的User-Agent",
            default=self.default_config.get('user_agent', 
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        )
        
        config['continue_on_error'] = prompt_yes_no(
            "遇到错误时是否继续抓取",
            default=self.default_config.get('continue_on_error', True)
        )
        
        if config_mode in ['advanced', 'expert']:
            config['max_pages'] = prompt_integer(
                "最大抓取页面数（0表示不限制）",
                default=self.default_config.get('max_pages', 0),
                min_value=0
            )
            
            config['start_page'] = prompt_integer(
                "开始抓取的页码（用于断点续传）",
                default=self.default_config.get('start_page', 1),
                min_value=1
            )
            
            if config_mode == 'expert':
                cookies_question = prompt_yes_no(
                    "是否设置Cookie（用于需要登录的网站）",
                    default=bool(self.default_config.get('cookies'))
                )
                
                if cookies_question:
                    config['cookies'] = prompt_input(
                        "Cookie字符串",
                        default=self.default_config.get('cookies', '')
                    )
                else:
                    config['cookies'] = None
                    
                headers_question = prompt_yes_no(
                    "是否设置额外的HTTP请求头",
                    default=bool(self.default_config.get('headers'))
                )
                
                if headers_question:
                    headers_str = prompt_input(
                        "HTTP请求头（JSON格式）",
                        default=json.dumps(self.default_config.get('headers', {}))
                    )
                    try:
                        config['headers'] = json.loads(headers_str)
                    except json.JSONDecodeError:
                        print("警告: HTTP请求头不是有效的JSON格式，将使用空字典")
                        config['headers'] = {}
                else:
                    config['headers'] = {}
        
        # 输出配置
        print("\n--- 输出配置 ---")
        config['show_progress_bar'] = prompt_yes_no(
            "是否显示进度条",
            default=self.default_config.get('show_progress_bar', True)
        )
        
        log_file_question = prompt_yes_no(
            "是否将日志保存到文件",
            default=bool(self.default_config.get('log_file'))
        )
        
        if log_file_question:
            config['log_file'] = prompt_input(
                "日志文件路径",
                default=self.default_config.get('log_file', 'crawler.log')
            )
            
            if config_mode in ['advanced', 'expert']:
                config['log_level'] = prompt_choice(
                    "日志级别",
                    [
                        ('DEBUG', 'DEBUG - 详细调试信息'),
                        ('INFO', 'INFO - 一般信息'),
                        ('WARNING', 'WARNING - 警告信息'),
                        ('ERROR', 'ERROR - 错误信息'),
                        ('CRITICAL', 'CRITICAL - 严重错误信息')
                    ],
                    default=self.default_config.get('log_level', 'INFO')
                )
        else:
            config['log_file'] = None
            
        if config_mode in ['advanced', 'expert']:
            config['quiet'] = prompt_yes_no(
                "是否启用安静模式（只输出错误信息）",
                default=self.default_config.get('quiet', False)
            )
            
            if not config['quiet']:
                config['verbose'] = prompt_yes_no(
                    "是否启用详细模式（输出更多调试信息）",
                    default=self.default_config.get('verbose', False)
                )
            else:
                config['verbose'] = False
                
            config['output_format'] = prompt_choice(
                "输出格式",
                [
                    ('markdown', 'Markdown - 适合大多数Markdown查看器'),
                    ('html', 'HTML - 适合在浏览器中查看'),
                    ('text', '纯文本 - 适合在任何文本编辑器中查看')
                ],
                default=self.default_config.get('output_format', 'markdown')
            )
            
        # 内容过滤配置（仅高级和专家模式）
        if config_mode in ['advanced', 'expert']:
            print("\n--- 内容过滤配置 ---")
            
            include_keywords_question = prompt_yes_no(
                "是否设置包含关键词（只抓取包含特定关键词的内容）",
                default=bool(self.default_config.get('include_keywords'))
            )
            
            if include_keywords_question:
                config['include_keywords'] = prompt_input(
                    "包含关键词（多个关键词用逗号分隔）",
                    default=self.default_config.get('include_keywords', '')
                )
            else:
                config['include_keywords'] = None
                
            exclude_keywords_question = prompt_yes_no(
                "是否设置排除关键词（排除包含特定关键词的内容）",
                default=bool(self.default_config.get('exclude_keywords'))
            )
            
            if exclude_keywords_question:
                config['exclude_keywords'] = prompt_input(
                    "排除关键词（多个关键词用逗号分隔）",
                    default=self.default_config.get('exclude_keywords', '')
                )
            else:
                config['exclude_keywords'] = None
                
            config['min_content_length'] = prompt_integer(
                "最小内容长度（小于此长度的页面将被忽略，0表示不限制）",
                default=self.default_config.get('min_content_length', 0),
                min_value=0
            )
            
            config['remove_ads'] = prompt_yes_no(
                "是否移除广告内容",
                default=self.default_config.get('remove_ads', True)
            )
            
        # 其他配置（仅专家模式）
        if config_mode == 'expert':
            print("\n--- 其他配置 ---")
            
            config['interactive'] = prompt_yes_no(
                "是否启用交互式模式（允许用户在运行过程中控制爬虫）",
                default=self.default_config.get('interactive', True)
            )
            
            config['preview'] = prompt_yes_no(
                "是否启用预览模式（只抓取前几页进行预览）",
                default=self.default_config.get('preview', False)
            )
            
            if config['preview']:
                config['preview_pages'] = prompt_integer(
                    "预览模式下抓取的页面数",
                    default=self.default_config.get('preview_pages', 3),
                    min_value=1
                )
                
            config['dry_run'] = prompt_yes_no(
                "是否启用空运行模式（不实际抓取内容，只显示将要执行的操作）",
                default=self.default_config.get('dry_run', False)
            )
            
        # 确认配置
        print("\n" + "=" * 60)
        print("配置摘要:")
        print("=" * 60)
        print(f"起始URL: {config['start_url']}")
        print(f"输出目录: {config['output_dir']}")
        print(f"输出文件: {config['output_file']}")
        print(f"是否下载图片: {'是' if config['download_images'] else '否'}")
        if config['download_images']:
            print(f"图片保存目录: {config['image_dir']}")
            print(f"图片下载间隔: {config['image_delay']}秒")
            if config_mode in ['advanced', 'expert']:
                print(f"图片质量: {config['image_quality']}")
                print(f"跳过已存在的图片: {'是' if config.get('skip_existing_images', True) else '否'}")
        print(f"页面请求间隔: {config['delay']}秒")
        print(f"最大重试次数: {config['max_retries']}")
        print(f"重试间隔时间: {config['retry_delay']}秒")
        print(f"请求超时时间: {config['timeout']}秒")
        print(f"遇到错误时继续: {'是' if config['continue_on_error'] else '否'}")
        
        if config_mode in ['advanced', 'expert']:
            print(f"最大抓取页面数: {config.get('max_pages', 0)} {'(不限制)' if config.get('max_pages', 0) == 0 else ''}")
            print(f"开始抓取的页码: {config.get('start_page', 1)}")
            
            if config_mode == 'expert' and config.get('cookies'):
                print(f"已设置Cookie: {'是' if config.get('cookies') else '否'}")
                
            if config_mode == 'expert' and config.get('headers'):
                print(f"已设置额外的HTTP请求头: {'是' if config.get('headers') else '否'}")
        
        print(f"显示进度条: {'是' if config['show_progress_bar'] else '否'}")
        print(f"日志文件: {config['log_file'] or '不保存'}")
        
        if config_mode in ['advanced', 'expert']:
            if config['log_file']:
                print(f"日志级别: {config.get('log_level', 'INFO')}")
                
            print(f"安静模式: {'是' if config.get('quiet', False) else '否'}")
            print(f"详细模式: {'是' if config.get('verbose', False) else '否'}")
            print(f"输出格式: {config.get('output_format', 'markdown')}")
            
            print(f"包含关键词: {config.get('include_keywords') or '无'}")
            print(f"排除关键词: {config.get('exclude_keywords') or '无'}")
            print(f"最小内容长度: {config.get('min_content_length', 0)} {'(不限制)' if config.get('min_content_length', 0) == 0 else ''}")
            print(f"移除广告内容: {'是' if config.get('remove_ads', True) else '否'}")
            
        if config_mode == 'expert':
            print(f"交互式模式: {'是' if config.get('interactive', True) else '否'}")
            print(f"预览模式: {'是' if config.get('preview', False) else '否'}")
            if config.get('preview', False):
                print(f"预览页面数: {config.get('preview_pages', 3)}")
            print(f"空运行模式: {'是' if config.get('dry_run', False) else '否'}")
            
        print("=" * 60)
        
        if not prompt_yes_no("确认使用以上配置?", default=True):
            print("配置已取消。")
            return None
            
        return config
        
    def save_config(self, config: Dict[str, Any], file_path: str) -> bool:
        """
        保存配置到文件
        
        参数:
            config: 配置字典
            file_path: 文件路径
            
        返回:
            是否成功保存
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # 根据文件扩展名选择格式
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.yaml' or ext == '.yml':
                try:
                    import yaml
                    with open(file_path, 'w', encoding='utf-8') as f:
                        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                except ImportError:
                    print("警告: 未安装PyYAML库，将使用JSON格式保存")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=4)
            elif ext == '.toml':
                try:
                    import toml
                    with open(file_path, 'w', encoding='utf-8') as f:
                        toml.dump(config, f)
                except ImportError:
                    print("警告: 未安装toml库，将使用JSON格式保存")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=4)
            else:
                # 默认使用JSON格式
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=4)
                
            print(f"配置已保存到: {file_path}")
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False