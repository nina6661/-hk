"""
数据下载服务
负责从香港政府数据门户网站下载CSV数据文件
"""
import requests
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataDownloader:
    """数据下载器"""
    
    def __init__(self):
        from config import CSV_DOWNLOAD_URL, RAW_DATA_DIR
        self.download_url = CSV_DOWNLOAD_URL
        self.raw_data_dir = RAW_DATA_DIR
        os.makedirs(self.raw_data_dir, exist_ok=True)
    
    def download_latest_data(self):
        """
        下载最新的出入境统计数据CSV文件
        返回：保存的文件路径
        """
        try:
            logger.info(f"开始下载数据: {self.download_url}")
            
            # 发送HTTP请求
            response = requests.get(self.download_url, timeout=30)
            response.raise_for_status()
            
            # 生成文件名（带时间戳）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'daily_passenger_traffic_{timestamp}.csv'
            filepath = os.path.join(self.raw_data_dir, filename)
            
            # 保存文件
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"数据下载成功，保存至: {filepath}")
            logger.info(f"文件大小: {len(response.content)} bytes")
            
            return filepath
            
        except requests.exceptions.RequestException as e:
            logger.error(f"下载数据失败: {str(e)}")
            raise Exception(f"下载数据失败: {str(e)}")
        except Exception as e:
            logger.error(f"保存数据文件失败: {str(e)}")
            raise Exception(f"保存数据文件失败: {str(e)}")
    
    def get_latest_csv_file(self):
        """
        获取最新的CSV文件路径
        返回：最新CSV文件的完整路径，如果没有则返回None
        """
        try:
            csv_files = [f for f in os.listdir(self.raw_data_dir) 
                        if f.endswith('.csv')]
            
            if not csv_files:
                return None
            
            # 按文件名排序（文件名包含时间戳）
            csv_files.sort(reverse=True)
            latest_file = os.path.join(self.raw_data_dir, csv_files[0])
            
            logger.info(f"找到最新CSV文件: {latest_file}")
            return latest_file
            
        except Exception as e:
            logger.error(f"获取最新CSV文件失败: {str(e)}")
            return None
    
    def validate_csv_file(self, filepath):
        """
        验证CSV文件格式是否正确（英文版）
        返回：(是否有效, 错误信息)
        """
        try:
            import pandas as pd
            
            # 读取CSV文件
            df = pd.read_csv(filepath, encoding='utf-8')
            
            # 检查必需的列（英文版CSV）
            required_columns = ['Date', 'Control Point', 'Arrival / Departure', 
                              'Hong Kong Residents', 'Mainland Visitors', 
                              'Other Visitors', 'Total']
            
            missing_columns = [col for col in required_columns 
                             if col not in df.columns]
            
            if missing_columns:
                return False, f"缺少必需列: {', '.join(missing_columns)}"
            
            # 检查数据行数
            if len(df) == 0:
                return False, "CSV文件为空"
            
            logger.info(f"CSV文件验证通过，共 {len(df)} 行数据")
            return True, "验证通过"
            
        except Exception as e:
            return False, f"验证失败: {str(e)}"
