# 快速开始指南

## 系统要求

- Python 3.8 或更高版本
- 网络连接（用于下载数据）

## 快速启动（推荐）

### macOS / Linux

```bash
cd hk-border-stats
chmod +x start.sh
./start.sh
```

### Windows

双击运行 `start.bat` 或在命令提示符中执行：

```cmd
cd hk-border-stats
start.bat
```

启动脚本会自动完成以下操作：
1. 检查Python环境
2. 安装所需依赖
3. 初始化数据库
4. 启动Web服务器

启动成功后，浏览器访问 http://localhost:5000

## 手动安装步骤

如果你想手动安装，可以按以下步骤操作：

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python init_system.py
```

这个过程会：
- 创建SQLite数据库
- 下载官方CSV数据文件
- 导入2021年至今的所有历史数据（首次运行约需1-2分钟）

### 3. 启动服务

```bash
python app.py
```

### 4. 访问系统

打开浏览器访问 http://localhost:5000

## 常见问题

### Q: 初始化失败怎么办？

A: 请检查：
1. Python版本是否 >= 3.8
2. 网络是否可以访问 https://www.immd.gov.hk
3. 是否有足够的磁盘空间

### Q: 数据多久更新一次？

A: 系统会每周一自动更新数据，你也可以在系统中手动触发同步。

### Q: 可以修改端口吗？

A: 可以，修改 `config.py` 中的 `PORT` 配置。

### Q: 数据存储在哪里？

A: 数据存储在本地的 SQLite 数据库中，位于 `database/border_stats.db`。

## 下一步

系统启动后，你可以：

1. 查看首页的最新周报
2. 在历史数据页面查询过往数据
3. 在预测页面查看客流趋势预测
4. 通过API接口获取数据（参考README.md）

详细使用说明请参考 README.md
