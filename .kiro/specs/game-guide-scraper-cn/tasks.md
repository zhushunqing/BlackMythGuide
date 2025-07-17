# 实现计划

- [x] 1. 搭建项目基础结构
  - 创建项目目录结构
  - 设置虚拟环境
  - 创建配置文件模板
  - _需求: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 2. 实现网页抓取器（Scraper）
  - [x] 2.1 实现基本的HTTP请求功能
    - 创建Scraper类
    - 实现fetch_page方法
    - 添加请求延迟机制
    - 处理HTTP错误和异常
    - _需求: 1.1, 1.3, 1.4, 5.1, 5.2, 5.3_
  
  - [x] 2.2 实现"下一页"链接提取功能
    - 实现get_next_page_url方法
    - 处理相对URL和绝对URL
    - 添加循环检测机制
    - _需求: 1.2_

- [x] 3. 实现内容解析器（Parser）
  - [x] 3.1 实现HTML解析基础功能
    - 创建Parser类
    - 实现parse_content方法
    - _需求: 2.1, 2.3, 2.4, 2.5_
  
  - [x] 3.2 实现标题提取功能
    - 实现extract_title方法
    - 处理标题格式化
    - _需求: 2.1, 2.5_
  
  - [x] 3.3 实现正文内容提取功能
    - 实现extract_content方法
    - 处理文本段落和格式
    - 过滤广告和无关内容
    - _需求: 2.1, 2.3, 2.4, 2.5_
  
  - [x] 3.4 实现图片提取功能
    - 实现extract_images方法
    - 处理图片URL和描述
    - _需求: 2.2, 2.3_

- [x] 4. 实现图片下载器（ImageDownloader）
  - [x] 4.1 实现基本的图片下载功能
    - 创建ImageDownloader类
    - 实现download_image方法
    - 添加下载延迟机制
    - 处理下载错误和异常
    - _需求: 2.2, 5.3_
  
  - [x] 4.2 实现批量下载功能
    - 实现download_all_images方法
    - 维护图片URL到本地路径的映射
    - _需求: 2.2_

- [x] 5. 实现内容组织器（ContentOrganizer）
  - [x] 5.1 实现内容收集功能
    - 创建ContentOrganizer类
    - 实现add_page_content方法
    - 存储和管理多个页面的内容
    - _需求: 3.1, 3.5_
  
  - [x] 5.2 实现内容结构化功能
    - 实现organize_content方法
    - 根据页码和标题组织内容
    - 创建章节和小节结构
    - _需求: 3.1, 3.5_
  
  - [x] 5.3 实现目录生成功能
    - 实现generate_toc方法
    - 根据内容结构生成目录
    - _需求: 3.2_

- [x] 6. 实现Markdown生成器（MarkdownGenerator）
  - [x] 6.1 实现基本的Markdown生成功能
    - 创建MarkdownGenerator类
    - 实现generate_markdown方法
    - 处理文本和图片的Markdown格式
    - _需求: 3.3, 3.4_
  
  - [x] 6.2 实现目录的Markdown生成功能
    - 实现generate_toc_markdown方法
    - 创建带链接的目录
    - _需求: 3.2_
  
  - [x] 6.3 实现Markdown保存功能
    - 实现save_markdown方法
    - 处理文件写入和错误
    - _需求: 3.3, 3.4_

- [x] 7. 实现主控制器（Controller）
  - [x] 7.1 实现基本控制流程
    - 创建Controller类
    - 实现run方法
    - 协调各组件工作
    - _需求: 1.1, 1.2, 3.1_
  
  - [x] 7.2 实现进度报告功能
    - 实现report_progress方法
    - 提供抓取状态和进度信息
    - _需求: 4.5_
  
  - [x] 7.3 实现配置处理功能
    - 处理用户配置
    - 设置默认值
    - _需求: 4.1, 4.2, 4.3, 4.4_

- [x] 8. 实现命令行接口
  - [x] 8.1 创建主程序入口
    - 创建main.py
    - 解析命令行参数
    - 加载配置
    - _需求: 4.1, 4.2, 4.3, 4.4_
  
  - [x] 8.2 实现用户交互功能
    - 添加命令行参数解析
    - 提供帮助信息
    - 处理用户输入
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5_

- [-] 9. 编写单元测试
  - [x] 9.1 为Scraper编写测试
    - 测试fetch_page方法
    - 测试get_next_page_url方法
    - 模拟HTTP响应
    - _需求: 1.1, 1.2, 1.3, 1.4_
  
  - [ ] 9.2 为Parser编写测试
    - 测试parse_content方法
    - 测试extract_title方法
    - 测试extract_content方法
    - 测试extract_images方法
    - _需求: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ] 9.3 为ImageDownloader编写测试
    - 测试download_image方法
    - 测试download_all_images方法
    - 模拟图片下载
    - _需求: 2.2_
  
  - [ ] 9.4 为ContentOrganizer编写测试
    - 测试add_page_content方法
    - 测试organize_content方法
    - 测试generate_toc方法
    - _需求: 3.1, 3.2, 3.5_
  
  - [ ] 9.5 为MarkdownGenerator编写测试
    - 测试generate_markdown方法
    - 测试generate_toc_markdown方法
    - 测试save_markdown方法
    - _需求: 3.2, 3.3, 3.4_

- [ ] 10. 集成测试和优化
  - [ ] 10.1 编写集成测试
    - 测试完整的抓取流程
    - 验证生成的Markdown文档
    - _需求: 1.1, 1.2, 2.1, 2.2, 3.1, 3.3, 3.4_
  
  - [ ] 10.2 性能优化
    - 优化内存使用
    - 优化执行速度
    - 添加缓存机制
    - _需求: 5.3, 5.4_
  
  - [ ] 10.3 错误处理优化
    - 完善错误处理机制
    - 添加日志记录
    - 实现恢复机制
    - _需求: 1.4, 1.5_