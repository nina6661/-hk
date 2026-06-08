"""
定时任务服务
负责每周一自动下载数据和生成报告
"""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchedulerService:
    """定时任务服务"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """设置定时任务"""
        # 每周一09:00同步数据
        self.scheduler.add_job(
            self._sync_data_job,
            'cron',
            day_of_week='mon',
            hour=9,
            minute=0,
            id='sync_data',
            name='同步出入境数据'
        )
        
        # 每周一12:00生成周报
        self.scheduler.add_job(
            self._generate_report_job,
            'cron',
            day_of_week='mon',
            hour=12,
            minute=0,
            id='generate_report',
            name='生成周报'
        )
        
        logger.info("定时任务设置完成")
    
    def _sync_data_job(self):
        """数据同步任务"""
        try:
            logger.info("开始执行数据同步任务...")
            
            # 添加项目路径到sys.path
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            from services.data_downloader import DataDownloader
            from services.data_importer import DataImporter
            
            downloader = DataDownloader()
            importer = DataImporter()
            
            # 下载数据
            csv_path = downloader.download_latest_data()
            
            # 导入数据
            new_records = importer.import_from_csv(csv_path)
            
            logger.info(f"数据同步完成，新增 {new_records} 条记录")
            
        except Exception as e:
            logger.error(f"数据同步任务失败: {str(e)}")
    
    def _generate_report_job(self):
        """周报生成任务"""
        try:
            logger.info("开始执行周报生成任务...")
            
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            from services.statistics import StatisticsService
            
            stats_service = StatisticsService()
            report = stats_service.generate_weekly_report()
            
            logger.info(f"周报生成完成: {report['week_start']} 至 {report['week_end']}")
            
        except Exception as e:
            logger.error(f"周报生成任务失败: {str(e)}")
    
    def start(self):
        """启动定时任务"""
        self.scheduler.start()
        logger.info("定时任务服务已启动")
    
    def stop(self):
        """停止定时任务"""
        self.scheduler.shutdown()
        logger.info("定时任务服务已停止")
    
    def get_jobs(self):
        """获取所有任务"""
        return self.scheduler.get_jobs()
