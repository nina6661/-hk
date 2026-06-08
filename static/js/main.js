// API基础路径
const API_BASE = '';

// 工具函数
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
}

function formatNumber(num) {
    return num.toFixed(1);
}

function formatPercent(num) {
    const sign = num > 0 ? '+' : '';
    return `${sign}${num.toFixed(2)}%`;
}

function getColorClass(num) {
    if (num > 0) return 'positive';
    if (num < 0) return 'negative';
    return 'neutral';
}

// 加载当前周报告
async function loadCurrentWeekReport() {
    try {
        const response = await fetch(`${API_BASE}/api/current-week-report`);
        const result = await response.json();
        
        if (result.success) {
            displayReport(result.data);
        } else {
            showError('table-container', result.error);
        }
    } catch (error) {
        showError('table-container', '加载失败: ' + error.message);
    }
}

// 加载年度对比图
async function loadYearComparisonCharts() {
    try {
        const response = await fetch(`${API_BASE}/api/year-comparison-charts`);
        const result = await response.json();
        
        if (result.success) {
            renderCharts(result.data);
        } else {
            console.error('加载图表失败:', result.error);
        }
    } catch (error) {
        console.error('加载图表失败:', error);
    }
}

// 显示报告
function displayReport(report) {
    // 更新标题
    document.getElementById('report-title').textContent = 
        `${report.year}年 第${report.week_number}周出入境数据报告`;
    
    document.getElementById('report-meta').textContent = 
        `统计周期：${report.week_start} 至 ${report.week_end} | 生成时间：${report.generated_at}`;
    
    // 显示统计表格
    displayTable(report.table);
    
    // 显示小抄
    displaySummary(report.summary);
    
    // 更新时间
    document.getElementById('update-time').textContent = report.generated_at;
}

// 显示统计表格
function displayTable(tableData) {
    const container = document.getElementById('table-container');
    
    if (!tableData || !tableData.current_week) {
        container.innerHTML = '<div class="error">暂无数据</div>';
        return;
    }
    
    const current = tableData.current_week.data;
    const lastYear = tableData.last_year_week;
    
    if (!current) {
        container.innerHTML = '<div class="error">暂无数据</div>';
        return;
    }
    
    let html = '<table>';
    
    // 表头
    html += '<thead><tr>';
    html += '<th>类别</th>';
    html += '<th>上周日均(万)</th>';
    html += '<th>周对比</th>';
    
    tableData.dates.forEach(date => {
        html += `<th>${formatDate(date)}</th>`;
    });
    
    html += '</tr></thead>';
    
    // 上层：当年数据
    html += '<tbody>';
    html += generateTableRows(current, 'inbound');
    html += generateTableRows(current, 'outbound');
    
    // 下层：去年数据
    if (lastYear) {
        html += '<tr style="height: 20px; background: white;"><td colspan="11"></td></tr>';
        html += generateTableRows(lastYear, 'inbound', true);
        html += generateTableRows(lastYear, 'outbound', true);
    }
    
    html += '</tbody></table>';
    
    container.innerHTML = html;
}

// 生成表格行
function generateTableRows(data, direction, isLastYear = false) {
    const labels = {
        inbound: {
            hk: '港人南下',
            mainland: '内地旅客南下',
            other: '外国旅客入境',
            total: '入境合计'
        },
        outbound: {
            hk: '港人北上',
            mainland: '内地旅客北上',
            other: '外国旅客出境',
            total: '出境合计'
        }
    };
    
    const dirData = data[direction];
    if (!dirData) return '';
    
    let html = '';
    const categories = ['hk', 'mainland', 'other', 'total'];
    
    categories.forEach(cat => {
        const isTotal = cat === 'total';
        const label = labels[direction][cat];
        
        html += `<tr${isTotal ? ' class="total-row"' : ''}>`;
        html += `<td>${label}</td>`;
        
        // 日均
        const avgKey = cat === 'total' ? 'total_daily_avg' : `${cat}_daily_avg`;
        html += `<td>${formatNumber(dirData[avgKey])}</td>`;
        
        // 周对比
        const changeKey = cat === 'total' ? 'total_weekly_change' : `${cat}_weekly_change`;
        const change = dirData[changeKey] || 0;
        html += `<td class="${getColorClass(change)}">${formatPercent(change)}</td>`;
        
        // 每日数据
        if (dirData.daily_data && !isLastYear) {
            dirData.daily_data.forEach(day => {
                html += `<td>${formatNumber(day.total)}</td>`;
            });
        }
        
        html += '</tr>';
    });
    
    return html;
}

// 显示小抄
function displaySummary(summary) {
    const container = document.getElementById('summary-container');
    container.textContent = summary || '暂无数据';
}

// 渲染图表
function renderCharts(chartData) {
    renderInboundChart(chartData.inbound, chartData.current_year, chartData.last_year);
    renderOutboundChart(chartData.outbound, chartData.current_year, chartData.last_year);
}

// 渲染入境图表
function renderInboundChart(data, currentYear, lastYear) {
    const chart = echarts.init(document.getElementById('inbound-chart'));
    
    const option = {
        title: {
            text: '入境情况年度对比',
            subtext: `港人-蓝色、旅客-绿色、总人数-红色 | ${lastYear}实线、${currentYear}虚线`,
            left: 'center',
            textStyle: { fontSize: 14 }
        },
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                let result = params[0].axisValue + '<br/>';
                params.forEach(param => {
                    result += `${param.marker}${param.seriesName}: ${param.value}万<br/>`;
                });
                return result;
            }
        },
        legend: {
            bottom: 10,
            data: [
                `港人(${lastYear})`, `旅客(${lastYear})`, `总人数(${lastYear})`,
                `港人(${currentYear})`, `旅客(${currentYear})`, `总人数(${currentYear})`
            ]
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: data.last_year.map(d => d.date),
            axisLabel: { formatter: formatDate }
        },
        yAxis: {
            type: 'value',
            name: '万人次',
            max: 80,
            interval: 10
        },
        series: [
            {
                name: `港人(${lastYear})`,
                type: 'line',
                data: data.last_year.map(d => d.hk),
                smooth: true,
                lineStyle: { color: '#3498db', width: 2 },
                itemStyle: { color: '#3498db' }
            },
            {
                name: `旅客(${lastYear})`,
                type: 'line',
                data: data.last_year.map(d => d.mainland),
                smooth: true,
                lineStyle: { color: '#2ecc71', width: 2 },
                itemStyle: { color: '#2ecc71' }
            },
            {
                name: `总人数(${lastYear})`,
                type: 'line',
                data: data.last_year.map(d => d.total),
                smooth: true,
                lineStyle: { color: '#e74c3c', width: 2 },
                itemStyle: { color: '#e74c3c' }
            },
            {
                name: `港人(${currentYear})`,
                type: 'line',
                data: data.current_year.map(d => d.hk),
                smooth: true,
                lineStyle: { color: '#3498db', width: 2, type: 'dashed' },
                itemStyle: { color: '#3498db' }
            },
            {
                name: `旅客(${currentYear})`,
                type: 'line',
                data: data.current_year.map(d => d.mainland),
                smooth: true,
                lineStyle: { color: '#2ecc71', width: 2, type: 'dashed' },
                itemStyle: { color: '#2ecc71' }
            },
            {
                name: `总人数(${currentYear})`,
                type: 'line',
                data: data.current_year.map(d => d.total),
                smooth: true,
                lineStyle: { color: '#e74c3c', width: 2, type: 'dashed' },
                itemStyle: { color: '#e74c3c' }
            }
        ]
    };
    
    chart.setOption(option);
}

// 渲染出境图表
function renderOutboundChart(data, currentYear, lastYear) {
    const chart = echarts.init(document.getElementById('outbound-chart'));
    
    const option = {
        title: {
            text: '出境情况年度对比',
            subtext: `港人-蓝色、旅客-绿色、总人数-红色 | ${lastYear}实线、${currentYear}虚线`,
            left: 'center',
            textStyle: { fontSize: 14 }
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            bottom: 10,
            data: [
                `港人(${lastYear})`, `旅客(${lastYear})`, `总人数(${lastYear})`,
                `港人(${currentYear})`, `旅客(${currentYear})`, `总人数(${currentYear})`
            ]
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: data.last_year.map(d => d.date),
            axisLabel: { formatter: formatDate }
        },
        yAxis: {
            type: 'value',
            name: '万人次',
            max: 80,
            interval: 10
        },
        series: [
            {
                name: `港人(${lastYear})`,
                type: 'line',
                data: data.last_year.map(d => d.hk),
                smooth: true,
                lineStyle: { color: '#3498db', width: 2 },
                itemStyle: { color: '#3498db' }
            },
            {
                name: `旅客(${lastYear})`,
                type: 'line',
                data: data.last_year.map(d => d.mainland),
                smooth: true,
                lineStyle: { color: '#2ecc71', width: 2 },
                itemStyle: { color: '#2ecc71' }
            },
            {
                name: `总人数(${lastYear})`,
                type: 'line',
                data: data.last_year.map(d => d.total),
                smooth: true,
                lineStyle: { color: '#e74c3c', width: 2 },
                itemStyle: { color: '#e74c3c' }
            },
            {
                name: `港人(${currentYear})`,
                type: 'line',
                data: data.current_year.map(d => d.hk),
                smooth: true,
                lineStyle: { color: '#3498db', width: 2, type: 'dashed' },
                itemStyle: { color: '#3498db' }
            },
            {
                name: `旅客(${currentYear})`,
                type: 'line',
                data: data.current_year.map(d => d.mainland),
                smooth: true,
                lineStyle: { color: '#2ecc71', width: 2, type: 'dashed' },
                itemStyle: { color: '#2ecc71' }
            },
            {
                name: `总人数(${currentYear})`,
                type: 'line',
                data: data.current_year.map(d => d.total),
                smooth: true,
                lineStyle: { color: '#e74c3c', width: 2, type: 'dashed' },
                itemStyle: { color: '#e74c3c' }
            }
        ]
    };
    
    chart.setOption(option);
}

// 历史查询 - 按周查询
async function queryByWeek() {
    const dateInput = document.getElementById('week-picker');
    const date = dateInput.value;
    
    if (!date) {
        alert('请选择日期');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/week-report?date=${date}`);
        const result = await response.json();
        
        if (result.success) {
            document.getElementById('result-section').style.display = 'block';
            displayReport(result.data);
        } else {
            alert('查询失败: ' + result.error);
        }
    } catch (error) {
        alert('查询失败: ' + error.message);
    }
}

// 历史查询 - 自定义范围
async function queryByRange() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    
    if (!startDate || !endDate) {
        alert('请选择起始和结束日期');
        return;
    }
    
    try {
        const response = await fetch(
            `${API_BASE}/api/custom-range-report?start_date=${startDate}&end_date=${endDate}`
        );
        const result = await response.json();
        
        if (result.success) {
            document.getElementById('result-section').style.display = 'block';
            displayCustomRangeReport(result.data);
        } else {
            alert('查询失败: ' + result.error);
        }
    } catch (error) {
        alert('查询失败: ' + error.message);
    }
}

// 显示自定义范围报告
function displayCustomRangeReport(report) {
    document.getElementById('result-title').textContent = 
        `自定义范围数据报告 (${report.start_date} 至 ${report.end_date})`;
    
    document.getElementById('result-meta').textContent = 
        `统计天数：${report.statistics.days_count}天 | 生成时间：${report.generated_at}`;
    
    const stats = report.statistics;
    let html = `
        <table>
            <thead>
                <tr>
                    <th>指标</th>
                    <th>数值</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>统计天数</td><td>${stats.days_count}</td></tr>
                <tr><td>入境总数</td><td>${stats.inbound_total.toLocaleString()}</td></tr>
                <tr><td>出境总数</td><td>${stats.outbound_total.toLocaleString()}</td></tr>
                <tr><td>入境日均(万)</td><td>${formatNumber(stats.inbound_daily_avg)}</td></tr>
                <tr><td>出境日均(万)</td><td>${formatNumber(stats.outbound_daily_avg)}</td></tr>
            </tbody>
        </table>
    `;
    
    document.getElementById('history-table-container').innerHTML = html;
    document.getElementById('history-summary').textContent = 
        `统计期间：${report.start_date} 至 ${report.end_date}，共 ${stats.days_count} 天\n` +
        `入境日均 ${formatNumber(stats.inbound_daily_avg)} 万人次\n` +
        `出境日均 ${formatNumber(stats.outbound_daily_avg)} 万人次`;
}

// 加载预测数据
async function loadPrediction() {
    const days = document.getElementById('predict-days').value;
    
    try {
        const response = await fetch(`${API_BASE}/api/prediction?days=${days}`);
        const result = await response.json();
        
        if (result.success) {
            displayPrediction(result.data);
        } else {
            document.getElementById('prediction-result').innerHTML = 
                `<div class="error">预测失败: ${result.error}</div>`;
        }
    } catch (error) {
        document.getElementById('prediction-result').innerHTML = 
            `<div class="error">预测失败: ${error.message}</div>`;
    }
}

// 显示预测结果
function displayPrediction(prediction) {
    if (!prediction) {
        document.getElementById('prediction-result').innerHTML = '<div class="error">暂无数据</div>';
        return;
    }
    
    let html = `
        <h4>预测说明</h4>
        <p>基于${prediction.based_on}进行预测</p>
        <p>平均入境：${prediction.avg_inbound} 万 | 平均出境：${prediction.avg_outbound} 万</p>
        
        <h4 style="margin-top: 20px;">预测详情</h4>
        <table>
            <thead>
                <tr>
                    <th>日期</th>
                    <th>入境预测(万)</th>
                    <th>出境预测(万)</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    prediction.predictions.forEach(pred => {
        html += `
            <tr>
                <td>${pred.date}</td>
                <td>${pred.inbound}</td>
                <td>${pred.outbound}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    
    document.getElementById('prediction-result').innerHTML = html;
    
    // 渲染预测图表
    renderPredictionCharts(prediction);
}

// 渲染预测图表
function renderPredictionCharts(prediction) {
    const dates = prediction.predictions.map(p => p.date);
    const inbound = prediction.predictions.map(p => p.inbound);
    const outbound = prediction.predictions.map(p => p.outbound);
    
    // 入境预测图
    const inboundChart = echarts.init(document.getElementById('predict-inbound-chart'));
    inboundChart.setOption({
        title: { text: '入境客流预测', left: 'center', textStyle: { fontSize: 14 } },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: dates, axisLabel: { formatter: formatDate } },
        yAxis: { type: 'value', name: '万人次' },
        series: [{
            type: 'line',
            data: inbound,
            smooth: true,
            lineStyle: { color: '#3498db', width: 2 },
            itemStyle: { color: '#3498db' },
            areaStyle: { color: 'rgba(52, 152, 219, 0.1)' }
        }]
    });
    
    // 出境预测图
    const outboundChart = echarts.init(document.getElementById('predict-outbound-chart'));
    outboundChart.setOption({
        title: { text: '出境客流预测', left: 'center', textStyle: { fontSize: 14 } },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: dates, axisLabel: { formatter: formatDate } },
        yAxis: { type: 'value', name: '万人次' },
        series: [{
            type: 'line',
            data: outbound,
            smooth: true,
            lineStyle: { color: '#e74c3c', width: 2 },
            itemStyle: { color: '#e74c3c' },
            areaStyle: { color: 'rgba(231, 76, 60, 0.1)' }
        }]
    });
}

// 显示错误
function showError(containerId, message) {
    document.getElementById(containerId).innerHTML = 
        `<div class="error">错误: ${message}</div>`;
}

// 响应式图表
window.addEventListener('resize', function() {
    const charts = ['inbound-chart', 'outbound-chart', 
                   'history-inbound-chart', 'history-outbound-chart',
                   'predict-inbound-chart', 'predict-outbound-chart'];
    
    charts.forEach(chartId => {
        const chartDom = document.getElementById(chartId);
        if (chartDom) {
            const chartInstance = echarts.getInstanceByDom(chartDom);
            if (chartInstance) {
                chartInstance.resize();
            }
        }
    });
});
