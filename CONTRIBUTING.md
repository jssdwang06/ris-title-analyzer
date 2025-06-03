# 贡献指南

感谢您对RIS标题词频分析工具的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告问题
如果您发现了bug或有改进建议：

1. 检查 [Issues](https://github.com/jssdwang06/ris-title-analyzer/issues) 确保问题未被报告
2. 创建新的Issue，包含：
   - 清晰的问题描述
   - 复现步骤
   - 预期行为 vs 实际行为
   - 系统环境信息（操作系统、Python版本等）
   - 相关截图或错误日志

### 功能建议
我们欢迎新功能建议：

1. 在Issues中创建功能请求
2. 描述功能的使用场景
3. 解释为什么这个功能有用
4. 如果可能，提供实现思路

### 代码贡献

#### 开发环境设置
```bash
# 1. Fork并克隆仓库
git clone https://github.com/jssdwang06/ris-title-analyzer.git
cd ris-title-analyzer

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行程序确保环境正常
python ris_title_analyzer_gui.py
```

#### 提交代码
1. 创建功能分支：`git checkout -b feature/amazing-feature`
2. 进行更改并测试
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建Pull Request

#### 代码规范
- 使用Python PEP 8编码规范
- 添加适当的注释和文档字符串
- 确保代码在Python 3.7+上运行
- 测试您的更改

#### 提交信息格式
```
类型: 简短描述

详细描述（如果需要）

- 具体更改1
- 具体更改2
```

类型包括：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

## 📋 开发指南

### 项目结构
```
ris-title-analyzer/
├── ris_title_analyzer.py          # 命令行版本
├── ris_title_analyzer_gui.py      # GUI版本
├── requirements.txt               # 依赖列表
├── README.md                     # 项目说明
├── CHANGELOG.md                  # 更新日志
├── LICENSE                       # 许可证
└── 启动GUI版本.bat               # Windows启动脚本
```

### 核心功能模块
- **RIS解析**: `parse_ris_file()` 函数
- **词频分析**: `analyze_word_frequency()` 函数
- **词形规范化**: `normalize_word()` 函数
- **GUI界面**: `RISAnalyzerGUI` 类
- **图表生成**: `update_chart()` 方法

### 测试
在提交代码前，请确保：
- [ ] GUI版本正常启动
- [ ] 能够正确解析RIS文件
- [ ] 词频分析结果准确
- [ ] 图表生成正常
- [ ] 文件导出功能正常

## 🎯 优先级任务

我们特别欢迎以下方面的贡献：

### 高优先级
- 🐛 Bug修复
- 📚 文档改进
- 🌐 多语言支持
- 🔧 性能优化

### 中优先级
- 🎨 UI/UX改进
- 📊 新的可视化选项
- 🔍 更多文件格式支持
- 📱 跨平台兼容性

### 低优先级
- 🚀 新功能特性
- 🎯 高级分析功能
- 🔌 插件系统

## 📞 联系方式

如果您有任何问题或需要帮助：

- 🐛 [GitHub Issues](https://github.com/jssdwang06/ris-title-analyzer/issues)

## 📄 许可证

通过贡献代码，您同意您的贡献将在MIT许可证下发布。

---

再次感谢您的贡献！🎉
