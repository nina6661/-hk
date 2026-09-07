# 香港出入境数据统计系统

基于香港入境事务处官方数据的出入境统计系统，自动生成周报、年度对比图表和数据预测。

## 功能特性

- **自动周报生成**：每周一自动生成上周完整数据报告
- **数据可视化**：出入境流量统计表、年度对比折线图、周度汇报小抄
- **历史数据查询**：支持按周查询和自定义时间范围查询
- **数据预测**：基于历史数据的客流趋势预测
- **定时任务**：自动数据同步和报告生成

## 系统架构

```
hk-border-stats/
├── app.py                 # Flask主应用
├── config.py              # 配置文件
├── requirements.txt       # Python依赖
├── database/              # 数据库模块
│   ├── models.py          # 数据库模型
│   └── schema.sql         # 数据库schema
├── data/                  # 数据存储
│   ├── raw/               # 原始CSV文件
│   └── reports/           # 生成的报告
├── services/              # 业务服务
│   ├── data_downloader.py # 数据下载服务
│   ├── data_importer.py   # 数据导入服务
│   ├── statistics.py      # 统计计算服务
│   └── scheduler.py       # 定时任务服务
├── static/                # 静态资源
│   ├── css/               # 样式文件
│   └── js/                # JavaScript文件
└── templates/             # 页面模板
    ├── index.html         # 首页（最新周报）
    ├── history.html       # 历史数据页面
    └── prediction.html    # 数据预测页面
```

## 安装部署

### 1. 安装依赖

```bash
cd hk-border-stats
pip install -r requirements.txt
```

### 2. 初始化系统

首次运行需要初始化数据库并导入历史数据：

```bash
python init_system.py
```

系统将自动：
- 创建SQLite数据库
- 下载CSV数据文件
- 导入2021年至今的所有历史数据
- 生成初始周报

### 3. 启动系统

```bash
python app.py
```

访问 http://localhost:5000 查看系统界面。

## 使用说明

### 首页 - 最新周报

自动展示上周（周一至周日）的完整数据报告，包含：
1. 出入境旅客流量统计表格
2. 年度对比折线图（入境和出境各一张）
3. 周度数据汇报小抄

### 历史数据页面

支持两种查询方式：

**按周查询**：
- 选择任意日期，系统自动匹配该日期所属自然周
- 生成对应周的完整报告

**自定义区间查询**：
- 手动选择起始日期和结束日期
- 生成指定时间段的专属报表

### 数据预测页面

基于最近30天的历史数据，使用移动平均法预测未来客流趋势：
- 支持7天、14天、30天预测
- 显示预测趋势图

## 定时任务

系统内置两个定时任务：

1. **数据同步**：每周一 09:00 自动下载最新数据
2. **报告生成**：每周一 12:00 自动生成上周周报

## API接口

系统提供以下API接口：

- `GET /api/current-week-report` - 获取当前周报告
- `GET /api/week-report?date=YYYY-MM-DD` - 获取指定周报告
- `GET /api/custom-range-report?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - 自定义范围报告
- `GET /api/year-comparison-charts` - 年度对比图数据
- `GET /api/prediction?days=7` - 客流预测
- `GET /api/available-weeks` - 可用周列表
- `POST /api/sync-data` - 手动触发数据同步

## 数据来源

数据来自香港特别行政区政府入境事务处公开数据：
- 数据门户：https://data.gov.hk/tc-data/dataset/hk-immd-set5-statistics-daily-passenger-traffic
- CSV文件：https://www.immd.gov.hk/opendata/eng/stat/daily_passenger_traffic_statistics.csv

数据包含2021年1月1日至今的每日出入境人次统计。

## 核心计算公式

**单日周环比**：
```
(指定周当天的流量 - 指定周前一周同一天的流量) / 指定周前一周同一天的流量 × 100%
```

**整周综合周环比**：
```
(指定周日均流量 - 指定周前一周日均流量) / 指定周前一周日均流量 × 100%
```

## 技术栈

- **后端**：Python 3.8+, Flask, SQLite
- **前端**：原生HTML + CSS + JavaScript
- **图表**：ECharts 5.4
- **数据处理**：Pandas, NumPy
- **定时任务**：APScheduler

## 注意事项

1. 首次运行需要较长时间下载和导入历史数据
2. 系统会每周一自动更新数据，无需手动干预
3. 预测结果仅供参考，实际数据可能有所不同
4. 数据源CSV文件每天更新前一天的数据

## 许可证

本项目仅供学习和研究使用。
