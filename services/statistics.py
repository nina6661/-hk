"""
统计计算服务
负责计算各种统计数据和生成报告
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
from database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StatisticsService:
    """统计计算服务"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def generate_weekly_report(self, date_str=None):
        """
        生成周报
        如果不指定日期，则生成上周的报告
        """
        try:
            # 确定目标周
            if date_str:
                target_date = datetime.strptime(date_str, '%Y-%m-%d')
            else:
                # 默认为上周
                target_date = datetime.now() - timedelta(days=7)
            
            # 获取该周的开始和结束日期（周一到周日）
            week_start, week_end = self._get_week_range(target_date)
            
            logger.info(f"生成周报: {week_start} 至 {week_end}")
            
            # 获取当前周和对比周的数据
            current_week_data = self._get_week_data(week_start, week_end)
            previous_week_start = week_start - timedelta(days=7)
            previous_week_end = week_end - timedelta(days=7)
            previous_week_data = self._get_week_data(previous_week_start, 
                                                     previous_week_end)
            
            # 获取去年同期数据
            last_year_week_start, last_year_week_end = \
                self._get_last_year_week_range(week_start, week_end)
            last_year_week_data = self._get_week_data(last_year_week_start, 
                                                      last_year_week_end)
            
            # 生成统计表格
            table_data = self._generate_statistics_table(
                current_week_data, previous_week_data, 
                last_year_week_data, week_start, week_end
            )
            
            # 生成汇报小抄
            summary_text = self._generate_summary_text(
                current_week_data, previous_week_data
            )
            
            # 组装完整报告
            report = {
                'week_start': week_start.strftime('%Y-%m-%d'),
                'week_end': week_end.strftime('%Y-%m-%d'),
                'year': week_start.year,
                'week_number': week_start.isocalendar()[1],
                'table': table_data,
                'summary': summary_text,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 保存到数据库
            self.db.save_weekly_report(
                report['year'],
                report['week_number'],
                report['week_start'],
                report['week_end'],
                report
            )
            
            return report
            
        except Exception as e:
            logger.error(f"生成周报失败: {str(e)}")
            raise Exception(f"生成周报失败: {str(e)}")
    
    def generate_custom_range_report(self, start_date, end_date):
        """生成自定义时间范围的报告"""
        try:
            logger.info(f"生成自定义范围报告: {start_date} 至 {end_date}")
            range_data = self._get_range_data(start_date, end_date)
            stats = self._calculate_range_statistics(range_data)
            
            report = {
                'start_date': start_date,
                'end_date': end_date,
                'statistics': stats,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            return report
        except Exception as e:
            logger.error(f"生成自定义范围报告失败: {str(e)}")
            raise Exception(f"生成自定义范围报告失败: {str(e)}")
    
    def generate_year_comparison_charts(self, end_date=None):
        """生成年度对比折线图数据"""
        try:
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            current_year = datetime.strptime(end_date, '%Y-%m-%d').year
            last_year = current_year - 1
            
            # 获取去年全年数据
            last_year_start = f"{last_year}-01-01"
            last_year_end = f"{last_year}-12-31"
            last_year_data = self._get_range_data(last_year_start, last_year_end)
            
            # 获取今年数据
            current_year_start = f"{current_year}-01-01"
            current_year_data = self._get_range_data(current_year_start, end_date)
            
            # 生成对比图数据
            inbound_chart = self._prepare_chart_data(last_year_data, current_year_data, 'inbound')
            outbound_chart = self._prepare_chart_data(last_year_data, current_year_data, 'outbound')
            
            return {
                'inbound': inbound_chart,
                'outbound': outbound_chart,
                'current_year': current_year,
                'last_year': last_year,
                'end_date': end_date
            }
        except Exception as e:
            logger.error(f"生成年度对比图失败: {str(e)}")
            raise Exception(f"生成年度对比图失败: {str(e)}")
    
    def generate_prediction(self, days=7):
        """生成客流预测（简单移动平均法）"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            recent_data = self._get_range_data(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            prediction = self._calculate_prediction(recent_data, days)
            return prediction
        except Exception as e:
            logger.error(f"生成预测失败: {str(e)}")
            raise Exception(f"生成预测失败: {str(e)}")
    
    def get_available_weeks(self):
        """获取可用的周列表"""
        try:
            date_range = self.db.get_date_range()
            if not date_range['min_date'] or not date_range['max_date']:
                return []
            
            min_date = datetime.strptime(date_range['min_date'], '%Y-%m-%d')
            max_date = datetime.strptime(date_range['max_date'], '%Y-%m-%d')
            
            weeks = []
            current = min_date
            while current <= max_date:
                week_start, week_end = self._get_week_range(current)
                week_number = week_start.isocalendar()[1]
                
                weeks.append({
                    'year': week_start.year,
                    'week_number': week_number,
                    'start_date': week_start.strftime('%Y-%m-%d'),
                    'end_date': week_end.strftime('%Y-%m-%d'),
                    'label': f"{week_start.year}年 第{week_number}周 ({week_start.strftime('%m/%d')}-{week_end.strftime('%m/%d')})"
                })
                
                current = week_end + timedelta(days=1)
            
            weeks.sort(key=lambda x: (x['year'], x['week_number']), reverse=True)
            return weeks
        except Exception as e:
            logger.error(f"获取可用周列表失败: {str(e)}")
            return []
    
    # 私有辅助方法
    def _get_week_range(self, date):
        """获取指定日期所在周的范围（周一到周日）"""
        weekday = date.weekday()
        week_start = date - timedelta(days=weekday)
        week_end = week_start + timedelta(days=6)
        return week_start, week_end
    
    def _get_last_year_week_range(self, week_start, week_end):
        """获取去年同期的周范围（ISO周对齐）"""
        iso_year, iso_week, _ = week_start.isocalendar()
        last_year = iso_year - 1
        
        jan4 = datetime(last_year, 1, 4)
        week1_monday = jan4 - timedelta(days=jan4.weekday())
        target_monday = week1_monday + timedelta(weeks=iso_week-1)
        target_sunday = target_monday + timedelta(days=6)
        
        return target_monday, target_sunday
    
    def _get_week_data(self, week_start, week_end):
        """获取一周的数据"""
        start_str = week_start.strftime('%Y-%m-%d')
        end_str = week_end.strftime('%Y-%m-%d')
        
        raw_data = self.db.get_daily_stats_by_range(start_str, end_str)
        
        aggregated = {}
        for record in raw_data:
            date = record['date']
            if date not in aggregated:
                aggregated[date] = {
                    'inbound': {'hk': 0, 'mainland': 0, 'other': 0, 'total': 0},
                    'outbound': {'hk': 0, 'mainland': 0, 'other': 0, 'total': 0}
                }
            
            direction = 'inbound' if '入境' in record['direction'] else 'outbound'
            aggregated[date][direction]['hk'] += record['hk_residents']
            aggregated[date][direction]['mainland'] += record['mainland_visitors']
            aggregated[date][direction]['other'] += record['other_visitors']
            aggregated[date][direction]['total'] += record['total']
        
        return aggregated
    
    def _get_range_data(self, start_date, end_date):
        """获取时间范围内的数据"""
        raw_data = self.db.get_daily_stats_by_range(start_date, end_date)
        
        aggregated = {}
        for record in raw_data:
            date = record['date']
            if date not in aggregated:
                aggregated[date] = {
                    'inbound': {'hk': 0, 'mainland': 0, 'other': 0, 'total': 0},
                    'outbound': {'hk': 0, 'mainland': 0, 'other': 0, 'total': 0}
                }
            
            direction = 'inbound' if '入境' in record['direction'] else 'outbound'
            aggregated[date][direction]['hk'] += record['hk_residents']
            aggregated[date][direction]['mainland'] += record['mainland_visitors']
            aggregated[date][direction]['other'] += record['other_visitors']
            aggregated[date][direction]['total'] += record['total']
        
        return aggregated
    
    def _generate_statistics_table(self, current_week, previous_week, 
                                   last_year_week, week_start, week_end):
        """生成统计表格数据"""
        current_stats = self._calculate_weekly_stats(current_week, previous_week)
        last_year_stats = self._calculate_weekly_stats(last_year_week, None)
        
        table = {
            'current_week': {
                'start_date': week_start.strftime('%Y-%m-%d'),
                'end_date': week_end.strftime('%Y-%m-%d'),
                'data': current_stats
            },
            'last_year_week': last_year_stats,
            'dates': self._get_week_dates(week_start)
        }
        
        return table
    
    def _calculate_weekly_stats(self, week_data, previous_week_data):
        """计算一周的统计数据"""
        if not week_data:
            return None
        
        days_count = len(week_data)
        
        # 入境统计
        inbound_total = sum(day['inbound']['total'] for day in week_data.values())
        inbound_hk = sum(day['inbound']['hk'] for day in week_data.values())
        inbound_mainland = sum(day['inbound']['mainland'] for day in week_data.values())
        inbound_other = sum(day['inbound']['other'] for day in week_data.values())
        
        # 出境统计
        outbound_total = sum(day['outbound']['total'] for day in week_data.values())
        outbound_hk = sum(day['outbound']['hk'] for day in week_data.values())
        outbound_mainland = sum(day['outbound']['mainland'] for day in week_data.values())
        outbound_other = sum(day['outbound']['other'] for day in week_data.values())
        
        stats = {
            'inbound': {
                'total_daily_avg': inbound_total / days_count / 10000,
                'hk_daily_avg': inbound_hk / days_count / 10000,
                'mainland_daily_avg': inbound_mainland / days_count / 10000,
                'other_daily_avg': inbound_other / days_count / 10000,
                'daily_data': []
            },
            'outbound': {
                'total_daily_avg': outbound_total / days_count / 10000,
                'hk_daily_avg': outbound_hk / days_count / 10000,
                'mainland_daily_avg': outbound_mainland / days_count / 10000,
                'other_daily_avg': outbound_other / days_count / 10000,
                'daily_data': []
            }
        }
        
        # 添加每日数据
        for date in sorted(week_data.keys()):
            day = week_data[date]
            stats['inbound']['daily_data'].append({
                'date': date,
                'total': day['inbound']['total'] / 10000
            })
            stats['outbound']['daily_data'].append({
                'date': date,
                'total': day['outbound']['total'] / 10000
            })
        
        # 计算环比
        if previous_week_data:
            prev_days_count = len(previous_week_data)
            
            prev_inbound_total = sum(day['inbound']['total'] for day in previous_week_data.values())
            prev_outbound_total = sum(day['outbound']['total'] for day in previous_week_data.values())
            prev_inbound_hk = sum(day['inbound']['hk'] for day in previous_week_data.values())
            prev_outbound_hk = sum(day['outbound']['hk'] for day in previous_week_data.values())
            prev_inbound_mainland = sum(day['inbound']['mainland'] for day in previous_week_data.values())
            prev_outbound_mainland = sum(day['outbound']['mainland'] for day in previous_week_data.values())
            
            stats['inbound']['total_weekly_change'] = self._calculate_change_rate(
                inbound_total / days_count, prev_inbound_total / prev_days_count)
            stats['inbound']['hk_weekly_change'] = self._calculate_change_rate(
                inbound_hk / days_count, prev_inbound_hk / prev_days_count)
            stats['inbound']['mainland_weekly_change'] = self._calculate_change_rate(
                inbound_mainland / days_count, prev_inbound_mainland / prev_days_count)
            
            stats['outbound']['total_weekly_change'] = self._calculate_change_rate(
                outbound_total / days_count, prev_outbound_total / prev_days_count)
            stats['outbound']['hk_weekly_change'] = self._calculate_change_rate(
                outbound_hk / days_count, prev_outbound_hk / prev_days_count)
            stats['outbound']['mainland_weekly_change'] = self._calculate_change_rate(
                outbound_mainland / days_count, prev_outbound_mainland / prev_days_count)
        
        return stats
    
    def _calculate_change_rate(self, current, previous):
        """计算变化率"""
        if previous == 0:
            return 0
        return (current - previous) / previous * 100
    
    def _get_week_dates(self, week_start):
        """获取一周的日期列表"""
        dates = []
        for i in range(7):
            date = week_start + timedelta(days=i)
            dates.append(date.strftime('%Y-%m-%d'))
        return dates
    
    def _generate_summary_text(self, current_week, previous_week):
        """生成汇报小抄"""
        if not current_week:
            return ""
        
        current_stats = self._calculate_weekly_stats(current_week, previous_week)
        
        if not current_stats:
            return ""
        
        # 提取数据
        inbound_avg = current_stats['inbound']['total_daily_avg']
        outbound_avg = current_stats['outbound']['total_daily_avg']
        total_avg = inbound_avg + outbound_avg
        
        inbound_change = current_stats['inbound'].get('total_weekly_change', 0)
        outbound_change = current_stats['outbound'].get('total_weekly_change', 0)
        
        hk_inbound_avg = current_stats['inbound']['hk_daily_avg']
        hk_inbound_change = current_stats['inbound'].get('hk_weekly_change', 0)
        mainland_inbound_avg = current_stats['inbound']['mainland_daily_avg']
        mainland_inbound_change = current_stats['inbound'].get('mainland_weekly_change', 0)
        
        hk_outbound_avg = current_stats['outbound']['hk_daily_avg']
        hk_outbound_change = current_stats['outbound'].get('hk_weekly_change', 0)
        mainland_outbound_avg = current_stats['outbound']['mainland_daily_avg']
        mainland_outbound_change = current_stats['outbound'].get('mainland_weekly_change', 0)
        
        # 生成文本
        trend = "上升" if inbound_change + outbound_change > 0 else "下降"
        
        summary = f"""出入境日均是 {total_avg:.1f} 万，整体{trend}

一、入境（上周日均 {inbound_avg:.1f} 万，{self._format_change(inbound_change)}）
港人南下：{hk_inbound_avg:.1f} 万，周环比 {self._format_change(hk_inbound_change)}
内地旅客南下：{mainland_inbound_avg:.1f} 万，周环比 {self._format_change(mainland_inbound_change)}

二、出境（上周日均 {outbound_avg:.1f} 万，周环比 {self._format_change(outbound_change)}）
港人北上：{hk_outbound_avg:.1f} 万，周环比 {self._format_change(hk_outbound_change)}
内地旅客北上：{mainland_outbound_avg:.1f} 万，周环比 {self._format_change(mainland_outbound_change)}"""
        
        return summary
    
    def _format_change(self, change):
        """格式化变化率"""
        if change > 0:
            return f"+{change:.2f}%"
        else:
            return f"{change:.2f}%"
    
    def _calculate_range_statistics(self, range_data):
        """计算时间范围统计"""
        if not range_data:
            return None
        
        days_count = len(range_data)
        
        inbound_total = sum(day['inbound']['total'] for day in range_data.values())
        outbound_total = sum(day['outbound']['total'] for day in range_data.values())
        
        return {
            'days_count': days_count,
            'inbound_total': inbound_total,
            'outbound_total': outbound_total,
            'inbound_daily_avg': inbound_total / days_count / 10000,
            'outbound_daily_avg': outbound_total / days_count / 10000
        }
    
    def _prepare_chart_data(self, last_year_data, current_year_data, direction):
        """准备图表数据"""
        chart_data = {
            'last_year': [],
            'current_year': []
        }
        
        # 去年数据
        for date in sorted(last_year_data.keys()):
            day = last_year_data[date]
            chart_data['last_year'].append({
                'date': date,
                'hk': day[direction]['hk'] / 10000,
                'mainland': day[direction]['mainland'] / 10000,
                'total': day[direction]['total'] / 10000
            })
        
        # 今年数据
        for date in sorted(current_year_data.keys()):
            day = current_year_data[date]
            chart_data['current_year'].append({
                'date': date,
                'hk': day[direction]['hk'] / 10000,
                'mainland': day[direction]['mainland'] / 10000,
                'total': day[direction]['total'] / 10000
            })
        
        return chart_data
    
    def _calculate_prediction(self, recent_data, days):
        """计算预测数据（简单移动平均）"""
        if not recent_data:
            return None
        
        # 计算最近7天的平均值作为预测基础
        recent_dates = sorted(recent_data.keys())[-7:]
        
        avg_inbound = sum(recent_data[d]['inbound']['total'] for d in recent_dates) / 7 / 10000
        avg_outbound = sum(recent_data[d]['outbound']['total'] for d in recent_dates) / 7 / 10000
        
        # 生成未来days天的预测
        predictions = []
        last_date = datetime.strptime(recent_dates[-1], '%Y-%m-%d')
        
        for i in range(1, days + 1):
            pred_date = last_date + timedelta(days=i)
            predictions.append({
                'date': pred_date.strftime('%Y-%m-%d'),
                'inbound': round(avg_inbound, 1),
                'outbound': round(avg_outbound, 1)
            })
        
        return {
            'predictions': predictions,
            'based_on': f"最近7天平均值",
            'avg_inbound': round(avg_inbound, 1),
            'avg_outbound': round(avg_outbound, 1)
        }
