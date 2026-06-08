"""
系统配置文件
"""
import os
from datetime import datetime

# 基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

# 数据库配置
DATABASE_PATH = os.path.join(DATABASE_DIR, 'border_stats.db')

# 数据源配置
DATA_SOURCE_URL = 'https://data.gov.hk/en-data/dataset/hk-immd-set5-statistics-daily-passenger-traffic'
CSV_DOWNLOAD_URL = 'https://www.immd.gov.hk/opendata/eng/transport/immigration_clearance/statistics_on_daily_passenger_traffic.csv'

# 定时任务配置
SCHEDULE_DATA_SYNC = {
    'day_of_week': 'mon',
    'hour': 9,
    'minute': 0
}

SCHEDULE_REPORT_GENERATION = {
    'day_of_week': 'mon',
    'hour': 12,
    'minute': 0
}

# 初始数据导入起始日期
INITIAL_DATA_START_DATE = '2021-01-01'

# Flask配置
SECRET_KEY = os.urandom(24).hex()
DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
HOST = '0.0.0.0'
PORT = 5001

# 创建必要的目录
for directory in [DATA_DIR, RAW_DATA_DIR, REPORTS_DIR, DATABASE_DIR, STATIC_DIR, TEMPLATE_DIR]:
    os.makedirs(directory, exist_ok=True)
