/**
 * 交互式数据表格组件
 * 支持排序、筛选、分页
 */

class DataTable extends HTMLElement {
    constructor() {
        super();
        this.data = [];
        this.filteredData = [];
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.currentPage = 1;
        this.pageSize = 10;
    }

    static get observedAttributes() {
        return ['source', 'sortable', 'filterable'];
    }

    async connectedCallback() {
        this.sortable = this.getAttribute('sortable') !== 'false';
        this.filterable = this.getAttribute('filterable') !== 'false';
        
        this.render();
        
        const source = this.getAttribute('source');
        if (source) {
            await this.loadData(source);
        }
    }

    render() {
        this.innerHTML = `
            <div class="data-table-container">
                ${this.filterable ? `
                    <div class="table-filters">
                        <input type="text" class="filter-input" placeholder="🔍 搜索...">
                    </div>
                ` : ''}
                <div class="table-wrapper">
                    <table class="data-table">
                        <thead></thead>
                        <tbody></tbody>
                    </table>
                </div>
                <div class="table-footer">
                    <div class="table-info">
                        显示 <span class="showing-start">0</span>-<span class="showing-end">0</span> 条，共 <span class="total-count">0</span> 条
                    </div>
                    <div class="table-pagination">
                        <button class="btn-prev" disabled>上一页</button>
                        <span class="page-info">第 <span class="current-page">1</span> 页</span>
                        <button class="btn-next" disabled>下一页</button>
                    </div>
                </div>
            </div>
        `;
        
        // 绑定事件
        if (this.filterable) {
            this.querySelector('.filter-input').addEventListener('input', (e) => {
                this.handleFilter(e.target.value);
            });
        }
        
        this.querySelector('.btn-prev').addEventListener('click', () => this.prevPage());
        this.querySelector('.btn-next').addEventListener('click', () => this.nextPage());
    }

    async loadData(source) {
        try {
            // 支持内联数据或 URL
            if (source.endsWith('.csv')) {
                const response = await fetch(source);
                const text = await response.text();
                this.data = this.parseCSV(text);
            } else if (source.endsWith('.json')) {
                const response = await fetch(source);
                this.data = await response.json();
            } else {
                // 尝试解析为内联 JSON
                this.data = JSON.parse(source);
            }
            
            this.filteredData = [...this.data];
            this.renderTable();
        } catch (error) {
            console.error('加载数据失败:', error);
            this.showError('数据加载失败');
        }
    }

    parseCSV(text) {
        const lines = text.trim().split('\n');
        const headers = lines[0].split(',').map(h => h.trim());
        
        return lines.slice(1).map(line => {
            const values = line.split(',').map(v => v.trim());
            const obj = {};
            headers.forEach((h, i) => {
                // 尝试转换为数字
                const val = values[i];
                obj[h] = isNaN(parseFloat(val)) ? val : parseFloat(val);
            });
            return obj;
        });
    }

    renderTable() {
        if (this.data.length === 0) return;
        
        const headers = Object.keys(this.data[0]);
        const thead = this.querySelector('thead');
        const tbody = this.querySelector('tbody');
        
        // 渲染表头
        thead.innerHTML = `
            <tr>
                ${headers.map(h => `
                    <th ${this.sortable ? 'class="sortable"' : ''} data-column="${h}">
                        ${h}
                        ${this.sortable ? '<span class="sort-icon">⇅</span>' : ''}
                    </th>
                `).join('')}
            </tr>
        `;
        
        // 绑定排序事件
        if (this.sortable) {
            thead.querySelectorAll('th.sortable').forEach(th => {
                th.addEventListener('click', () => this.handleSort(th.dataset.column));
            });
        }
        
        // 分页数据
        const start = (this.currentPage - 1) * this.pageSize;
        const end = Math.min(start + this.pageSize, this.filteredData.length);
        const pageData = this.filteredData.slice(start, end);
        
        // 渲染表体
        tbody.innerHTML = pageData.map(row => `
            <tr>
                ${headers.map(h => `
                    <td>${this.formatCell(row[h])}</td>
                `).join('')}
            </tr>
        `).join('');
        
        // 更新分页信息
        this.updatePagination(start + 1, end, this.filteredData.length);
    }

    formatCell(value) {
        if (typeof value === 'number') {
            // 保留适当小数位
            return Number.isInteger(value) ? value : value.toFixed(2);
        }
        return value;
    }

    handleSort(column) {
        if (this.sortColumn === column) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = column;
            this.sortDirection = 'asc';
        }
        
        this.filteredData.sort((a, b) => {
            const aVal = a[column];
            const bVal = b[column];
            
            if (typeof aVal === 'number' && typeof bVal === 'number') {
                return this.sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
            }
            
            const aStr = String(aVal).toLowerCase();
            const bStr = String(bVal).toLowerCase();
            
            if (this.sortDirection === 'asc') {
                return aStr.localeCompare(bStr);
            }
            return bStr.localeCompare(aStr);
        });
        
        this.currentPage = 1;
        this.renderTable();
        this.updateSortIcons();
    }

    updateSortIcons() {
        this.querySelectorAll('th.sortable').forEach(th => {
            const icon = th.querySelector('.sort-icon');
            if (th.dataset.column === this.sortColumn) {
                icon.textContent = this.sortDirection === 'asc' ? '↑' : '↓';
            } else {
                icon.textContent = '⇅';
            }
        });
    }

    handleFilter(query) {
        if (!query) {
            this.filteredData = [...this.data];
        } else {
            const lowerQuery = query.toLowerCase();
            this.filteredData = this.data.filter(row => {
                return Object.values(row).some(val => 
                    String(val).toLowerCase().includes(lowerQuery)
                );
            });
        }
        
        this.currentPage = 1;
        this.renderTable();
    }

    prevPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.renderTable();
        }
    }

    nextPage() {
        const maxPage = Math.ceil(this.filteredData.length / this.pageSize);
        if (this.currentPage < maxPage) {
            this.currentPage++;
            this.renderTable();
        }
    }

    updatePagination(start, end, total) {
        this.querySelector('.showing-start').textContent = total > 0 ? start : 0;
        this.querySelector('.showing-end').textContent = end;
        this.querySelector('.total-count').textContent = total;
        this.querySelector('.current-page').textContent = this.currentPage;
        
        const maxPage = Math.ceil(total / this.pageSize);
        this.querySelector('.btn-prev').disabled = this.currentPage <= 1;
        this.querySelector('.btn-next').disabled = this.currentPage >= maxPage || maxPage === 0;
    }

    showError(message) {
        this.querySelector('tbody').innerHTML = `
            <tr><td colspan="100" class="error-cell">${message}</td></tr>
        `;
    }
}

customElements.define('data-table', DataTable);
