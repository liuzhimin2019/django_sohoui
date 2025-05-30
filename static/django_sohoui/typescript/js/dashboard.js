// 折线图示例
var lineChart = echarts.init(document.getElementById('line-chart'));
lineChart.setOption({
    title: { text: '折线图示例' },
    tooltip: {},
    xAxis: {
        data: ['一月', '二月', '三月', '四月', '五月', '六月']
    },
    yAxis: {},
    series: [{
        name: '销售额',
        type: 'line',
        data: [5, 20, 36, 10, 10, 20]
    }]
});

// 柱状图示例
var barChart = echarts.init(document.getElementById('bar-chart'));
barChart.setOption({
    title: { text: '柱状图示例' },
    tooltip: {},
    xAxis: {
        data: ['一月', '二月', '三月', '四月', '五月', '六月']
    },
    yAxis: {},
    series: [{
        name: '销售额',
        type: 'bar',
        data: [5, 20, 36, 10, 10, 20]
    }]
});

// 饼图示例
var pieChart = echarts.init(document.getElementById('pie-chart'));
pieChart.setOption({
    title: { text: '饼图示例', subtext: '销售分布', left: 'center' },
    tooltip: { trigger: 'item' },
    series: [{
        name: '销售额',
        type: 'pie',
        radius: '50%',
        data: [
            { value: 335, name: '直接访问' },
            { value: 310, name: '邮件营销' },
            { value: 234, name: '联盟广告' },
            { value: 135, name: '视频广告' },
            { value: 1548, name: '搜索引擎' }
        ],
        emphasis: {
            itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
        }
    }]
});

// 地图示例（这里使用简单的示例，实际地图需要更多配置）
var mapChart = echarts.init(document.getElementById('map-chart'));
mapChart.setOption({
    title: { text: '地图示例' },
    tooltip: {},
    series: [{
        type: 'map',
        map: 'world', // 这里需要确保有相应的地图数据
        roam: true,
        data: [
            { name: '中国', value: 100 },
            { name: '美国', value: 80 },
            { name: '巴西', value: 60 },
            { name: '俄罗斯', value: 50 },
            { name: '印度', value: 40 }
        ]
    }]
});