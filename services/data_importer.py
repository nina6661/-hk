"""
数据导入服务
负责将CSV数据导入到SQLite数据库
"""
import pandas as pd
import os
from datetime import datetime
import logging
from database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataImporter:
    """数据导入器"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def import_from_csv(self, csv_filepath):
        """
        从CSV文件导入数据到数据库
        返回：新增的记录数
        """
        try:
            logger.info(f"开始导入CSV文件: {csv_filepath}")
            
            # 读取CSV文件
            df = pd.read_csv(csv_filepath, encoding='utf-8')
            
            # 数据清洗和转换
            df = self._clean_data(df)
            
            # 准备批量插入数据
            stats_list = []
            for _, row in df.iterrows():
                stats_list.append((
                    row['date'],
                    row['control_point'],
                    row['direction'],
                    int(row['hk_residents']),
                    int(row['mainland_visitors']),
                    int(row['other_visitors']),
                    int(row['total'])
                ))
            
            # 批量插入数据库
            self.db.batch_insert_daily_stats(stats_list)
            
            logger.info(f"数据导入成功，共处理 {len(stats_list)} 条记录")
            
            # 记录同步日志
            self.db.add_sync_log(
                sync_type='weekly',
                csv_file_path=csv_filepath,
                records_added=len(stats_list),
                records_updated=0,
                status='success'
            )
            
            return len(stats_list)
            
        except Exception as e:
            logger.error(f"导入CSV文件失败: {str(e)}")
            
            # 记录失败日志
            self.db.add_sync_log(
                sync_type='weekly',
                csv_file_path=csv_filepath,
                records_added=0,
                records_updated=0,
                status='failed',
                error_message=str(e)
            )
            
            raise Exception(f"导入CSV文件失败: {str(e)}")
    
    def import_initial_data(self, csv_filepath):
        """
        初始化导入历史数据
        用于首次运行时导入所有历史数据
        """
        try:
            logger.info(f"开始初始化导入历史数据: {csv_filepath}")
            
            # 读取CSV文件
            df = pd.read_csv(csv_filepath, encoding='utf-8')
            
            # 数据清洗和转换
            df = self._clean_data(df)
            
            # 过滤出从2021-01-01开始的数据
            from config import INITIAL_DATA_START_DATE
            df = df[df['date'] >= INITIAL_DATA_START_DATE]
            
            # 准备批量插入数据
            stats_list = []
            for _, row in df.iterrows():
                stats_list.append((
                    row['date'],
                    row['control_point'],
                    row['direction'],
                    int(row['hk_residents']),
                    int(row['mainland_visitors']),
                    int(row['other_visitors']),
                    int(row['total'])
                ))
            
            # 批量插入数据库
            self.db.batch_insert_daily_stats(stats_list)
            
            logger.info(f"初始化导入成功，共处理 {len(stats_list)} 条记录")
            
            # 记录同步日志
            self.db.add_sync_log(
                sync_type='initial',
                csv_file_path=csv_filepath,
                records_added=len(stats_list),
                records_updated=0,
                status='success'
            )
            
            # 设置初始化标记
            self.db.set_config('initialized', 'true', '系统已初始化')
            self.db.set_config('initial_date', 
                             datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             '初始化时间')
            
            return len(stats_list)
            
        except Exception as e:
            logger.error(f"初始化导入失败: {str(e)}")
            
            # 记录失败日志
            self.db.add_sync_log(
                sync_type='initial',
                csv_file_path=csv_filepath,
                records_added=0,
                records_updated=0,
                status='failed',
                error_message=str(e)
            )
            
            raise Exception(f"初始化导入失败: {str(e)}")
    
    def _clean_data(self, df):
        """
        清洗和转换数据（英文版CSV）
        """
        # 重命名列（英文 -> 内部标准名）
        column_mapping = {
            'Date': 'date',
            'Control Point': 'control_point',
            'Arrival / Departure': 'direction',
            'Hong Kong Residents': 'hk_residents',
            'Mainland Visitors': 'mainland_visitors',
            'Other Visitors': 'other_visitors',
            'Total': 'total'
        }
        
        df = df.rename(columns=column_mapping)
        
        # 转换日期格式（DD-MM-YYYY -> YYYY-MM-DD）
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y').dt.strftime('%Y-%m-%d')
        
        # 将Arrival/Departure转换为中文
        df['direction'] = df['direction'].map({
            'Arrival': '入境',
            'Departure': '出境'
        })
        
        # 处理缺失值（填充为0）
        numeric_columns = ['hk_residents', 'mainland_visitors', 
                         'other_visitors', 'total']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # 移除重复记录（保留最新的）
        df = df.drop_duplicates(subset=['date', 'control_point', 'direction'], 
                               keep='last')
        
        return df
    
    def is_initialized(self):
        """
        检查系统是否已初始化
        """
        initialized = self.db.get_config('initialized')
        return initialized == 'true'
    
    def get_import_summary(self):
        """
        获取导入数据摘要
        """
        date_range = self.db.get_date_range()
        total_records = self.db.get_stats_count()
        latest_sync = self.db.get_latest_sync_log()
        
        return {
            'total_records': total_records,
            'date_range': date_range,
            'latest_sync': latest_sync
        }
