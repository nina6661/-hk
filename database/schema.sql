-- 香港出入境数据统计系统数据库Schema

-- 出入境每日统计数据表
CREATE TABLE IF NOT EXISTS daily_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,  -- 日期 YYYY-MM-DD
    control_point TEXT NOT NULL,  -- 管制站名称
    direction TEXT NOT NULL,  -- 入境/出境
    hk_residents INTEGER DEFAULT 0,  -- 香港居民人次
    mainland_visitors INTEGER DEFAULT 0,  -- 内地访客人次
    other_visitors INTEGER DEFAULT 0,  -- 其他访客人次
    total INTEGER DEFAULT 0,  -- 总计
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, control_point, direction)
);

-- 创建索引以优化查询性能
CREATE INDEX IF NOT EXISTS idx_date ON daily_statistics(date);
CREATE INDEX IF NOT EXISTS idx_control_point ON daily_statistics(control_point);
CREATE INDEX IF NOT EXISTS idx_direction ON daily_statistics(direction);
CREATE INDEX IF NOT EXISTS idx_date_direction ON daily_statistics(date, direction);

-- 周报数据表
CREATE TABLE IF NOT EXISTS weekly_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    week_number INTEGER NOT NULL,
    start_date TEXT NOT NULL,  -- 周一日期
    end_date TEXT NOT NULL,  -- 周日日期
    report_data TEXT NOT NULL,  -- JSON格式的完整报告数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, week_number)
);

-- 数据同步日志表
CREATE TABLE IF NOT EXISTS sync_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sync_type TEXT NOT NULL,  -- 'initial' 或 'weekly'
    csv_file_path TEXT,
    records_added INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    status TEXT NOT NULL,  -- 'success', 'failed'
    error_message TEXT,
    sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
