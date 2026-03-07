// 应用主逻辑
class SociologyNotes {
    constructor() {
        this.articles = [];
        this.graphData = { nodes: [], links: [] };
        this.searchIndex = null;
        this.currentView = 'home';
        this.mdParser = new MarkdownInteractive();
        this.init();
    }

    async init() {
        await this.loadData();
        this.buildSearchIndex();
        this.setupEventListeners();
        this.renderHome();
        this.renderTagsCloud();
        this.setupPyScriptLoader();
    }

    // 设置 PyScript 加载提示
    setupPyScriptLoader() {
        // 监听 PyScript 加载事件
        document.addEventListener('py:ready', () => {
            const loader = document.getElementById('pyscript-loader');
            if (loader) {
                loader.style.display = 'none';
            }
            window.pyscriptLoaded = true;
        });
    }

    // 加载数据
    async loadData() {
        try {
            const response = await fetch('data/index.json');
            const data = await response.json();
            this.articles = data.articles || [];
            this.graphData = data.graph || { nodes: [], links: [] };
        } catch (e) {
            console.warn('使用示例数据');
            this.loadSampleData();
        }
    }

    // 示例数据
    loadSampleData() {
        this.articles = [
            {
                id: 'zhou-2008-conspiracy',
                title: '基层政府间的共谋现象',
                authors: ['周雪光'],
                year: 2008,
                tags: ['基层治理', '共谋', '行政发包制'],
                category: 'papers',
                summary: '探讨中国政府内部上下级政府间在应对上级政策指令时采取共谋行为的制度逻辑',
                content: '...',
                mentions: ['周雪光', '渠敬东', '项目制', '行政发包制']
            },
            {
                id: 'qu-2012-project',
                title: '项目制：一种新型国家治理体制',
                authors: ['渠敬东'],
                year: 2012,
                tags: ['项目制', '国家治理', '财政体制'],
                category: 'papers',
                summary: '分析项目制作为新型国家治理体制的运行机制及其社会影响',
                content: '...',
                mentions: ['渠敬东', '周雪光', '项目制', '行政发包制']
            },
            {
                id: 'concept-contract',
                title: '行政发包制',
                authors: ['周黎安', '周雪光'],
                year: 2014,
                tags: ['国家治理', '央地关系', '行政体制'],
                category: 'concepts',
                summary: '理解中国政府间关系的核心概念，描述中央向地方逐级发包行政任务的治理模式',
                content: '...',
                mentions: ['周黎安', '周雪光', '行政发包制']
            }
        ];
        
        this.buildGraphFromArticles();
    }

    // 从文章构建图谱
    buildGraphFromArticles() {
        const nodes = [];
        const links = [];
        const nodeSet = new Set();

        this.articles.forEach(article => {
            const articleId = `article-${article.id}`;
            if (!nodeSet.has(articleId)) {
                nodes.push({
                    id: articleId,
                    name: article.title,
                    type: article.category,
                    group: 1
                });
                nodeSet.add(articleId);
            }

            article.authors?.forEach(author => {
                const authorId = `author-${author}`;
                if (!nodeSet.has(authorId)) {
                    nodes.push({
                        id: authorId,
                        name: author,
                        type: 'author',
                        group: 2
                    });
                    nodeSet.add(authorId);
                }
                links.push({ source: authorId, target: articleId, type: 'authored' });
            });

            article.tags?.forEach(tag => {
                const tagId = `tag-${tag}`;
                if (!nodeSet.has(tagId)) {
                    nodes.push({
                        id: tagId,
                        name: tag,
                        type: 'tag',
                        group: 3
                    });
                    nodeSet.add(tagId);
                }
                links.push({ source: articleId, target: tagId, type: 'tagged' });
            });

            article.mentions?.forEach(mention => {
                if (mention !== article.title) {
                    const mentionedArticle = this.articles.find(a => 
                        a.title === mention || a.authors?.includes(mention)
                    );
                    if (mentionedArticle) {
                        const mentionedId = `article-${mentionedArticle.id}`;
                        links.push({ 
                            source: articleId, 
                            target: mentionedId, 
                            type: 'mentions' 
                        });
                    }
                }
            });
        });

        this.graphData = { nodes, links };
    }

    // 构建搜索索引
    buildSearchIndex() {
        this.searchIndex = lunr(function() {
            this.ref('id');
            this.field('title', { boost: 10 });
            this.field('authors', { boost: 5 });
            this.field('tags', { boost: 5 });
            this.field('summary');
            this.field('content');

            this.articles.forEach(article => {
                this.add({
                    id: article.id,
                    title: article.title,
                    authors: article.authors?.join(' '),
                    tags: article.tags?.join(' '),
                    summary: article.summary,
                    content: article.content?.substring(0, 1000)
                });
            });
        });
    }

    // 设置事件监听
    setupEventListeners() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const view = item.dataset.view;
                this.switchView(view);
            });
        });

        const searchInput = document.getElementById('search-input');
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.handleSearch(e.target.value);
            }, 300);
        });

        document.getElementById('semantic-search-btn').addEventListener('click', () => {
            this.handleSemanticSearch(searchInput.value);
        });

        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById('content').className = `content ${btn.dataset.mode}-view`;
            });
        });

        document.querySelector('.close-btn').addEventListener('click', () => {
            document.getElementById('article-modal').style.display = 'none';
        });

        document.getElementById('article-modal').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                document.getElementById('article-modal').style.display = 'none';
            }
        });
    }

    // 切换视图
    switchView(view) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.view === view) item.classList.add('active');
        });

        document.getElementById('graph-view').style.display = view === 'graph' ? 'block' : 'none';

        switch(view) {
            case 'home':
                this.renderHome();
                break;
            case 'papers':
                this.renderCategory('papers');
                break;
            case 'books':
                this.renderCategory('books');
                break;
            case 'concepts':
                this.renderCategory('concepts');
                break;
            case 'graph':
                this.renderGraph();
                break;
            case 'about':
                this.renderAbout();
                break;
        }
    }

    // 渲染首页
    renderHome() {
        const recentArticles = this.articles.slice(0, 6);
        const html = `
            <div class="welcome-section">
                <h2>👋 欢迎</h2>
                <p>这里是我的社会学学习笔记，包含论文、书籍和概念梳理。</p>
                <p>💡 支持交互式代码运行：在阅读定量分析论文时，可以运行 Python 代码复现分析过程。</p>
                <div class="stats">
                    <div class="stat-item">
                        <span class="stat-number">${this.articles.filter(a => a.category === 'papers').length}</span>
                        <span class="stat-label">论文笔记</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">${this.articles.filter(a => a.category === 'books').length}</span>
                        <span class="stat-label">书籍笔记</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">${this.articles.filter(a => a.category === 'concepts').length}</span>
                        <span class="stat-label">概念梳理</span>
                    </div>
                </div>
            </div>
            <h3>📝 最近更新</h3>
            <div class="list-view">
                ${recentArticles.map(article => this.createCardHTML(article)).join('')}
            </div>
        `;
        document.getElementById('content').innerHTML = html;
        this.attachCardListeners();
    }

    // 渲染分类
    renderCategory(category) {
        const filtered = this.articles.filter(a => a.category === category);
        const titles = { papers: '📄 论文笔记', books: '📖 书籍笔记', concepts: '💡 概念梳理' };
        const html = `
            <h2>${titles[category]}</h2>
            <div class="list-view">
                ${filtered.map(article => this.createCardHTML(article)).join('')}
            </div>
        `;
        document.getElementById('content').innerHTML = html;
        this.attachCardListeners();
    }

    // 创建卡片HTML
    createCardHTML(article) {
        const typeLabels = { papers: '论文', books: '书籍', concepts: '概念' };
        return `
            <div class="card" data-id="${article.id}">
                <div class="card-header">
                    <span class="card-type ${article.category}">${typeLabels[article.category]}</span>
                    <span class="card-year">${article.year || ''}</span>
                </div>
                <h3>${article.title}</h3>
                <div class="card-meta">
                    ${article.authors?.join(', ') || ''}
                    ${article.venue ? ` · ${article.venue}` : ''}
                </div>
                <div class="card-summary">${article.summary || article.content?.substring(0, 150) + '...'}</div>
                <div class="card-tags">
                    ${article.tags?.map(tag => `<span class="card-tag">${tag}</span>`).join('') || ''}
                </div>
            </div>
        `;
    }

    // 附加卡片点击事件
    attachCardListeners() {
        document.querySelectorAll('.card').forEach(card => {
            card.addEventListener('click', () => {
                const article = this.articles.find(a => a.id === card.dataset.id);
                if (article) this.showArticle(article);
            });
        });
    }

    // 显示文章详情
    showArticle(article) {
        const modal = document.getElementById('article-modal');
        const content = document.getElementById('article-content');
        
        // 处理交互式 Markdown 语法
        let processedContent = article.content || '';
        
        // 使用 MarkdownInteractive 解析扩展语法
        if (this.mdParser) {
            processedContent = this.mdParser.parse(processedContent);
        }
        
        // 处理 @ 提及
        processedContent = processedContent.replace(/@([^\s@,，。.!！?？]+)/g, (match, name) => {
            return `<a href="#" class="mention-link" data-mention="${name}">@${name}</a>`;
        });

        content.innerHTML = `
            <header class="article-header">
                <span class="card-type ${article.category}">${article.category}</span>
                <h1>${article.title}</h1>
                <div class="article-meta">
                    ${article.authors?.join(', ') ? `<span>作者: ${article.authors.join(', ')}</span>` : ''}
                    ${article.year ? `<span>年份: ${article.year}</span>` : ''}
                    ${article.venue ? `<span>来源: ${article.venue}</span>` : ''}
                </div>
            </header>
            <div class="article-body">
                ${marked.parse(processedContent || article.summary || '暂无内容')}
            </div>
            <div class="article-footer">
                ${article.tags?.length ? `
                    <div class="article-tags">
                        <strong>标签:</strong>
                        ${article.tags.map(tag => `<span class="card-tag">${tag}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        `;

        // 处理提及链接点击
        content.querySelectorAll('.mention-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const mention = link.dataset.mention;
                const mentionedArticle = this.articles.find(a => 
                    a.title === mention || a.authors?.includes(mention)
                );
                if (mentionedArticle) {
                    this.showArticle(mentionedArticle);
                }
            });
        });

        modal.style.display = 'block';
        
        // 初始化图表（如果有）
        setTimeout(() => {
            content.querySelectorAll('chart-renderer').forEach(chart => {
                if (chart.drawChart) {
                    chart.drawChart();
                }
            });
        }, 100);
    }

    // 渲染标签云
    renderTagsCloud() {
        const allTags = {};
        this.articles.forEach(article => {
            article.tags?.forEach(tag => {
                allTags[tag] = (allTags[tag] || 0) + 1;
            });
        });

        const sortedTags = Object.entries(allTags)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 15);

        const container = document.querySelector('.tags-list');
        container.innerHTML = sortedTags.map(([tag, count]) => 
            `<span class="tag" data-tag="${tag}">${tag} (${count})</span>`
        ).join('');

        container.querySelectorAll('.tag').forEach(tagEl => {
            tagEl.addEventListener('click', () => {
                document.getElementById('search-input').value = tagEl.dataset.tag;
                this.handleSearch(tagEl.dataset.tag);
            });
        });
    }

    // 搜索处理
    handleSearch(query) {
        if (!query.trim()) {
            this.renderHome();
            return;
        }

        const results = this.searchIndex.search(query);
        const matchedArticles = results.map(r => 
            this.articles.find(a => a.id === r.ref)
        ).filter(Boolean);

        const html = `
            <h2>🔍 搜索结果: "${query}"</h2>
            <p>找到 ${matchedArticles.length} 篇相关文章</p>
            <div class="list-view">
                ${matchedArticles.length ? matchedArticles.map(a => this.createCardHTML(a)).join('') : 
                '<p class="no-results">没有找到相关文章，试试语义搜索？</p>'}
            </div>
        `;
        document.getElementById('content').innerHTML = html;
        this.attachCardListeners();
    }

    // 语义搜索
    handleSemanticSearch(query) {
        if (!query.trim()) return;

        const keywords = {
            '基层治理': ['基层治理', '社区自治', '行政下沉', '网格化', '共治'],
            '国家治理': ['国家治理', '治理现代化', '治理能力', '制度优势'],
            '项目制': ['项目制', '专项资金', '财政转移支付', '打包机制']
        };

        let relatedTerms = [query];
        for (const [key, terms] of Object.entries(keywords)) {
            if (query.includes(key) || key.includes(query)) {
                relatedTerms = [...relatedTerms, ...terms];
            }
        }

        const matched = this.articles.filter(article => {
            const text = `${article.title} ${article.summary} ${article.tags?.join(' ')}`.toLowerCase();
            return relatedTerms.some(term => text.includes(term.toLowerCase()));
        });

        const html = `
            <div class="semantic-hint">
                <h3>🧠 语义搜索: "${query}"</h3>
                <p>基于语义相似度，为您找到以下相关内容：</p>
                <small>相关概念: ${relatedTerms.slice(1, 4).join(', ')}...</small>
            </div>
            <div class="list-view">
                ${matched.map(a => this.createCardHTML(a)).join('')}
            </div>
        `;
        document.getElementById('content').innerHTML = html;
        this.attachCardListeners();
    }

    // 渲染脑图
    renderGraph() {
        const container = document.getElementById('graph-container');
        container.innerHTML = '';

        const width = container.clientWidth;
        const height = container.clientHeight;

        const svg = d3.select('#graph-container')
            .append('svg')
            .attr('width', width)
            .attr('height', height);

        const colorMap = {
            papers: '#3498db',
            books: '#9b59b6',
            concepts: '#2ecc71',
            author: '#f39c12',
            tag: '#e74c3c'
        };

        const g = svg.append('g');

        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
            });

        svg.call(zoom);

        const simulation = d3.forceSimulation(this.graphData.nodes)
            .force('link', d3.forceLink(this.graphData.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(30));

        const link = g.append('g')
            .selectAll('line')
            .data(this.graphData.links)
            .enter()
            .append('line')
            .attr('stroke', 'rgba(255,255,255,0.3)')
            .attr('stroke-width', 1);

        const node = g.append('g')
            .selectAll('g')
            .data(this.graphData.nodes)
            .enter()
            .append('g')
            .call(d3.drag()
                .on('start', (event, d) => {
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                })
                .on('drag', (event, d) => {
                    d.fx = event.x;
                    d.fy = event.y;
                })
                .on('end', (event, d) => {
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }));

        node.append('circle')
            .attr('r', d => d.type === 'author' ? 8 : 12)
            .attr('fill', d => colorMap[d.type] || '#999')
            .attr('stroke', '#fff')
            .attr('stroke-width', 2)
            .style('cursor', 'pointer');

        node.append('text')
            .text(d => d.name)
            .attr('x', 15)
            .attr('y', 4)
            .attr('fill', '#fff')
            .attr('font-size', '12px')
            .style('pointer-events', 'none');

        node.on('click', (event, d) => {
            if (d.type !== 'author' && d.type !== 'tag') {
                const article = this.articles.find(a => `article-${a.id}` === d.id);
                if (article) this.showArticle(article);
            }
        });

        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node.attr('transform', d => `translate(${d.x},${d.y})`);
        });

        document.getElementById('reset-zoom').addEventListener('click', () => {
            svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
        });

        document.getElementById('graph-search').addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            node.selectAll('circle')
                .attr('opacity', d => 
                    !term || d.name.toLowerCase().includes(term) ? 1 : 0.2
                );
        });
    }

    // 渲染关于页面
    renderAbout() {
        const html = `
            <div class="about-page">
                <h2>ℹ️ 关于本站</h2>
                <p>这是一个基于 GitHub Pages 的社会学读书笔记网站。</p>
                
                <h3>🎯 功能特色</h3>
                <ul>
                    <li><strong>关键词搜索</strong> - 快速定位相关内容</li>
                    <li><strong>语义搜索</strong> - 基于概念的智能匹配</li>
                    <li><strong>知识脑图</strong> - 可视化文章关联</li>
                    <li><strong>@ 关联</strong> - 文章间相互引用跳转</li>
                    <li><strong>交互式代码</strong> - 运行 Python 复现论文分析</li>
                    <li><strong>参数滑块</strong> - 动态调整模型参数</li>
                </ul>
                
                <h3>🚀 交互式功能</h3>
                <p>在定量分析论文笔记中，你可以：</p>
                <ul>
                    <li>运行 <code>python-runnable</code> 代码块复现分析</li>
                    <li>使用 <code>@slider</code> 调节参数看效应变化</li>
                    <li>通过 <code>@chart</code> 查看交互式图表</li>
                    <li>用 <code>@table</code> 探索数据</li>
                </ul>
                
                <h3>🔗 相关链接</h3>
                <ul>
                    <li><a href="https://github.com/jinyanghe1/sociology-notes">GitHub 仓库</a></li>
                    <li><a href="https://github.com/jinyanghe1/sociology-notes/issues">提交反馈</a></li>
                </ul>
            </div>
        `;
        document.getElementById('content').innerHTML = html;
    }
}

// 启动应用
document.addEventListener('DOMContentLoaded', () => {
    new SociologyNotes();
});
