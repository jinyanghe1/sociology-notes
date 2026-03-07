/**
 * 图表渲染组件
 * 封装 Plotly.js 提供交互式图表
 */

class ChartRenderer extends HTMLElement {
    constructor() {
        super();
        this.chartId = 'chart-' + Math.random().toString(36).substr(2, 9);
    }

    static get observedAttributes() {
        return ['type', 'data', 'config'];
    }

    connectedCallback() {
        this.type = this.getAttribute('type') || 'line';
        this.chartData = this.parseData(this.getAttribute('data'));
        this.config = this.parseConfig(this.getAttribute('config') || '{}');
        
        this.render();
        this.initChart();
    }

    render() {
        const height = this.getAttribute('height') || '400';
        
        this.innerHTML = `
            <div class="chart-container">
                <div class="chart-header">
                    <h4 class="chart-title">${this.getAttribute('title') || '图表'}</h4>
                    <div class="chart-actions">
                        <button class="btn-download" title="下载图片">💾</button>
                        <button class="btn-zoom" title="放大">🔍</button>
                    </div>
                </div>
                <div id="${this.chartId}" class="chart-plot" style="height: ${height}px;"></div>
            </div>
        `;
        
        this.querySelector('.btn-download').addEventListener('click', () => this.downloadImage());
        this.querySelector('.btn-zoom').addEventListener('click', () => this.toggleFullscreen());
    }

    initChart() {
        // 检查 Plotly 是否已加载
        if (typeof Plotly === 'undefined') {
            this.loadPlotly().then(() => this.drawChart());
        } else {
            this.drawChart();
        }
    }

    loadPlotly() {
        return new Promise((resolve) => {
            const script = document.createElement('script');
            script.src = 'https://cdn.plot.ly/plotly-2.27.0.min.js';
            script.onload = resolve;
            document.head.appendChild(script);
        });
    }

    drawChart() {
        const container = document.getElementById(this.chartId);
        if (!container) return;
        
        const trace = this.createTrace();
        const layout = this.createLayout();
        const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['lasso2d', 'select2d']
        };
        
        Plotly.newPlot(this.chartId, trace, layout, config);
    }

    createTrace() {
        const data = this.chartData;
        
        switch (this.type) {
            case 'line':
                return [{
                    x: data.x || [],
                    y: data.y || [],
                    mode: 'lines+markers',
                    type: 'scatter',
                    line: { color: '#3498db', width: 2 },
                    marker: { size: 8 }
                }];
                
            case 'bar':
                return [{
                    x: data.x || [],
                    y: data.y || [],
                    type: 'bar',
                    marker: { color: '#3498db' }
                }];
                
            case 'scatter':
                return [{
                    x: data.x || [],
                    y: data.y || [],
                    mode: 'markers',
                    type: 'scatter',
                    marker: {
                        size: data.size || 10,
                        color: data.color || '#3498db',
                        opacity: 0.7
                    }
                }];
                
            case 'histogram':
                return [{
                    x: data.x || [],
                    type: 'histogram',
                    nbinsx: data.bins || 30,
                    marker: { color: '#3498db' }
                }];
                
            case 'box':
                return [{
                    y: data.y || [],
                    type: 'box',
                    boxpoints: 'outliers',
                    marker: { color: '#3498db' }
                }];
                
            case 'network':
                // 使用散点图模拟网络图
                return this.createNetworkTrace(data);
                
            default:
                return [{
                    x: data.x || [],
                    y: data.y || [],
                    type: 'scatter'
                }];
        }
    }

    createNetworkTrace(data) {
        // 简化的网络图实现
        const nodes = data.nodes || [];
        const links = data.links || [];
        
        const nodeTrace = {
            x: nodes.map(n => n.x),
            y: nodes.map(n => n.y),
            mode: 'markers+text',
            type: 'scatter',
            text: nodes.map(n => n.name),
            textposition: 'top center',
            marker: {
                size: nodes.map(n => n.size || 20),
                color: nodes.map(n => n.color || '#3498db')
            }
        };
        
        // 绘制连线
        const edgeTraces = links.map(link => {
            const source = nodes[link.source];
            const target = nodes[link.target];
            return {
                x: [source.x, target.x],
                y: [source.y, target.y],
                mode: 'lines',
                type: 'scatter',
                line: { color: '#999', width: 1 },
                hoverinfo: 'none'
            };
        });
        
        return [...edgeTraces, nodeTrace];
    }

    createLayout() {
        const defaultLayout = {
            margin: { t: 40, r: 40, b: 60, l: 60 },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { family: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif' },
            xaxis: {
                gridcolor: '#e0e0e0',
                zerolinecolor: '#999'
            },
            yaxis: {
                gridcolor: '#e0e0e0',
                zerolinecolor: '#999'
            },
            hovermode: 'closest'
        };
        
        if (this.config.title) {
            defaultLayout.title = {
                text: this.config.title,
                font: { size: 16 }
            };
        }
        
        if (this.config.xaxis) {
            defaultLayout.xaxis = { ...defaultLayout.xaxis, ...this.config.xaxis };
        }
        if (this.config.yaxis) {
            defaultLayout.yaxis = { ...defaultLayout.yaxis, ...this.config.yaxis };
        }
        
        return defaultLayout;
    }

    updateData(newData) {
        this.chartData = this.parseData(newData);
        this.drawChart();
    }

    parseData(dataAttr) {
        if (!dataAttr) return {};
        try {
            return JSON.parse(dataAttr);
        } catch (e) {
            // 尝试解析简写格式 "x:1,2,3;y:4,5,6"
            const result = {};
            const parts = dataAttr.split(';');
            parts.forEach(part => {
                const [key, values] = part.split(':');
                if (key && values) {
                    result[key.trim()] = values.split(',').map(v => {
                        const num = parseFloat(v.trim());
                        return isNaN(num) ? v.trim() : num;
                    });
                }
            });
            return result;
        }
    }

    parseConfig(configAttr) {
        try {
            return JSON.parse(configAttr);
        } catch (e) {
            return {};
        }
    }

    downloadImage() {
        Plotly.downloadImage(this.chartId, {
            format: 'png',
            width: 1200,
            height: 800,
            filename: this.getAttribute('title') || 'chart'
        });
    }

    toggleFullscreen() {
        const container = this.querySelector('.chart-container');
        if (!document.fullscreenElement) {
            container.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }
}

customElements.define('chart-renderer', ChartRenderer);
