/**
 * 文章页面交互脚本
 */

document.addEventListener('DOMContentLoaded', () => {
    // 处理代码高亮（简单版）
    document.querySelectorAll('pre code').forEach(block => {
        block.classList.add('code-block');
    });
    
    // 处理表格样式
    document.querySelectorAll('table').forEach(table => {
        table.classList.add('data-table');
    });
    
    // 平滑滚动到锚点
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});
