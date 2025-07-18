# 黑神话悟空攻略爬虫使用手册

## 快速开始

### 基本使用
```bash
# 抓取前3页预览
python -m game_guide_scraper.main \
  --start-url "https://www.gamersky.com/handbook/202409/1815206.shtml" \
  --output-dir "Guide_C" \
  --preview --preview-pages 3

# 抓取完整攻略
python -m game_guide_scraper.main \
  --start-url "https://www.gamersky.com/handbook/202409/1815206.shtml" \
  --output-dir "Guide_C" \
  --output-file "complete_guide.md"
```

### 输出结果
运行成功后，你将得到：
- `Guide_C/guide.md` - 结构化的攻略文档
- `Guide_C/images/` - 高清游戏截图目录

## 命令行参数详解

### 基本参数

#### `--start-url`
- **说明**: 起始URL，爬虫从这个页面开始抓取
- **必需**: 是
- **示例**: `--start-url "https://www.gamersky.com/handbook/202409/1815206.shtml"`

#### `--output-dir`
- **说明**: 输出目录，用于保存生成的文件
- **默认值**: `output`
- **示例**: `--output-dir "Guide_C"`

#### `--output-file`
- **说明**: 输出文件名
- **默认值**: `guide.md`
- **示例**: `--output-file "black_myth_guide.md"`

### 图片相关参数

#### `--download-images` / `--no-images`
- **说明**: 是否下载图片
- **默认值**: 下载图片
- **示例**: 
  ```bash
  --download-images    # 下载图片（默认）
  --no-images         # 不下载图片
  ```

#### `--image-dir`
- **说明**: 图片保存目录
- **默认值**: `{output_dir}/images`
- **示例**: `--image-dir "Guide_C/screenshots"`

#### `--image-delay`
- **说明**: 图片下载间隔时间（秒）
- **默认值**: `0.5`
- **示例**: `--image-delay 1.0`

#### `--skip-existing-images` / `--force-download-images`
- **说明**: 是否跳过已存在的图片
- **默认值**: 跳过已存在的图片
- **示例**:
  ```bash
  --skip-existing-images    # 跳过已存在的图片（默认）
  --force-download-images   # 强制重新下载所有图片
  ```

### 爬虫行为参数

#### `--delay`
- **说明**: 页面请求间隔时间（秒）
- **默认值**: `1.0`
- **示例**: `--delay 2.0`

#### `--max-retries`
- **说明**: 请求失败时的最大重试次数
- **默认值**: `3`
- **示例**: `--max-retries 5`

#### `--timeout`
- **说明**: 请求超时时间（秒）
- **默认值**: `30`
- **示例**: `--timeout 60`

#### `--preview` / `--preview-pages`
- **说明**: 预览模式，只抓取前几页
- **默认值**: 关闭预览模式
- **示例**: 
  ```bash
  --preview --preview-pages 5    # 只抓取前5页
  ```

### 输出控制参数

#### `--non-interactive`
- **说明**: 非交互模式，适用于自动化脚本
- **默认值**: 交互模式
- **示例**: `--non-interactive`

#### `--log-file`
- **说明**: 日志文件路径
- **默认值**: 不保存日志文件
- **示例**: `--log-file "crawler.log"`

#### `--quiet` / `--verbose`
- **说明**: 输出详细程度
- **默认值**: 正常输出
- **示例**:
  ```bash
  --quiet      # 安静模式，只输出错误
  --verbose    # 详细模式，输出调试信息
  ```

## 使用场景

### 场景1: 快速预览
当你想要快速查看攻略内容时：
```bash
python -m game_guide_scraper.main \
  --start-url "https://www.gamersky.com/handbook/202409/1815206.shtml" \
  --output-dir "Preview" \
  --preview --preview-pages 3 \
  --non-interactive
```

### 场景2: 完整抓取
当你需要完整的攻略文档时：
```bash
python -m game_guide_scraper.main \
  --start-url "https://www.gamersky.com/handbook/202409/1815206.shtml" \
  --output-dir "Complete_Guide" \
  --output-file "black_myth_wukong_complete.md" \
  --delay 2.0 \
  --non-interactive
```

### 场景3: 只要文字不要图片
当你只需要文字内容时：
```bash
python -m game_guide_scraper.main \
  --start-url "https://www.gamersky.com/handbook/202409/1815206.shtml" \
  --output-dir "Text_Only" \
  --no-images \
  --non-interactive
```

### 场景4: 更新已有攻略
当你想要更新已有的攻略文档时：
```bash
python -m game_guide_scraper.main \
  --start-url "https://www.gamersky.com/handbook/202409/1815206.shtml" \
  --output-dir "Guide_C" \
  --skip-existing-images \
  --non-interactive
```

### 场景5: 重新下载所有内容
当你想要重新下载所有内容时：
```bash
python -m game_guide_scraper.main \
  --start-url "https://www.gamersky.com/handbook/202409/1815206.shtml" \
  --output-dir "Fresh_Guide" \
  --force-download-images \
  --non-interactive
```

## 配置文件使用

### 生成配置文件模板
```bash
python -m game_guide_scraper.main --generate-config "my_config.json"
```

### 使用配置文件
```bash
python -m game_guide_scraper.main --config "my_config.json"
```

### 配置文件示例
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
    "timeout": 30,
    "preview": false,
    "preview_pages": 3,
    "non_interactive": false,
    "log_file": "crawler.log",
    "quiet": false,
    "verbose": false
}
```

## 交互式控制

在交互模式下，你可以在程序运行时使用以下按键：

- `q`: 退出爬虫
- `p`: 暂停/恢复爬虫
- `c`: 继续（当爬虫暂停时）
- `s`: 显示当前状态
- `i`: 显示当前页面信息
- `d`: 显示下载统计
- `o`: 打开输出目录
- `+`: 增加请求延迟（减慢爬取速度）
- `-`: 减少请求延迟（加快爬取速度）
- `l`: 显示最近的日志
- `h`: 显示帮助信息

## 输出文档结构

生成的Markdown文档具有以下结构：

```markdown
# 《黑神话悟空》影神图妖怪位置及图鉴解锁方法 影神图100%收集攻略

*来源: [原始URL]*

## 目录

  - [第1页：小妖-第一回-狼斥候](#page-1-小妖-第一回-狼斥候)
  - [第2页：小妖-第一回-狼剑客](#page-2-小妖-第一回-狼剑客)
  - [第3页：小妖-第一回-狼校卫](#page-3-小妖-第一回-狼校卫)

---

## 第1页：小妖-第一回-狼斥候 <a id="page-1-小妖-第一回-狼斥候"></a>

[攻略内容...]

![游民星空](images/screenshot1.jpg)

[更多内容...]

## 第2页：小妖-第一回-狼剑客 <a id="page-2-小妖-第一回-狼剑客"></a>

[攻略内容...]
```

### 文档特点
- **自动目录**: 基于页面标题生成的可点击目录
- **锚点导航**: 每个页面标题都有对应的锚点
- **高清图片**: 1920x1080分辨率的游戏截图
- **干净内容**: 过滤了广告、编辑信息等无关内容
- **标准格式**: 符合Markdown标准，兼容各种阅读器

## 常见问题

### Q: 为什么有些图片下载失败？
A: 可能的原因：
- 网络连接不稳定
- 图片URL已失效
- 服务器限制访问

解决方法：
- 增加重试次数：`--max-retries 5`
- 增加请求间隔：`--delay 2.0`
- 检查网络连接

### Q: 如何加快抓取速度？
A: 可以尝试：
- 减少请求间隔：`--delay 0.5`
- 不下载图片：`--no-images`
- 使用预览模式：`--preview --preview-pages 5`

### Q: 如何处理中断的抓取？
A: 重新运行相同的命令，程序会：
- 自动跳过已下载的图片
- 继续从中断的地方开始
- 保持文件完整性

### Q: 生成的文档太大怎么办？
A: 可以：
- 使用预览模式只抓取部分内容
- 不下载图片减少文件大小
- 分批抓取不同的章节

### Q: 如何自定义输出格式？
A: 目前支持Markdown格式，你可以：
- 使用Markdown转换工具生成PDF、HTML等格式
- 修改生成器代码支持其他格式
- 使用模板系统自定义样式

## 性能建议

### 网络友好
- 设置合适的请求间隔（建议1-2秒）
- 不要设置过高的并发数
- 遵守网站的robots.txt规则

### 存储优化
- 定期清理不需要的图片文件
- 使用SSD存储提高I/O性能
- 监控磁盘空间使用

### 内存管理
- 对于大型攻略，考虑分批处理
- 及时关闭不需要的程序释放内存
- 监控内存使用情况

## 故障排除

### 网络错误
```
Error: 连接超时
```
解决方法：
- 检查网络连接
- 增加超时时间：`--timeout 60`
- 使用代理：配置系统代理

### 解析错误
```
Error: 无法解析页面内容
```
解决方法：
- 检查URL是否正确
- 网站结构可能已变化，需要更新解析规则
- 查看详细日志：`--verbose --log-file debug.log`

### 权限错误
```
Error: 无法创建目录
```
解决方法：
- 检查目录权限
- 使用管理员权限运行
- 更改输出目录到有权限的位置

### 磁盘空间不足
```
Error: 磁盘空间不足
```
解决方法：
- 清理磁盘空间
- 更改输出目录到空间充足的磁盘
- 不下载图片：`--no-images`

## 高级用法

### 批量处理
创建批处理脚本：
```bash
#!/bin/bash
# batch_crawl.sh

urls=(
    "https://www.gamersky.com/handbook/202409/1815206.shtml"
    "https://www.gamersky.com/handbook/202408/1803231.shtml"
    # 添加更多URL
)

for url in "${urls[@]}"; do
    echo "Processing: $url"
    python -m game_guide_scraper.main \
        --start-url "$url" \
        --output-dir "Guides/$(basename $url .shtml)" \
        --non-interactive
done
```

### 定时任务
使用cron定时更新攻略：
```bash
# 每天凌晨2点更新攻略
0 2 * * * /usr/bin/python3 -m game_guide_scraper.main --config /path/to/config.json
```

### 监控脚本
创建监控脚本检查抓取状态：
```python
import os
import time
from datetime import datetime

def check_guide_freshness(guide_path, max_age_hours=24):
    """检查攻略文件是否需要更新"""
    if not os.path.exists(guide_path):
        return True
    
    file_age = time.time() - os.path.getmtime(guide_path)
    return file_age > (max_age_hours * 3600)

if check_guide_freshness("Guide_C/guide.md"):
    print("攻略需要更新，开始抓取...")
    # 运行抓取命令
else:
    print("攻略是最新的，无需更新")
```

这个使用手册提供了完整的使用指导，帮助用户快速上手并解决常见问题。