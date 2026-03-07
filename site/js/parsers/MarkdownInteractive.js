/**
 * 交互式 Markdown 扩展语法解析器
 * 将自定义语法转换为可运行的 Web Components
 */

class MarkdownInteractive {
    constructor() {
        this.patterns = {
            // 可运行代码块
            pythonRunnable: /```python-runnable\s*(?:\{([^}]+)\})?\n([\s\S]*?)```/g,
            
            // 参数滑块
            slider: /@slider\[(\w+)\]\s*\(([^)]+)\)/g,
            
            // 图表
            chart: /@chart\[(\w+)\]\s*\(([^)]*)\)/g,
            
            // 交互式表格
            table: /@table\[([^\]]+)\]\s*\(([^)]*)\)/g,
            
            // 信息图
            infographic: /@infographic\[(\w+)\]\s*\(([^)]*)\)\n([\s\S]*?)@end/g,
            
            // 对比视图
            compare: /@compare\[([^\]]*)\]\n([\s\S]*?)@end/g,
            
            // 变量插值 {{slider.name}}
            interpolation: /\{\{\s*slider\.(\w+)\s*\}\}/g
        };
    }

    /**
     * 解析完整的 Markdown 文本
     */
    parse(markdown) {
        let html = markdown;
        
        // 按顺序解析各种语法
        html = this.parsePythonRunnable(html);
        html = this.parseSliders(html);
        html = this.parseCharts(html);
        html = this.parseTables(html);
        html = this.parseInfographics(html);
        html = this.parseCompare(html);
        
        return html;
    }

    /**
     * 解析可运行 Python 代码块
     */
    parsePythonRunnable(text) {
        return text.replace(this.patterns.pythonRunnable, (match, attrs, code) => {
            const attrObj = this.parseAttributes(attrs);
            const height = attrObj.height || '200';
            const packages = attrObj.packages || '';
            
            // 转义代码中的 HTML 特殊字符
            const escapedCode = this.escapeHtml(code.trim());
            
            return `<code-runner height="${height}" packages="${packages}">${escapedCode}</code-runner>`;
        });
    }

    /**
     * 解析参数滑块
     */
    parseSliders(text) {
        return text.replace(this.patterns.slider, (match, name, params) => {
            const attrObj = this.parseAttributes(params);
            
            const label = attrObj.label || name;
            const min = attrObj.min !== undefined ? attrObj.min : 0;
            const max = attrObj.max !== undefined ? attrObj.max : 100;
            const value = attrObj.value !== undefined ? attrObj.value : (parseFloat(min) + parseFloat(max)) / 2;
            const step = attrObj.step || 1;
            
            return `<param-slider name="${name}" label="${label}" min="${min}" max="${max}" value="${value}" step="${step}"></param-slider>`;
        });
    }

    /**
     * 解析图表
     */
    parseCharts(text) {
        return text.replace(this.patterns.chart, (match, type, params) => {
            const attrObj = this.parseAttributes(params);
            
            // 构建 data 对象
            const dataObj = {};
            if (attrObj.x) dataObj.x = attrObj.x;
            if (attrObj.y) dataObj.y = attrObj.y;
            if (attrObj.size) dataObj.size = attrObj.size;
            if (attrObj.color) dataObj.color = attrObj.color;
            
            const dataStr = JSON.stringify(dataObj).replace(/"/g, '&quot;');
            const configStr = JSON.stringify(attrObj).replace(/"/g, '&quot;');
            
            return `<chart-renderer type="${type}" data="${dataStr}" config="${configStr}" title="${attrObj.title || ''}" height="${attrObj.height || '400'}"></chart-renderer>`;
        });
    }

    /**
     * 解析交互式表格
     */
    parseTables(text) {
        return text.replace(this.patterns.table, (match, source, params) => {
            const attrObj = this.parseAttributes(params);
            
            const sortable = attrObj.sortable !== 'false';
            const filterable = attrObj.filterable !== 'false';
            
            return `<data-table source="${source}" sortable="${sortable}" filterable="${filterable}"></data-table>`;
        });
    }

    /**
     * 解析信息图
     */
    parseInfographics(text) {
        return text.replace(this.patterns.infographic, (match, type, params, content) => {
            const attrObj = this.parseAttributes(params);
            
            // 解析内容中的节点
            const nodes = this.parseInfographicContent(content);
            const nodesStr = JSON.stringify(nodes).replace(/"/g, '&quot;');
            
            return `<info-graphic type="${type}" title="${attrObj.title || ''}" nodes="${nodesStr}"></info-graphic>`;
        });
    }

    /**
     * 解析对比视图
     */
    parseCompare(text) {
        return text.replace(this.patterns.compare, (match, title, content) => {
            const rows = this.parseCompareContent(content);
            const rowsStr = JSON.stringify(rows).replace(/"/g, '&quot;');
            
            return `<compare-view title="${title}" rows="${rowsStr}"></compare-view>`;
        });
    }

    /**
     * 解析属性字符串 "key=value,key2=value2"
     */
    parseAttributes(attrStr) {
        if (!attrStr) return {};
        
        const attrs = {};
        const pairs = attrStr.split(',');
        
        pairs.forEach(pair => {
            const [key, ...valueParts] = pair.trim().split('=');
            if (key && valueParts.length > 0) {
                let value = valueParts.join('=').trim();
                
                // 尝试解析为数字
                if (/^-?\d+$/.test(value)) {
                    value = parseInt(value);
                } else if (/^-?\d+\.\d+$/.test(value)) {
                    value = parseFloat(value);
                } else if (value === 'true') {
                    value = true;
                } else if (value === 'false') {
                    value = false;
                } else if (value.startsWith('[') && value.endsWith(']')) {
                    // 数组
                    try {
                        value = JSON.parse(value);
                    } catch (e) {}
                }
                
                attrs[key.trim()] = value;
            }
        });
        
        return attrs;
    }

    /**
     * 解析信息图内容
     */
    parseInfographicContent(content) {
        const nodes = [];
        const lines = content.trim().split('\n');
        
        lines.forEach(line => {
            line = line.trim();
            if (!line || line.startsWith('-')) {
                // 解析 "- 节点名 → [详情]" 格式
                const match = line.match(/-\s*(.+?)\s*→\s*\[(.*?)\]/);
                if (match) {
                    nodes.push({
                        name: match[1].trim(),
                        detail: match[2].trim()
                    });
                }
            }
        });
        
        return nodes;
    }

    /**
     * 解析对比内容
     */
    parseCompareContent(content) {
        const rows = [];
        const lines = content.trim().split('\n');
        
        lines.forEach(line => {
            line = line.trim();
            if (!line) return;
            
            // 解析 "维度 :: 左侧内容 :: 右侧内容" 格式
            const parts = line.split('::').map(p => p.trim());
            if (parts.length >= 3) {
                rows.push({
                    dimension: parts[0].replace(/^-\s*/, ''),
                    left: parts[1],
                    right: parts[2]
                });
            }
        });
        
        return rows;
    }

    /**
     * 在代码执行前插值变量
     */
    interpolateVariables(code, sliderValues) {
        return code.replace(this.patterns.interpolation, (match, varName) => {
            if (sliderValues[varName] !== undefined) {
                return sliderValues[varName];
            }
            return '0';
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MarkdownInteractive;
} else {
    window.MarkdownInteractive = MarkdownInteractive;
}
