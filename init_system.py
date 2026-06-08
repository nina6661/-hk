"""
系统初始化脚本
首次运行时使用，下载并导入所有历史数据
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.data_downloader import DataDownloader
from services.data_importer import DataImporter
from services.statistics import StatisticsService
from database import DatabaseManager

def init_database():
    """初始化数据库"""
    print("=" * 60)
    print("步骤 1/4: 初始化数据库...")
    print("=" * 60)
    
    db = DatabaseManager()
    print(f"✓ 数据库创建成功: {db.db_path}")
    
    # 检查是否已初始化
    if db.get_config('initialized') == 'true':
        print("⚠ 系统已经初始化过，跳过初始化")
        return False
    
    return True

def download_data():
    """下载CSV数据文件"""
    print("\n" + "=" * 60)
    print("步骤 2/4: 下载数据文件...")
    print("=" * 60)
    
    downloader = DataDownloader()
    
    try:
        csv_path = downloader.download_latest_data()
        print(f"✓ 数据下载成功: {csv_path}")
        
        # 验证文件
        is_valid, message = downloader.validate_csv_file(csv_path)
        if is_valid:
            print(f"✓ 文件验证通过")
            return csv_path
        else:
            print(f"✗ 文件验证失败: {message}")
            return None
    except Exception as e:
        print(f"✗ 数据下载失败: {str(e)}")
        return None

def import_data(csv_path):
    """导入数据到数据库"""
    print("\n" + "=" * 60)
    print("步骤 3/4: 导入历史数据...")
    print("=" * 60)
    
    importer = DataImporter()
    
    try:
        records = importer.import_initial_data(csv_path)
        print(f"✓ 数据导入成功，共 {records} 条记录")
        return True
    except Exception as e:
        print(f"✗ 数据导入失败: {str(e)}")
        return False

def generate_initial_report():
    """生成初始周报"""
    print("\n" + "=" * 60)
    print("步骤 4/4: 生成初始周报...")
    print("=" * 60)
    
    stats_service = StatisticsService()
    
    try:
        # 生成上周报告
        report = stats_service.generate_weekly_report()
        print(f"✓ 周报生成成功: {report['week_start']} 至 {report['week_end']}")
        return True
    except Exception as e:
        print(f"✗ 周报生成失败: {str(e)}")
        return False

def show_summary():
    """显示系统摘要"""
    print("\n" + "=" * 60)
    print("系统初始化完成！")
    print("=" * 60)
    
    db = DatabaseManager()
    summary = db.get_import_summary()
    
    print(f"\n数据概览：")
    print(f"  - 总记录数: {summary['total_records']:,}")
    print(f"  - 数据范围: {summary['date_range']['min_date']} 至 {summary['date_range']['max_date']}")
    
    if summary['latest_sync']:
        print(f"  - 最后同步: {summary['latest_sync']['sync_time']}")
    
    print(f"\n启动系统：")
    print(f"  python app.py")
    print(f"\n访问地址：")
    print(f"  http://localhost:5000")
    print("=" * 60)

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("香港出入境数据统计系统 - 初始化向导")
    print("=" * 60)
    
    try:
        # 步骤1: 初始化数据库
        if not init_database():
            return
        
        # 步骤2: 下载数据
        csv_path = download_data()
        if not csv_path:
            return
        
        # 步骤3: 导入数据
        if not import_data(csv_path):
            return
        
        # 步骤4: 生成初始报告
        if not generate_initial_report():
            return
        
        # 显示摘要
        show_summary()
        
    except KeyboardInterrupt:
        print("\n\n初始化已取消")
    except Exception as e:
        print(f"\n✗ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
    """显示系统摘要"""
    print("\n" + "=" * 60)
    print("系统初始化完成！")
    print("=" * 60)
    
    from services.data_importer import DataImporter
    importer = DataImporter()
    summary = importer.get_import_summary()
    
    print(f"\n数据概览：")
    print(f"  - 总记录数: {summary['total_records']:,}")
    print(f"  - 数据范围: {summary['date_range']['min_date']} 至 {summary['date_range']['max_date']}")
    
    if summary['latest_sync']:
        print(f"  - 最后同步: {summary['latest_sync']['sync_time']}")
    
    print(f"\n启动系统：")
    print(f"  python app.py")
    print(f"\n访问地址：")
    print(f"  http://localhost:5000")
    print("=" * 60)
