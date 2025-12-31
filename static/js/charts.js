document.addEventListener('DOMContentLoaded', () => {
    // Theme Colors
    const colors = {
        bg: '#0a0a0a',
        primary: '#00f3ff',
        secondary: '#bd00ff',
        text: '#ededed',
        textMuted: '#888888',
        grid: '#222'
    };

    // Chart 1: Disk Footprint (Bar)
    const chartDisk = echarts.init(document.getElementById('chart-disk'));
    chartDisk.setOption({
        title: { text: 'Disk Footprint (MB)', textStyle: { color: colors.textMuted, fontSize: 12 } },
        tooltip: { trigger: 'axis' },
        grid: { top: 30, bottom: 20, left: 50, right: 20 },
        xAxis: { type: 'category', data: ['bge-small-v1.5', 'bge-optimised'], axisLine: { lineStyle: { color: colors.grid } }, axisLabel: { color: colors.textMuted } },
        yAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: colors.grid } }, axisLabel: { color: colors.textMuted } },
        series: [{
            data: [
                { value: 133.00, itemStyle: { color: '#333' } },  // Baseline
                { value: 33.33, itemStyle: { color: colors.primary } } // Optimized
            ],
            type: 'bar',
            barWidth: '40%',
            label: { show: true, position: 'top', color: colors.text }
        }]
    });

    // Chart 2: Generative Disk Footprint (Bar - Replaces Latency)
    const chartLatency = echarts.init(document.getElementById('chart-latency'));
    chartLatency.setOption({
        title: { text: 'Disk Footprint (GB)', textStyle: { color: colors.textMuted, fontSize: 12 } },
        tooltip: { trigger: 'axis' },
        grid: { top: 30, bottom: 20, left: 50, right: 20 },
        xAxis: { type: 'category', data: ['Qwen 2.5', 'Qwen Optimized'], axisLine: { lineStyle: { color: colors.grid } }, axisLabel: { color: colors.textMuted } },
        yAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: colors.grid } }, axisLabel: { color: colors.textMuted } },
        series: [{
            data: [
                { value: 4.00, itemStyle: { color: '#333' }, name: 'Baseline (4GB)' },  // Baseline
                { value: 0.94, itemStyle: { color: colors.secondary }, name: 'Optimized (940MB)' } // Optimized
            ],
            type: 'bar',
            barWidth: '40%',
            label: { show: true, position: 'top', color: colors.text }
        }]
    });

    // Resize Observer
    window.addEventListener('resize', () => {
        chartDisk.resize();
        chartLatency.resize();
    });
});
