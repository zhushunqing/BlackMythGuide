# 黑神话悟空攻略爬虫开发记录

## 项目概述

本项目是一个专门用于抓取游民星空网站《黑神话悟空》攻略内容的爬虫工具，能够自动下载高清图片、过滤无效内容、生成结构化的Markdown攻略文档。

**开发时间**: 2025年7月18日  
**目标网站**: https://www.gamersky.com/handbook/202409/1815206.shtml  
**输出目录**: Guide_C/

## 开发历程

### 阶段1: 图片下载优化

#### 问题描述
- 原始爬虫下载的是缩略图（带`_S`后缀），而不是高清原图
- 需要修改图片URL提取逻辑，获取高清版本

#### 解决方案
修改 `game_guide_scraper/parser/parser.py` 中的 `_extract_image_info` 方法：

```python
# 处理游民星空的高清原图URL
# 游民星空的缩略图URL格式：image001_S.jpg
# 高清原图URL格式：image001.jpg
if 'gamersky.com' in img_url and '_S.jpg' in img_url:
    img_url = img_url.replace('_S.jpg', '.jpg')
elif 'gamersky.com' in img_url and '_S.png' in img_url:
    img_url = img_url.replace('_S.png', '.png')
```

#### 测试结果
- ✅ 成功下载1920x1080高清图片
- ✅ 图片质量显著提升

### 阶段2: 预览模式实现

#### 问题描述
- 预览模式参数存在但没有实际功能
- 需要限制抓取页面数量进行测试

#### 解决方案
修改 `game_guide_scraper/controller/controller.py`：

```python
# 检查预览模式限制
if self.config.get('preview', False):
    preview_pages = self.config.get('preview_pages', 3)
    if total_pages_processed >= preview_pages:
        self.report_progress(f"预览模式：已抓取 {preview_pages} 页，停止抓取")
        break
```

#### 测试结果
- ✅ 成功限制抓取页面数量
- ✅ 预览模式正常工作

### 阶段3: 内容过滤优化

#### 问题描述
抓取的内容包含大量无效信息：
- "更多相关内容请关注：黑神话：悟空专区"
- "责任编辑：瑞破受气包"
- "友情提示：支持键盘左右键"← →"翻页"
- "本文是否解决了您的问题"
- 长页码导航列表

#### 解决方案
在 `game_guide_scraper/parser/parser.py` 中添加智能过滤：

```python
# 定义需要过滤的文本内容关键词
self.filter_keywords = [
    '更多相关内容请关注',
    '责任编辑',
    '友情提示：支持键盘',
    '翻页',
    '本文是否解决了您的问题',
    '已解决',
    '未解决',
    '文章内容导航',
    '上一页',
    '下一页'
]

def _should_filter_text(self, text: str) -> bool:
    # 检查是否包含过滤关键词
    for keyword in self.filter_keywords:
        if keyword in text:
            return True
    
    # 检查是否是单独的页面标题（保留）
    single_page_pattern = r'^第\d+页：[^第]*$'
    if re.match(single_page_pattern, text.strip()):
        return False
    
    # 检查是否是包含多个页码的长列表（过滤）
    page_matches = re.findall(r'第\d+页：', text)
    if len(page_matches) > 1:
        return True
    
    return False
```

#### 测试结果
- ✅ 成功过滤无效内容
- ✅ 保留有用的页面标题
- ✅ 生成干净的攻略文档

### 阶段4: 图片去重功能

#### 问题描述
- 重复运行爬虫会重复下载已存在的图片
- 需要跳过已存在的文件，提高效率

#### 解决方案
修改 `game_guide_scraper/downloader/downloader.py`：

```python
def download_image(self, url, filename=None, skip_existing=True):
    # 检查文件是否已存在
    if skip_existing and os.path.exists(local_path):
        print(f"图片已存在，跳过下载: {local_path}")
        return local_path
    
    # 继续下载逻辑...

def download_all_images(self, image_list, skip_existing=True):
    # 优化输出信息，显示跳过、新下载、失败的统计
    print(f"图片处理完成。总计: {total_images}, 新下载: {downloaded_count}, 跳过: {skipped_count}, 失败: {failed_count}")
```

#### 命令行参数支持
- `--skip-existing-images`: 跳过已存在的图片（默认）
- `--force-download-images`: 强制重新下载所有图片

#### 测试结果
- ✅ 智能跳过已存在文件
- ✅ 只下载缺失的图片
- ✅ 详细的下载统计信息

### 阶段5: 页面标题目录生成

#### 问题描述
- 需要根据页面标题生成目录和锚点
- 格式："第1页：小妖-第一回-狼斥候"

#### 解决方案

**1. 修改内容组织器** (`game_guide_scraper/organizer/organizer.py`)：

```python
def _extract_page_titles(self) -> List[Dict[str, Any]]:
    """从页面内容中提取页面标题"""
    page_titles = []
    
    for page in self.pages:
        content = page.get('content', [])
        for item in content:
            if item.get('type') == 'text':
                text = item.get('value', '')
                # 匹配"第X页：标题"格式
                match = re.match(r'^第(\d+)页：(.+)$', text.strip())
                if match:
                    page_num = int(match.group(1))
                    title = match.group(2).strip()
                    
                    page_titles.append({
                        'page_number': page_num,
                        'title': title,
                        'full_title': text.strip(),
                        'id': self._generate_id(f"page-{page_num}-{title}"),
                        'url': page.get('url', '')
                    })
                    break
    
    return page_titles

def generate_page_based_toc(self, page_titles):
    """基于页面标题生成目录"""
    toc = []
    for page_info in page_titles:
        toc.append({
            'level': 1,
            'title': page_info['full_title'],
            'id': page_info['id'],
            'page_number': page_info['page_number']
        })
    return toc
```

**2. 修改Markdown生成器** (`game_guide_scraper/generator/markdown_generator.py`)：

```python
def generate_content_markdown_with_anchors(self, content_list, page_title_map):
    """生成带页面标题锚点的内容Markdown"""
    for item in content_list:
        if item_type == 'text':
            value = item.get('value', '')
            if value:
                # 检查是否是页面标题
                if value in page_title_map:
                    page_info = page_title_map[value]
                    # 为页面标题添加锚点
                    markdown.append(f"\n## {value} <a id=\"{page_info['id']}\"></a>\n")
                else:
                    markdown.append(f"{value}\n")
```

#### 测试结果
- ✅ 自动生成页面标题目录
- ✅ 正确的锚点链接
- ✅ 清晰的文档结构

### 阶段6: 默认标题清理

#### 问题描述
- 生成的目录包含不必要的默认文档标题
- 需要只保留页面标题的目录

#### 解决方案
修改Markdown生成器的目录生成逻辑：

```python
# 添加目录（只包含页面标题，不包含默认的文档标题）
if page_titles:
    markdown.append("## 目录\n")
    # 只生成页面标题的目录，跳过默认的文档标题
    page_toc = [item for item in toc if item.get('level', 0) > 0]
    markdown.append(self.generate_toc_markdown(page_toc))
    markdown.append("\n---\n")

# 如果有页面标题，则不显示默认的章节标题
if page_titles:
    # 直接添加章节内容，不添加章节标题
    chapter_content = chapter.get('content', [])
    markdown.append(self.generate_content_markdown_with_anchors(chapter_content, page_title_map))
```

#### 测试结果
- ✅ 清理了默认标题
- ✅ 只保留页面标题目录
- ✅ 文档结构更清晰

### 阶段7: Banner图片过滤

#### 问题描述
- 需要过滤掉特定的banner图片：banner923.jpg
- 这是广告图片，不属于攻略内容

#### 解决方案
修改图片过滤逻辑：

```python
# 过滤掉小图标、广告图片等
filter_keywords = ['icon', 'logo', 'banner', 'ad', 'advertisement']
filter_filenames = ['banner923.jpg']

# 检查URL中是否包含过滤关键词
if any(keyword in img_url.lower() for keyword in filter_keywords):
    return None
    
# 检查是否是特定的需要过滤的文件名
if any(filename in img_url.lower() for filename in filter_filenames):
    return None
```

#### 测试结果
- ✅ 成功过滤banner923.jpg
- ✅ 图片数量从14张减少到11张
- ✅ 生成更干净的攻略文档

## 最终功能特性

### 核心功能
1. **高清图片下载**: 自动获取高清原图而非缩略图
2. **智能内容过滤**: 过滤编辑信息、导航信息、广告内容
3. **图片去重**: 跳过已存在的图片文件，避免重复下载
4. **页面标题目录**: 自动生成基于页面标题的目录和锚点
5. **预览模式**: 支持限制抓取页面数量进行测试

### 技术特点
1. **模块化设计**: 分离爬虫、解析器、下载器、组织器、生成器
2. **配置灵活**: 支持命令行参数和配置文件
3. **错误处理**: 完善的异常处理和重试机制
4. **进度显示**: 实时显示抓取和下载进度
5. **交互控制**: 支持运行时暂停、继续、退出等操作

### 输出质量
1. **结构清晰**: 自动生成目录和锚点导航
2. **内容干净**: 过滤无效信息，只保留攻略内容
3. **图片高清**: 1920x1080高分辨率图片
4. **格式标准**: 标准Markdown格式，兼容性好

## 使用示例

### 基本用法
```bash
# 抓取前3页预览
python -m game_guide_scraper.main \
  --start-url "https://www.gamersky.com/handbook/202409/1815206.shtml" \
  --output-dir "Guide_C" \
  --output-file "guide.md" \
  --preview --preview-pages 3 \
  --image-dir "Guide_C/images"

# 抓取完整攻略
python -m game_guide_scraper.main \
  --start-url "https://www.gamersky.com/handbook/202409/1815206.shtml" \
  --output-dir "Guide_C" \
  --output-file "complete_guide.md" \
  --image-dir "Guide_C/images"

# 强制重新下载所有图片
python -m game_guide_scraper.main \
  --start-url "https://www.gamersky.com/handbook/202409/1815206.shtml" \
  --output-dir "Guide_C" \
  --force-download-images
```

### 配置选项
- `--preview --preview-pages N`: 预览模式，只抓取前N页
- `--skip-existing-images`: 跳过已存在的图片（默认）
- `--force-download-images`: 强制重新下载所有图片
- `--non-interactive`: 非交互模式，适用于自动化脚本

## 性能统计

### 测试数据（前3页）
- **处理页面数**: 3页
- **下载图片数**: 19张（过滤后11张有效图片）
- **运行时间**: 约2-3秒（跳过已存在图片时）
- **图片质量**: 1920x1080高清
- **文件大小**: 约2-5MB per image

### 过滤效果
- **过滤的无效文本**: 编辑信息、导航提示、页码列表等
- **过滤的无效图片**: banner、logo、广告图片
- **保留的有效内容**: 攻略文本、游戏截图、位置说明图

## 项目结构

```
game_guide_scraper/
├── __init__.py
├── main.py                 # 主程序入口
├── controller/
│   ├── __init__.py
│   └── controller.py       # 控制器，协调各组件
├── scraper/
│   ├── __init__.py
│   └── scraper.py         # 网页抓取器
├── parser/
│   ├── __init__.py
│   └── parser.py          # HTML解析器
├── downloader/
│   ├── __init__.py
│   └── downloader.py      # 图片下载器
├── organizer/
│   ├── __init__.py
│   └── organizer.py       # 内容组织器
├── generator/
│   ├── __init__.py
│   └── markdown_generator.py  # Markdown生成器
└── utils/
    ├── __init__.py
    └── cli.py             # 命令行工具

Guide_C/                   # 输出目录
├── images/               # 图片目录
│   ├── a468430156ac04ec89a7918b8601b49b.jpg
│   ├── 8e201266573fc2d75f7f52d428f41d2b.jpg
│   └── ...
└── guide.md             # 生成的攻略文档
```

## 开发总结

这次开发过程展现了一个完整的爬虫项目从基础功能到高级特性的演进过程：

1. **需求驱动**: 每个功能都是为了解决实际使用中的问题
2. **迭代优化**: 通过多次测试和改进，不断完善功能
3. **用户体验**: 注重输出质量和使用便利性
4. **技术深度**: 涉及网络爬虫、HTML解析、图像处理、文档生成等多个技术领域

最终产品是一个功能完善、易于使用的专业级攻略抓取工具，能够生成高质量的游戏攻略文档。

## 后续改进建议

1. **多线程下载**: 支持并发下载图片，提高效率
2. **断点续传**: 支持中断后继续抓取
3. **多格式输出**: 支持PDF、HTML等多种输出格式
4. **网站适配**: 扩展支持更多游戏攻略网站
5. **内容分析**: 添加内容质量分析和自动分类功能