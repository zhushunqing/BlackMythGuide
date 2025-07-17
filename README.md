# 黑神话悟空游戏攻略爬虫

一个专门用于抓取"黑神话悟空"游戏攻略的Python爬虫工具，能够从指定网站抓取完整的攻略内容，包括文本和图片，并生成结构化的Markdown格式攻略书。

## 功能特性

- 🚀 **智能抓取**: 自动识别并跟随"下一页"链接，抓取完整攻略内容
- 📖 **结构化输出**: 生成格式良好的Markdown攻略书，包含目录和章节结构
- 🖼️ **图片下载**: 自动下载并保存攻略中的所有图片
- ⚡ **交互式控制**: 运行过程中可实时控制爬虫行为
- 📊 **进度监控**: 实时显示抓取进度和统计信息
- 🛠️ **灵活配置**: 支持命令行参数和配置文件多种配置方式
- 🔄 **断点续传**: 支持从指定页面开始抓取
- 🎯 **内容过滤**: 支持关键词过滤和内容长度限制

## 安装要求

### Python版本
- Python 3.7 或更高版本

### 依赖包
```bash
pip install -r requirements.txt
```

主要依赖：
- `requests` - HTTP请求库
- `beautifulsoup4` - HTML解析库
- `lxml` - XML/HTML解析器

## 快速开始

### 1. 基本使用

使用默认设置抓取攻略：
```bash
python -m game_guide_scraper.main
```

### 2. 指定输出目录

```bash
python -m game_guide_scraper.main --output-dir "my_guide" --output-file "wukong_guide.md"
```

### 3. 不下载图片（仅文本）

```bash
python -m game_guide_scraper.main --no-images
```

### 4. 使用配置向导

```bash
python -m game_guide_scraper.main --wizard
```

## 详细使用说明

### 命令行参数

#### 基本参数
- `--start-url URL`: 起始URL（默认：黑神话悟空攻略首页）
- `--output-dir DIR`: 输出目录（默认：output）
- `--output-file FILE`: 输出文件名（默认：guide.md）

#### 图片选项
- `--download-images`: 下载图片（默认启用）
- `--no-images`: 不下载图片
- `--image-dir DIR`: 图片保存目录
- `--image-delay SECONDS`: 图片下载间隔时间
- `--image-quality QUALITY`: 图片质量（original/high/medium/low）
- `--skip-existing-images`: 跳过已存在的图片
- `--force-download-images`: 强制重新下载所有图片

#### 爬虫行为控制
- `--delay SECONDS`: 页面请求间隔时间（默认：1.0秒）
- `--max-retries NUM`: 最大重试次数（默认：3）
- `--retry-delay SECONDS`: 重试间隔时间（默认：2.0秒）
- `--timeout SECONDS`: 请求超时时间（默认：30秒）
- `--max-pages NUM`: 最大抓取页面数（0=不限制）
- `--start-page NUM`: 开始抓取的页码（用于断点续传）
- `--continue-on-error`: 遇到错误时继续抓取
- `--stop-on-error`: 遇到错误时停止抓取

#### 输出和日志
- `--log-file FILE`: 日志文件路径
- `--log-level LEVEL`: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
- `--quiet`: 安静模式，只输出错误信息
- `--verbose`: 详细模式，输出更多调试信息
- `--show-progress-bar`: 显示进度条（默认启用）
- `--no-progress-bar`: 不显示进度条

#### 内容过滤
- `--include-keywords KEYWORDS`: 包含关键词过滤（逗号分隔）
- `--exclude-keywords KEYWORDS`: 排除关键词过滤（逗号分隔）
- `--min-content-length LENGTH`: 最小内容长度限制
- `--remove-ads`: 移除广告内容（默认启用）
- `--keep-ads`: 保留广告内容

#### 配置文件
- `--config FILE`: 使用配置文件
- `--generate-config FILE`: 生成配置文件模板
- `--save-config FILE`: 保存当前配置到文件
- `--wizard`: 启动配置向导

#### 其他选项
- `--version`: 显示版本信息
- `--examples`: 显示使用示例
- `--preview`: 预览模式，只抓取前几页
- `--preview-pages NUM`: 预览页面数
- `--dry-run`: 空运行模式，不实际抓取
- `--interactive`: 交互式模式（默认启用）
- `--non-interactive`: 非交互式模式

### 交互式控制

在爬虫运行过程中，可以使用以下按键进行实时控制：

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

### 配置文件使用

#### 生成配置文件模板
```bash
python -m game_guide_scraper.main --generate-config config.json
```

#### 使用配置文件
```bash
python -m game_guide_scraper.main --config config.json
```

#### 配置文件示例
```json
{
    "start_url": "https://www.gamersky.com/handbook/202408/1803231.shtml",
    "output_dir": "output",
    "output_file": "guide.md",
    "download_images": true,
    "image_dir": "output/images",
    "delay": 1.0,
    "max_retries": 3,
    "timeout": 30,
    "show_progress_bar": true,
    "log_file": "crawler.log",
    "interactive": true
}
```

## 使用示例

### 基本抓取
```bash
# 使用默认设置抓取完整攻略
python -m game_guide_scraper.main

# 指定输出目录和文件名
python -m game_guide_scraper.main --output-dir "wukong_guide" --output-file "complete_guide.md"
```

### 图片处理
```bash
# 不下载图片，仅抓取文本
python -m game_guide_scraper.main --no-images

# 设置图片质量和下载间隔
python -m game_guide_scraper.main --image-quality medium --image-delay 1.0

# 强制重新下载所有图片
python -m game_guide_scraper.main --force-download-images
```

### 爬虫行为控制
```bash
# 调整爬虫速度和重试设置
python -m game_guide_scraper.main --delay 2.0 --max-retries 5 --timeout 60

# 限制抓取页面数
python -m game_guide_scraper.main --max-pages 10

# 从第5页开始抓取（断点续传）
python -m game_guide_scraper.main --start-page 5
```

### 内容过滤
```bash
# 只抓取包含特定关键词的内容
python -m game_guide_scraper.main --include-keywords "boss,技巧,攻略"

# 排除包含特定关键词的内容
python -m game_guide_scraper.main --exclude-keywords "广告,活动"

# 设置最小内容长度
python -m game_guide_scraper.main --min-content-length 100
```

### 日志和调试
```bash
# 保存详细日志
python -m game_guide_scraper.main --log-file "debug.log" --log-level DEBUG

# 安静模式运行
python -m game_guide_scraper.main --quiet

# 详细输出模式
python -m game_guide_scraper.main --verbose
```

### 预览和测试
```bash
# 预览模式，只抓取前3页
python -m game_guide_scraper.main --preview --preview-pages 3

# 空运行模式，查看将要执行的操作
python -m game_guide_scraper.main --dry-run

# 非交互式模式，适用于脚本自动化
python -m game_guide_scraper.main --non-interactive
```

## 输出文件结构

抓取完成后，会在指定的输出目录中生成以下文件：

```
output/
├── guide.md          # 主攻略文件
├── images/           # 图片目录
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
└── crawler.log       # 日志文件（如果启用）
```

### Markdown文件结构
生成的Markdown文件包含：
- 文档标题和来源信息
- 自动生成的目录
- 按页面组织的章节内容
- 嵌入的图片引用
- 保持原始格式的文本内容

## 故障排除

### 常见问题

#### 1. 网络连接问题
```bash
# 增加超时时间和重试次数
python -m game_guide_scraper.main --timeout 60 --max-retries 5 --retry-delay 3.0
```

#### 2. 图片下载失败
```bash
# 增加图片下载间隔
python -m game_guide_scraper.main --image-delay 2.0

# 跳过图片下载
python -m game_guide_scraper.main --no-images
```

#### 3. 内存使用过多
```bash
# 限制抓取页面数
python -m game_guide_scraper.main --max-pages 50

# 不下载图片以节省内存
python -m game_guide_scraper.main --no-images
```

#### 4. 被网站限制访问
```bash
# 增加请求间隔
python -m game_guide_scraper.main --delay 3.0

# 使用自定义User-Agent
python -m game_guide_scraper.main --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

### 错误代码说明

- **退出码 0**: 成功完成
- **退出码 1**: 一般错误
- **退出码 130**: 用户中断（Ctrl+C）

### 日志分析

启用日志文件后，可以查看详细的运行信息：
```bash
# 查看日志文件
tail -f crawler.log

# 查看错误信息
grep "ERROR" crawler.log
```

## 高级用法

### 自定义HTTP请求头
```bash
python -m game_guide_scraper.main --headers '{"Referer": "https://www.gamersky.com/"}'
```

### 使用Cookie
```bash
python -m game_guide_scraper.main --cookies "session_id=abc123; user_pref=zh-cn"
```

### 批量处理脚本
```bash
#!/bin/bash
# 批量抓取不同章节
python -m game_guide_scraper.main --start-page 1 --max-pages 20 --output-file "chapter1.md"
python -m game_guide_scraper.main --start-page 21 --max-pages 20 --output-file "chapter2.md"
python -m game_guide_scraper.main --start-page 41 --max-pages 20 --output-file "chapter3.md"
```

## 开发和贡献

### 项目结构
```
game_guide_scraper/
├── __init__.py
├── main.py              # 主程序入口
├── controller/          # 主控制器
├── scraper/            # 网页抓取器
├── parser/             # 内容解析器
├── downloader/         # 图片下载器
├── organizer/          # 内容组织器
├── generator/          # Markdown生成器
├── utils/              # 工具模块
└── tests/              # 测试文件
```

### 运行测试
```bash
python -m pytest game_guide_scraper/tests/
```

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 免责声明

本工具仅供学习和研究使用。使用时请遵守目标网站的robots.txt和使用条款，不要对网站造成过大负担。用户需自行承担使用本工具的风险和责任。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持完整攻略抓取
- 实现交互式控制
- 支持图片下载
- 提供配置向导

---

如有问题或建议，请提交Issue或Pull Request。