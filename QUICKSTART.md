# 快速入门指南

## 5分钟上手黑神话悟空攻略爬虫

### 第一步：安装依赖
```bash
pip install -r requirements.txt
```

### 第二步：开始抓取

#### 🚀 最简单的使用方式
```bash
python -m game_guide_scraper.main
```
这将使用默认设置抓取完整攻略到 `output/guide.md`

#### 🎯 自定义输出位置
```bash
python -m game_guide_scraper.main --output-dir "我的攻略" --output-file "悟空攻略.md"
```

#### ⚡ 快速预览（只抓取前5页）
```bash
python -m game_guide_scraper.main --preview --preview-pages 5
```

#### 📱 仅文本模式（不下载图片）
```bash
python -m game_guide_scraper.main --no-images
```

### 第三步：交互式控制

运行过程中可以使用这些按键：
- `q` - 退出
- `p` - 暂停/继续  
- `s` - 查看状态
- `h` - 帮助

### 第四步：查看结果

抓取完成后，在输出目录中会有：
- `guide.md` - 完整攻略文档
- `images/` - 所有图片文件

## 常用命令组合

### 🎮 游戏玩家推荐
```bash
# 完整攻略，包含所有图片
python -m game_guide_scraper.main --output-dir "黑神话悟空完整攻略"
```

### 💾 节省空间版本
```bash
# 仅文本，节省磁盘空间
python -m game_guide_scraper.main --no-images --output-file "攻略文本版.md"
```

### 🔧 自定义配置
```bash
# 使用配置向导
python -m game_guide_scraper.main --wizard
```

### 📊 调试模式
```bash
# 详细日志输出
python -m game_guide_scraper.main --verbose --log-file "debug.log"
```

## 遇到问题？

### 网络太慢？
```bash
python -m game_guide_scraper.main --delay 2.0 --timeout 60
```

### 想要断点续传？
```bash
python -m game_guide_scraper.main --start-page 20
```

### 只要特定内容？
```bash
python -m game_guide_scraper.main --include-keywords "boss,技巧" --max-pages 10
```

## 下一步

- 查看 [README.md](README.md) 了解完整功能
- 使用 `--examples` 查看更多示例
- 使用 `--help` 查看所有选项

开始你的攻略收集之旅吧！🎮✨