"""
数据库模型和管理类
"""
import sqlite3
import json
import os
from datetime import datetime, timedelta
from contextlib import contextmanager

class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, db_path=None):
        """初始化数据库管理器"""
        if db_path is None:
            from config import DATABASE_PATH
            db_path = DATABASE_PATH
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库，创建表结构"""
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 读取schema文件
        from config import DATABASE_DIR
        schema_path = os.path.join(DATABASE_DIR, 'schema.sql')
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # 执行schema
        with self.get_connection() as conn:
            conn.executescript(schema_sql)
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def insert_daily_stat(self, date, control_point, direction, 
                          hk_residents, mainland_visitors, 
                          other_visitors, total):
        """插入或更新每日统计数据"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO daily_statistics 
                (date, control_point, direction, hk_residents, mainland_visitors, 
                 other_visitors, total, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(date, control_point, direction) DO UPDATE SET
                    control_point = excluded.control_point,
                    direction = excluded.direction,
                    hk_residents = excluded.hk_residents,
                    mainland_visitors = excluded.mainland_visitors,
                    other_visitors = excluded.other_visitors,
                    total = excluded.total,
                    updated_at = CURRENT_TIMESTAMP
            """, (date, control_point, direction, hk_residents, 
                  mainland_visitors, other_visitors, total))
            return cursor.lastrowid
    
    def batch_insert_daily_stats(self, stats_list):
        """批量插入每日统计数据"""
        with self.get_connection() as conn:
            conn.executemany("""
                INSERT INTO daily_statistics 
                (date, control_point, direction, hk_residents, mainland_visitors, 
                 other_visitors, total, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(date, control_point, direction) DO UPDATE SET
                    control_point = excluded.control_point,
                    direction = excluded.direction,
                    hk_residents = excluded.hk_residents,
                    mainland_visitors = excluded.mainland_visitors,
                    other_visitors = excluded.other_visitors,
                    total = excluded.total,
                    updated_at = CURRENT_TIMESTAMP
            """, stats_list)
    
    def get_daily_stats_by_date(self, date):
        """获取指定日期的统计数据"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM daily_statistics 
                WHERE date = ?
                ORDER BY direction, control_point
            """, (date,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_daily_stats_by_range(self, start_date, end_date):
        """获取日期范围内的统计数据"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM daily_statistics 
                WHERE date >= ? AND date <= ?
                ORDER BY date, direction, control_point
            """, (start_date, end_date))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_aggregated_stats_by_date(self, date):
        """
        获取指定日期的聚合统计数据（按入境/出境聚合）
        返回格式：
        {
            'date': '2024-01-01',
            'inbound': {
                'hk_residents': 总数,
                'mainland_visitors': 总数,
                'other_visitors': 总数,
                'total': 总数
            },
            'outbound': {...}
        }
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    direction,
                    SUM(hk_residents) as hk_residents,
                    SUM(mainland_visitors) as mainland_visitors,
                    SUM(other_visitors) as other_visitors,
                    SUM(total) as total
                FROM daily_statistics 
                WHERE date = ?
                GROUP BY direction
            """, (date,))
            
            result = {'date': date, 'inbound': {}, 'outbound': {}}
            for row in cursor.fetchall():
                direction = 'inbound' if '入境' in row['direction'] else 'outbound'
                result[direction] = {
                    'hk_residents': row['hk_residents'],
                    'mainland_visitors': row['mainland_visitors'],
                    'other_visitors': row['other_visitors'],
                    'total': row['total']
                }
            return result
    
    def get_date_range(self):
        """获取数据库中的日期范围"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT MIN(date) as min_date, MAX(date) as max_date
                FROM daily_statistics
            """)
            row = cursor.fetchone()
            return {
                'min_date': row['min_date'],
                'max_date': row['max_date']
            }
    
    def save_weekly_report(self, year, week_number, start_date, 
                           end_date, report_data):
        """保存周报数据"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO weekly_reports 
                (year, week_number, start_date, end_date, report_data)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(year, week_number) DO UPDATE SET
                    start_date = excluded.start_date,
                    end_date = excluded.end_date,
                    report_data = excluded.report_data
            """, (year, week_number, start_date, end_date, 
                  json.dumps(report_data, ensure_ascii=False)))
    
    def get_weekly_report(self, year, week_number):
        """获取周报数据"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM weekly_reports 
                WHERE year = ? AND week_number = ?
            """, (year, week_number))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['report_data'] = json.loads(result['report_data'])
                return result
            return None
    
    def get_all_weekly_reports(self):
        """获取所有周报列表"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT year, week_number, start_date, end_date, created_at
                FROM weekly_reports
                ORDER BY year DESC, week_number DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def add_sync_log(self, sync_type, csv_file_path, records_added, 
                     records_updated, status, error_message=None):
        """添加同步日志"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO sync_logs 
                (sync_type, csv_file_path, records_added, records_updated, 
                 status, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sync_type, csv_file_path, records_added, records_updated, 
                  status, error_message))
            return cursor.lastrowid
    
    def get_latest_sync_log(self):
        """获取最新的同步日志"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM sync_logs 
                ORDER BY sync_time DESC LIMIT 1
            """)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def set_config(self, key, value, description=None):
        """设置系统配置"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO system_config (key, value, description, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    description = excluded.description,
                    updated_at = CURRENT_TIMESTAMP
            """, (key, value, description))
    
    def get_config(self, key):
        """获取系统配置"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT value FROM system_config WHERE key = ?
            """, (key,))
            row = cursor.fetchone()
            return row['value'] if row else None
    
    def get_stats_count(self):
        """获取统计数据总数"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) as count FROM daily_statistics")
            return cursor.fetchone()['count']
