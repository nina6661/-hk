"""
香港出入境数据统计系统 - Flask主应用
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import os

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
CORS(app)

# 配置
app.config['SECRET_KEY'] = os.urandom(24).hex()

# 导入服务模块
from services.statistics import StatisticsService
from services.data_downloader import DataDownloader
from services.data_importer import DataImporter

@app.route('/')
def index():
    """首页 - 显示最新周报"""
    return render_template('index.html')

@app.route('/history')
def history():
    """历史数据页面"""
    return render_template('history.html')

@app.route('/prediction')
def prediction():
    """数据预测页面"""
    return render_template('prediction.html')

# ==================== API接口 ====================

@app.route('/api/current-week-report')
def get_current_week_report():
    """获取当前周报告（上周完整数据）"""
    try:
        stats_service = StatisticsService()
        report = stats_service.generate_weekly_report()
        return jsonify({
            'success': True,
            'data': report
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/week-report')
def get_week_report():
    """获取指定周报告"""
    try:
        date_str = request.args.get('date')
        stats_service = StatisticsService()
        report = stats_service.generate_weekly_report(date_str)
        return jsonify({
            'success': True,
            'data': report
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/custom-range-report')
def get_custom_range_report():
    """获取自定义时间范围报告"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({
                'success': False,
                'error': '缺少起始日期或结束日期参数'
            }), 400
        
        stats_service = StatisticsService()
        report = stats_service.generate_custom_range_report(start_date, end_date)
        return jsonify({
            'success': True,
            'data': report
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/year-comparison-charts')
def get_year_comparison_charts():
    """获取年度对比折线图数据"""
    try:
        end_date = request.args.get('end_date')
        stats_service = StatisticsService()
        charts_data = stats_service.generate_year_comparison_charts(end_date)
        return jsonify({
            'success': True,
            'data': charts_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/prediction')
def get_prediction():
    """获取客流预测数据"""
    try:
        days = request.args.get('days', 7, type=int)
        stats_service = StatisticsService()
        prediction = stats_service.generate_prediction(days)
        return jsonify({
            'success': True,
            'data': prediction
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sync-data', methods=['POST'])
def sync_data():
    """手动触发数据同步"""
    try:
        downloader = DataDownloader()
        importer = DataImporter()
        
        # 下载数据
        csv_path = downloader.download_latest_data()
        
        # 导入数据
        new_records = importer.import_from_csv(csv_path)
        
        return jsonify({
            'success': True,
            'message': f'数据同步成功，新增 {new_records} 条记录',
            'csv_path': csv_path
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/available-weeks')
def get_available_weeks():
    """获取可用周列表"""
    try:
        stats_service = StatisticsService()
        weeks = stats_service.get_available_weeks()
        return jsonify({
            'success': True,
            'data': weeks
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
