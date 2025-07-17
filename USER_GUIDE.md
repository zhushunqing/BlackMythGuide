# 黑神话悟空游戏攻略爬虫 - 使用说明

## 简介

黑神话悟空游戏攻略爬虫是一个专门用于抓取游戏"黑神话悟空"攻略内容的工具。它可以从指定的起始URL开始，自动抓取所有相关页面内容，包括"下一页"链接指向的所有页面，并将内容整理成一本结构化的Markdown格式攻略书。

### 主要功能

- 🕷️ **智能网页抓取**：自动识别并跟随"下一页"链接
- 🖼️ **图片下载**：自动下载并保存攻略中的图片
- 📝 **Markdown生成**：将抓取的内容整理成结构化的Markdown文档
- ⚙️ **灵活配置**：支持多种配置选项和自定义设置
- 🎮 **交互式控制**：运行过程中可实时控制爬虫行为
- 📊 **进度监控**：实时显示抓取进度和统计信息

## 安装要求

### 系统要求
- Python 3.7 或更高版本
- 支持的操作系统：Windows、macOS、Linux

### 依赖库
```bash
pip install -r requirements.txt
```

主要依赖：
- `requests` - HTTP请求库
- `beautifulsoup4` - HTML解析库
- `lxml` - XML/HTML解析器

## 快速开始

### 1. 基本使用

最简单的使用方式，使用默认设置抓取攻略：

```bash
python -m game_guide_scraper.main
```

### 2. 指定URL和输出目录

```bash
python -m game_guide_scraper.main \
    --start-url "https://www.gamersky.com/handbook/202408/1803231.shtml" \
    --output-dir "my_guide" \
    --output-file "black_myth_guide.md"
```

### 3. 使用配置向导

如果你是第一次使用，推荐使用配置向导：

```bash
python -m game_guide_scraper.main --wizard
```

配置向导会引导你完成所有设置，包括：
- 起始URL设置
- 输出目录配置
- 图片下载选项
- 爬虫行为参数
- 日志和输出设置

## 详细使用指南

### 命令行参数

#### 基本参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--start-url` | 起始URL | `https://www.gamersky.com/handbook/202408/1803231.shtml` |
| `--output-dir` | 输出目录 | `output` |
| `--output-file` | 输出文件名 | `guide.md` |

#### 图片选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--download-images` | 下载图片 | `True` |
| `--no-images` | 不下载图片 | - |
| `--image-dir` | 图片保存目录 | `output/images` |
| `--image-delay` | 图片下载间隔（秒） | `0.5` |
| `--image-quality` | 图片质量 | `original` |
| `--skip-existing-images` | 跳过已存在的图片 | `True` |

#### 爬虫选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--delay` | 页面请求间隔（秒） | `1.0` |
| `--max-retries` | 最大重试次数 | `3` |
| `--retry-delay` | 重试间隔（秒） | `2.0` |
| `--timeout` | 请求超时时间（秒） | `30` |
| `--max-pages` | 最大抓取页面数 | `0`（不限制） |
| `--continue-on-error` | 遇到错误时继续 | `True` |

#### 输出选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--log-file` | 日志文件路径 | 无 |
| `--log-level` | 日志级别 | `INFO` |
| `--quiet` | 安静模式 | `False` |
| `--verbose` | 详细模式 | `False` |
| `--output-format` | 输出格式 | `markdown` |

### 配置文件使用

#### 生成配置文件模板

```bash
python -m game_guide_scraper.main --generate-config "my_config.json"
```

#### 使用配置文件

```bash
python -m game_guide_scraper.main --config "my_config.json"
```

#### 保存当前配置

```bash
python -m game_guide_scraper.main --save-config "my_config.json" --delay 2.0 --max-pages 50
```

### 交互式控制

运行爬虫时，你可以使用以下按键进行实时控制：

| 按键 | 功能 |
|------|------|
| `q` | 退出爬虫 |
| `p` | 暂停/恢复爬虫 |
| `c` | 继续（当爬虫暂停时） |
| `s` | 显示当前状态 |
| `i` | 显示当前页面信息 |
| `d` | 显示下载统计 |
| `o` | 打开输出目录 |
| `+` | 增加请求延迟（减慢速度） |
| `-` | 减少请求延迟（加快速度） |
| `l` | 显示最近的日志 |
| `h` | 显示帮助信息 |

## 使用示例

### 示例1：基本抓取

```bash
# 使用默认设置抓取攻略
python -m game_guide_scraper.main
```

### 示例2：自定义输出

```bash
# 指定输出目录和文件名
python -m game_guide_scraper.main \
    --output-dir "guides" \
    --output-file "black_myth_wukong_guide.md"
```

### 示例3：不下载图片

```bash
# 只抓取文本内容，不下载图片
python -m game_guide_scraper.main --no-images
```

### 示例4：调整爬虫速度

```bash
# 设置更长的延迟时间，减轻服务器负担
python -m game_guide_scraper.main --delay 3.0 --image-delay 1.0
```

### 示例5：限制抓取页面数

```bash
# 只抓取前20页进行测试
python -m game_guide_scraper.main --max-pages 20
```

### 示例6：预览模式

```bash
# 预览模式，只抓取前3页
python -m game_guide_scraper.main --preview --preview-pages 3
```

### 示例7：详细日志

```bash
# 启用详细日志并保存到文件
python -m game_guide_scraper.main \
    --verbose \
    --log-file "crawler.log" \
    --log-level DEBUG
```

### 示例8：断点续传

```bash
# 从第10页开始抓取（用于断点续传）
python -m game_guide_scraper.main --start-page 10
```

### 示例9：内容过滤

```bash
# 只抓取包含特定关键词的内容
python -m game_guide_scraper.main \
    --include-keywords "boss,攻略,技巧" \
    --exclude-keywords "广告,活动"
```

### 示例10：非交互式模式

```bash
# 适用于自动化脚本的非交互式模式
python -m game_guide_scraper.main --non-interactive --quiet
```

## 配置文件详解

### JSON配置文件示例

```json
{
    "start_url": "https://www.gamersky.com/handbook/202408/1803231.shtml",
    "output_dir": "output",
    "output_file": "guide.md",
    "download_images": true,
    "image_dir": "output/images",
    "image_delay": 0.5,
    "image_quality": "original",
    "delay": 1.0,
    "max_retries": 3,
    "timeout": 30,
    "max_pages": 0,
    "continue_on_error": true,
    "log_file": "crawler.log",
    "log_level": "INFO",
    "interactive": true
}
```

### 配置选项说明

#### 基本配置
- `start_url`: 爬虫开始抓取的URL
- `output_dir`: 输出文件保存目录
- `output_file`: 生成的Markdown文件名

#### 图片配置
- `download_images`: 是否下载图片
- `image_dir`: 图片保存目录
- `image_delay`: 图片下载间隔时间
- `image_quality`: 图片质量（original/high/medium/low）
- `skip_existing_images`: 是否跳过已存在的图片

#### 爬虫配置
- `delay`: 页面请求间隔时间
- `max_retries`: 请求失败时的最大重试次数
- `retry_delay`: 重试间隔时间
- `timeout`: 请求超时时间
- `max_pages`: 最大抓取页面数（0表示不限制）
- `start_page`: 开始抓取的页码
- `continue_on_error`: 遇到错误时是否继续

#### 输出配置
- `log_file`: 日志文件路径
- `log_level`: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
- `quiet`: 安静模式
- `verbose`: 详细模式
- `output_format`: 输出格式（markdown/html/text）

#### 内容过滤配置
- `include_keywords`: 包含关键词（逗号分隔）
- `exclude_keywords`: 排除关键词（逗号分隔）
- `min_content_length`: 最小内容长度
- `remove_ads`: 是否移除广告内容

## 故障排除

### 常见问题

#### 1. 网络连接问题

**问题**：抓取失败，显示网络连接错误
**解决方案**：
- 检查网络连接
- 增加超时时间：`--timeout 60`
- 增加重试次数：`--max-retries 5`
- 增加请求延迟：`--delay 2.0`

#### 2. 图片下载失败

**问题**：部分图片下载失败
**解决方案**：
- 增加图片下载延迟：`--image-delay 1.0`
- 检查图片URL是否有效
- 使用`--force-download-images`强制重新下载

#### 3. 内存使用过高

**问题**：处理大量页面时内存占用过高
**解决方案**：
- 限制最大页面数：`--max-pages 100`
- 不下载图片：`--no-images`
- 分批处理，使用断点续传

#### 4. 中文编码问题

**问题**：生成的文件中中文显示乱码
**解决方案**：
- 确保系统支持UTF-8编码
- 使用支持UTF-8的文本编辑器打开文件

#### 5. 权限问题

**问题**：无法创建输出目录或写入文件
**解决方案**：
- 检查目录权限
- 使用管理员权限运行
- 更改输出目录到有写入权限的位置

### 调试技巧

#### 启用详细日志

```bash
python -m game_guide_scraper.main \
    --verbose \
    --log-file "debug.log" \
    --log-level DEBUG
```

#### 使用预览模式测试

```bash
python -m game_guide_scraper.main \
    --preview \
    --preview-pages 2 \
    --verbose
```

#### 检查特定URL

```bash
python -m game_guide_scraper.main \
    --check-url "https://www.gamersky.com/handbook/202408/1803231.shtml"
```

## 最佳实践

### 1. 礼貌爬取

- 设置合理的请求延迟（建议1-2秒）
- 不要并发过多请求
- 遵守网站的robots.txt规则
- 避免在高峰时段进行大量抓取

```bash
python -m game_guide_scraper.main --delay 2.0 --image-delay 1.0
```

### 2. 数据备份

- 定期保存配置文件
- 备份已下载的内容
- 使用版本控制管理配置

```bash
# 保存当前配置
python -m game_guide_scraper.main --save-config "backup_config.json"
```

### 3. 分批处理

对于大型攻略，建议分批处理：

```bash
# 第一批：1-50页
python -m game_guide_scraper.main --max-pages 50 --output-file "guide_part1.md"

# 第二批：51-100页
python -m game_guide_scraper.main --start-page 51 --max-pages 50 --output-file "guide_part2.md"
```

### 4. 监控和日志

```bash
python -m game_guide_scraper.main \
    --log-file "crawler_$(date +%Y%m%d_%H%M%S).log" \
    --log-level INFO \
    --verbose
```

### 5. 自动化脚本

创建自动化脚本进行定期抓取：

```bash
#!/bin/bash
# auto_crawl.sh

DATE=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="guides/$DATE"

python -m game_guide_scraper.main \
    --output-dir "$OUTPUT_DIR" \
    --log-file "$OUTPUT_DIR/crawler.log" \
    --non-interactive \
    --continue-on-error
```

## 输出文件说明

### 目录结构

```
output/
├── guide.md              # 主攻略文件
├── images/               # 图片目录
│   ├── image1.jpg
│   ├── image2.png
│   └── ...
└── crawler.log          # 日志文件（如果启用）
```

### Markdown文件格式

生成的Markdown文件包含：

1. **文档标题**：攻略名称
2. **来源信息**：原始URL链接
3. **目录**：自动生成的章节目录
4. **内容章节**：按页面组织的攻略内容
5. **图片引用**：本地图片的相对路径引用

### 示例输出

```markdown
# 黑神话悟空游戏攻略

*来源: [https://www.gamersky.com/handbook/202408/1803231.shtml](https://www.gamersky.com/handbook/202408/1803231.shtml)*

## 目录

- [第一章：游戏介绍](#第一章游戏介绍)
- [第二章：基础操作](#第二章基础操作)
- [第三章：战斗系统](#第三章战斗系统)

---

## 第一章：游戏介绍

游戏内容介绍...

![游戏截图](images/screenshot1.jpg)

## 第二章：基础操作

操作说明...
```

## 版本信息

- **当前版本**：v1.0.0
- **Python要求**：3.7+
- **最后更新**：2024年12月

## 许可证

本项目仅供学习和个人使用。请遵守相关网站的使用条款和版权规定。

## 支持和反馈

如果你在使用过程中遇到问题或有改进建议，请：

1. 检查本文档的故障排除部分
2. 查看日志文件获取详细错误信息
3. 使用`--verbose`模式获取更多调试信息

---

**注意**：请合理使用本工具，遵守网站的使用条款，避免对目标网站造成过大负担。