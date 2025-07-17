# 安装指南

## 系统要求

### 操作系统
- Windows 10/11
- macOS 10.14 或更高版本
- Linux (Ubuntu 18.04+, CentOS 7+, 或其他主流发行版)

### Python版本
- Python 3.7 或更高版本
- 推荐使用 Python 3.8 或 3.9

### 硬件要求
- **内存**: 至少 2GB RAM（推荐 4GB+）
- **存储**: 至少 1GB 可用空间（用于存储攻略和图片）
- **网络**: 稳定的互联网连接

## 安装步骤

### 方法一：直接安装（推荐）

#### 1. 检查Python版本
```bash
python --version
# 或
python3 --version
```

确保版本为 3.7 或更高。

#### 2. 下载项目
```bash
# 如果使用Git
git clone <repository-url>
cd black-myth-guide-scraper

# 或者下载ZIP文件并解压
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 验证安装
```bash
python -m game_guide_scraper.main --version
```

如果显示版本信息，说明安装成功。

### 方法二：使用虚拟环境（推荐高级用户）

#### 1. 创建虚拟环境
```bash
# 使用venv
python -m venv venv

# 或使用conda
conda create -n guide-scraper python=3.8
```

#### 2. 激活虚拟环境
```bash
# Windows (venv)
venv\Scripts\activate

# macOS/Linux (venv)
source venv/bin/activate

# conda
conda activate guide-scraper
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 验证安装
```bash
python -m game_guide_scraper.main --version
```

## 依赖包说明

### 核心依赖
- **requests** (>=2.25.0): HTTP请求库
- **beautifulsoup4** (>=4.9.0): HTML解析库
- **lxml** (>=4.6.0): XML/HTML解析器

### 可选依赖
- **PyYAML**: 支持YAML格式配置文件
- **toml**: 支持TOML格式配置文件

## 平台特定安装说明

### Windows

#### 使用pip安装
```cmd
# 打开命令提示符或PowerShell
pip install -r requirements.txt
```

#### 常见问题
1. **pip不是内部或外部命令**
   - 确保Python已正确安装并添加到PATH
   - 尝试使用 `python -m pip` 代替 `pip`

2. **lxml安装失败**
   - 安装Microsoft Visual C++ Build Tools
   - 或使用预编译的wheel包：`pip install --only-binary=lxml lxml`

### macOS

#### 使用Homebrew（推荐）
```bash
# 安装Python（如果未安装）
brew install python

# 安装依赖
pip3 install -r requirements.txt
```

#### 使用系统Python
```bash
# 确保使用Python 3
python3 -m pip install -r requirements.txt
```

#### 常见问题
1. **权限错误**
   ```bash
   pip3 install --user -r requirements.txt
   ```

2. **SSL证书错误**
   ```bash
   pip3 install --trusted-host pypi.org --trusted-host pypi.python.org -r requirements.txt
   ```

### Linux

#### Ubuntu/Debian
```bash
# 更新包列表
sudo apt update

# 安装Python和pip（如果未安装）
sudo apt install python3 python3-pip

# 安装系统依赖
sudo apt install python3-dev libxml2-dev libxslt1-dev

# 安装Python依赖
pip3 install -r requirements.txt
```

#### CentOS/RHEL
```bash
# 安装Python和pip
sudo yum install python3 python3-pip

# 安装系统依赖
sudo yum install python3-devel libxml2-devel libxslt-devel

# 安装Python依赖
pip3 install -r requirements.txt
```

#### Arch Linux
```bash
# 安装Python和pip
sudo pacman -S python python-pip

# 安装系统依赖
sudo pacman -S python-lxml

# 安装其他依赖
pip install requests beautifulsoup4
```

## 验证安装

### 基本功能测试
```bash
# 检查版本
python -m game_guide_scraper.main --version

# 查看帮助
python -m game_guide_scraper.main --help

# 生成配置文件测试
python -m game_guide_scraper.main --generate-config test_config.json

# 预览模式测试
python -m game_guide_scraper.main --preview --preview-pages 1 --dry-run
```

### 完整功能测试
```bash
# 运行一个小规模测试
python -m game_guide_scraper.main --max-pages 2 --output-dir "test_output"
```

## 故障排除

### 安装问题

#### 1. Python版本过低
```bash
# 检查Python版本
python --version

# 如果版本低于3.7，需要升级Python
```

#### 2. pip安装失败
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

#### 3. 依赖包冲突
```bash
# 使用虚拟环境隔离依赖
python -m venv clean_env
source clean_env/bin/activate  # Linux/macOS
# 或
clean_env\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### 4. 网络连接问题
```bash
# 使用代理
pip install --proxy http://proxy.server:port -r requirements.txt

# 或使用离线安装
pip download -r requirements.txt
pip install --no-index --find-links . -r requirements.txt
```

### 运行时问题

#### 1. 模块找不到
```bash
# 确保在正确的目录中运行
cd /path/to/black-myth-guide-scraper
python -m game_guide_scraper.main
```

#### 2. 权限错误
```bash
# Linux/macOS
chmod +x game_guide_scraper/main.py

# Windows: 以管理员身份运行命令提示符
```

#### 3. 编码错误
```bash
# 设置环境变量
export PYTHONIOENCODING=utf-8  # Linux/macOS
set PYTHONIOENCODING=utf-8     # Windows
```

## 卸载

### 完全卸载
```bash
# 删除项目目录
rm -rf /path/to/black-myth-guide-scraper

# 如果使用了虚拟环境
rm -rf venv  # 或删除conda环境
conda env remove -n guide-scraper
```

### 仅卸载依赖包
```bash
pip uninstall -r requirements.txt
```

## 更新

### 更新项目代码
```bash
# 如果使用Git
git pull origin main

# 或重新下载最新版本
```

### 更新依赖包
```bash
pip install --upgrade -r requirements.txt
```

## 开发环境设置

### 安装开发依赖
```bash
# 如果有开发依赖文件
pip install -r requirements-dev.txt

# 或手动安装开发工具
pip install pytest black flake8 mypy
```

### 运行测试
```bash
# 运行所有测试
python -m pytest

# 运行特定测试
python -m pytest game_guide_scraper/tests/test_scraper.py
```

### 代码格式化
```bash
# 使用black格式化代码
black game_guide_scraper/

# 检查代码风格
flake8 game_guide_scraper/
```

## 性能优化

### 系统优化
```bash
# 增加文件描述符限制（Linux/macOS）
ulimit -n 4096

# 调整Python内存限制
export PYTHONMALLOC=malloc
```

### 配置优化
```bash
# 使用配置文件优化设置
python -m game_guide_scraper.main --generate-config optimized_config.json
# 然后编辑配置文件，调整delay、timeout等参数
```

---

如果在安装过程中遇到问题，请查看 [故障排除指南](USER_GUIDE.md#故障排除) 或提交Issue。