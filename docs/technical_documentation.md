# 黑神话悟空攻略爬虫技术文档

## 架构设计

### 整体架构
本项目采用模块化设计，将爬虫功能分解为多个独立的组件：

```
Controller (控制器)
    ├── Scraper (网页抓取器)
    ├── Parser (HTML解析器)
    ├── ImageDownloader (图片下载器)
    ├── ContentOrganizer (内容组织器)
    └── MarkdownGenerator (文档生成器)
```

### 数据流
```
URL → Scraper → HTML → Parser → Content → Organizer → Document → Generator → Markdown
                  ↓
              ImageDownloader → Local Images
```

## 核心组件详解

### 1. Scraper (网页抓取器)

**文件**: `game_guide_scraper/scraper/scraper.py`

**主要功能**:
- HTTP请求处理
- 页面内容获取
- 下一页链接提取
- 错误重试机制

**关键方法**:
```python
def fetch_page(self, url: str) -> Optional[str]:
    """获取页面HTML内容"""
    
def get_next_page_url(self, html: str, current_url: str) -> Optional[str]:
    """提取下一页链接"""
```

**技术特点**:
- 支持自定义User-Agent
- 请求间隔控制
- 自动重试机制
- 超时处理

### 2. Parser (HTML解析器)

**文件**: `game_guide_scraper/parser/parser.py`

**主要功能**:
- HTML内容解析
- 文本和图片提取
- 内容过滤
- 结构化数据生成

**关键方法**:
```python
def parse_content(self, html: str) -> Optional[Dict[str, Any]]:
    """解析HTML内容，提取标题、正文、图片URL等"""
    
def _extract_image_info(self, img_tag) -> Optional[Dict[str, Any]]:
    """从img标签中提取图片信息"""
    
def _should_filter_text(self, text: str) -> bool:
    """判断文本是否应该被过滤掉"""
```

**过滤规则**:
```python
# 文本过滤关键词
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

# 图片过滤
filter_keywords = ['icon', 'logo', 'banner', 'ad', 'advertisement']
filter_filenames = ['banner923.jpg']
```

**高清图片处理**:
```python
# 游民星空高清原图URL转换
if 'gamersky.com' in img_url and '_S.jpg' in img_url:
    img_url = img_url.replace('_S.jpg', '.jpg')
elif 'gamersky.com' in img_url and '_S.png' in img_url:
    img_url = img_url.replace('_S.png', '.png')
```

### 3. ImageDownloader (图片下载器)

**文件**: `game_guide_scraper/downloader/downloader.py`

**主要功能**:
- 图片下载
- 文件去重
- 下载统计
- 错误处理

**关键方法**:
```python
def download_image(self, url, filename=None, skip_existing=True):
    """下载单张图片"""
    
def download_all_images(self, image_list, skip_existing=True):
    """批量下载图片"""
```

**去重机制**:
```python
# 检查文件是否已存在
if skip_existing and os.path.exists(local_path):
    print(f"图片已存在，跳过下载: {local_path}")
    return local_path
```

**文件命名**:
```python
# 使用URL的MD5哈希值作为文件名
url_hash = hashlib.md5(url.encode()).hexdigest()
parsed_url = urlparse(url)
path = parsed_url.path
ext = os.path.splitext(path)[1] or '.jpg'
filename = f"{url_hash}{ext}"
```

### 4. ContentOrganizer (内容组织器)

**文件**: `game_guide_scraper/organizer/organizer.py`

**主要功能**:
- 页面内容整合
- 页面标题提取
- 目录结构生成
- 文档结构化

**页面标题提取**:
```python
def _extract_page_titles(self) -> List[Dict[str, Any]]:
    """从页面内容中提取页面标题"""
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
```

**目录生成**:
```python
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

### 5. MarkdownGenerator (文档生成器)

**文件**: `game_guide_scraper/generator/markdown_generator.py`

**主要功能**:
- Markdown文档生成
- 目录和锚点处理
- 图片链接处理
- 文档格式化

**锚点生成**:
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

**目录清理**:
```python
# 添加目录（只包含页面标题，不包含默认的文档标题）
if page_titles:
    markdown.append("## 目录\n")
    # 只生成页面标题的目录，跳过默认的文档标题
    page_toc = [item for item in toc if item.get('level', 0) > 0]
    markdown.append(self.generate_toc_markdown(page_toc))
    markdown.append("\n---\n")
```

### 6. Controller (控制器)

**文件**: `game_guide_scraper/controller/controller.py`

**主要功能**:
- 组件协调
- 流程控制
- 进度报告
- 配置管理

**预览模式控制**:
```python
# 检查预览模式限制
if self.config.get('preview', False):
    preview_pages = self.config.get('preview_pages', 3)
    if total_pages_processed >= preview_pages:
        self.report_progress(f"预览模式：已抓取 {preview_pages} 页，停止抓取")
        break
```

**配置处理**:
```python
default_config = {
    # 基本配置
    'start_url': None,
    'output_dir': 'output',
    'output_file': 'guide.md',
    
    # 爬虫配置
    'user_agent': 'GameGuideScraper/1.0',
    'delay': 1.0,
    'max_retries': 3,
    'retry_delay': 2.0,
    
    # 图片配置
    'download_images': True,
    'image_dir': None,
    'image_delay': 0.5,
    'skip_existing_images': True,
    
    # 其他配置...
}
```

## 数据结构

### 页面内容结构
```python
{
    'title': '页面标题',
    'url': '页面URL',
    'page_number': 1,
    'content': [
        {
            'type': 'text',
            'value': '文本内容'
        },
        {
            'type': 'image',
            'url': '图片URL',
            'alt': '图片描述',
            'local_path': '本地路径'
        },
        {
            'type': 'heading',
            'value': '标题文本',
            'level': 2
        }
    ]
}
```

### 文档结构
```python
{
    'title': '文档标题',
    'source_url': '来源URL',
    'page_titles': [
        {
            'page_number': 1,
            'title': '页面标题',
            'full_title': '第1页：页面标题',
            'id': 'page-1-页面标题',
            'url': '页面URL'
        }
    ],
    'toc': [
        {
            'level': 1,
            'title': '第1页：页面标题',
            'id': 'page-1-页面标题',
            'page_number': 1
        }
    ],
    'chapters': [
        {
            'title': '章节标题',
            'id': '章节ID',
            'content': [...],
            'sections': [...]
        }
    ]
}
```

## 配置系统

### 命令行参数
```python
# 基本参数
--start-url: 起始URL
--output-dir: 输出目录
--output-file: 输出文件名

# 图片参数
--download-images / --no-images: 是否下载图片
--image-dir: 图片保存目录
--image-delay: 图片下载间隔
--skip-existing-images / --force-download-images: 图片去重控制

# 爬虫参数
--delay: 页面请求间隔
--max-retries: 最大重试次数
--timeout: 请求超时时间
--preview --preview-pages: 预览模式

# 输出参数
--non-interactive: 非交互模式
--log-file: 日志文件
--quiet / --verbose: 输出级别
```

### 配置文件支持
```json
{
    "start_url": "https://www.gamersky.com/handbook/202409/1815206.shtml",
    "output_dir": "Guide_C",
    "output_file": "guide.md",
    "download_images": true,
    "image_dir": "Guide_C/images",
    "image_delay": 0.5,
    "skip_existing_images": true,
    "delay": 1.0,
    "max_retries": 3,
    "preview": false,
    "preview_pages": 3
}
```

## 错误处理

### 网络错误处理
```python
try:
    response = requests.get(url, stream=True, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error downloading image {url}: {e}")
    return None
except IOError as e:
    print(f"Error saving image {url} to {local_path}: {e}")
    return None
```

### 解析错误处理
```python
try:
    soup = BeautifulSoup(html, 'html.parser')
    # 解析逻辑...
except Exception as e:
    print(f"解析HTML内容时出错: {e}")
    return None
```

### 重试机制
```python
for attempt in range(self.max_retries):
    try:
        response = self.session.get(url, timeout=self.timeout)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        if attempt < self.max_retries - 1:
            time.sleep(self.retry_delay)
            continue
        else:
            raise e
```

## 性能优化

### 1. 图片去重
- 使用文件存在性检查避免重复下载
- MD5哈希文件名避免重复存储

### 2. 请求控制
- 可配置的请求间隔避免被封IP
- 连接复用提高效率

### 3. 内存管理
- 流式下载大文件
- 及时释放不需要的对象

### 4. 并发控制
- 单线程顺序处理避免服务器压力
- 可扩展为多线程并发下载

## 扩展性设计

### 1. 网站适配
- 解析器可扩展支持不同网站结构
- 配置化的CSS选择器

### 2. 输出格式
- 生成器接口化，支持多种输出格式
- 模板系统支持自定义格式

### 3. 内容处理
- 插件化的内容过滤器
- 可配置的处理规则

### 4. 存储后端
- 抽象化的存储接口
- 支持本地文件、数据库、云存储

## 测试策略

### 单元测试
- 每个组件独立测试
- Mock外部依赖

### 集成测试
- 端到端流程测试
- 真实网站测试

### 性能测试
- 大量页面处理测试
- 内存使用监控

### 错误测试
- 网络异常处理测试
- 恶意内容处理测试

## 部署建议

### 环境要求
```
Python 3.7+
requests
beautifulsoup4
lxml
```

### 安装步骤
```bash
# 克隆项目
git clone <repository>

# 安装依赖
pip install -r requirements.txt

# 运行测试
python -m game_guide_scraper.main --help
```

### 生产环境配置
- 设置合适的请求间隔
- 配置日志记录
- 监控资源使用
- 定期清理临时文件

## 维护指南

### 日志分析
- 监控错误率
- 分析性能瓶颈
- 跟踪使用模式

### 更新策略
- 定期更新依赖库
- 适配网站结构变化
- 优化算法性能

### 故障排除
- 网络连接问题
- 解析失败问题
- 文件权限问题
- 内存不足问题

这个技术文档提供了项目的完整技术实现细节，便于后续的维护和扩展开发。