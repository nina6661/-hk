# 香港出入境数据看板 - 项目指南

## 项目概览
单页面 HTML 数据看板，可查看香港每日出入境人流量、周度对比、同比对趋势图。

## 核心文件
| 文件 | 说明 |
|-------|------|
| `index.html` | 主文件，需配合 `data.json` + HTTP 服务器使用 |
| `data.json` | 2075 天数据（2021-01-01 至 2026-09-06） |
| `index-offline.html` | 离线版，数据内嵌，双击即开，无需服务器 |
| `build_offline.py` | 生成 `index-offline.html` 的脚本 |
| `update_data.py` | 自动抓取官方 CSV 更新 `data.json` |
| `start.sh` | 启动本地 HTTP 服务器 |

## 数据来源
香港入境事务处官方 CSV：https://data.gov.hk/tc-data/dataset/hk-immd-set5-statistics-daily-passenger-traffic

## 常见修改
- 更新数据：运行 `python3 update_data.py`，或手动更新 `data.json`
- 生成离线版：`python3 build_offline.py`
- 本地预览：`sh start.sh`（打开 http://localhost:8000）

## 部署
- **Vercel**：导入 GitHub repo，使用 `@vercel/static` 静态部署，根目录指向 `index.html`
- **Netlify**：已配置 `netlify.toml`
- **GitHub Pages**：设为静态页面源

## YoY 对齐逻辑
今年某日 → 找去年同星期几的日期（不是同日期）。
例：2026-09-07 （周一）对齐 2025-09-08 （周一）。
实现函数：`lySameDay(cyDate)` （已放在全局作用域）。

## 重要约定
- 不要把编辑中的内容暴露给用户
- 保持软件开发和编程技能的专业性
- 注意跟踪总结
