/**
 * 可运行 Python 代码块组件
 * 集成 PyScript 实现浏览器内代码执行
 */

class CodeRunner extends HTMLElement {
    constructor() {
        super();
        this.code = '';
        this.originalCode = '';
        this.editor = null;
        this.isRunning = false;
    }

    connectedCallback() {
        this.code = this.textContent.trim();
        this.originalCode = this.code;
        this.render();
        this.initEditor();
    }

    render() {
        const height = this.getAttribute('height') || '200';
        
        this.innerHTML = `
            <div class="code-runner">
                <div class="code-header">
                    <span class="code-label">🐍 Python</span>
                    <div class="code-actions">
                        <button class="btn-run" title="运行代码 (Ctrl+Enter)">
                            ▶ 运行
                        </button>
                        <button class="btn-reset" title="重置代码">
                            ↺ 重置
                        </button>
                    </div>
                </div>
                <div class="code-editor" style="height: ${height}px;"></div>
                <div class="code-output" style="display: none;">
                    <div class="output-header">
                        <span>输出</span>
                        <button class="btn-clear">清除</button>
                    </div>
                    <pre class="output-content"></pre>
                </div>
                <div class="pyscript-loading" style="display: none;">
                    <span class="spinner"></span>
                    正在加载 Python 运行时...
                </div>
            </div>
        `;

        // 绑定事件
        this.querySelector('.btn-run').addEventListener('click', () => this.runCode());
        this.querySelector('.btn-reset').addEventListener('click', () => this.resetCode());
        this.querySelector('.btn-clear').addEventListener('click', () => this.clearOutput());
        
        // 键盘快捷键
        this.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                this.runCode();
            }
        });
    }

    initEditor() {
        // 使用简单的 textarea + 语法高亮
        // 实际项目中可以集成 CodeMirror 或 Monaco Editor
        const editorDiv = this.querySelector('.code-editor');
        editorDiv.innerHTML = `
            <textarea class="code-textarea" spellcheck="false">${this.escapeHtml(this.code)}</textarea>
        `;
        
        this.textarea = editorDiv.querySelector('textarea');
        
        // Tab 键支持
        this.textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = this.textarea.selectionStart;
                const end = this.textarea.selectionEnd;
                this.textarea.value = this.textarea.value.substring(0, start) + '    ' + 
                                      this.textarea.value.substring(end);
                this.textarea.selectionStart = this.textarea.selectionEnd = start + 4;
            }
        });
    }

    async runCode() {
        if (this.isRunning) return;
        
        const code = this.textarea.value;
        const outputDiv = this.querySelector('.code-output');
        const outputContent = outputDiv.querySelector('.output-content');
        const loadingDiv = this.querySelector('.pyscript-loading');
        
        // 检查 PyScript 是否已加载
        if (!window.pyscriptLoaded) {
            loadingDiv.style.display = 'flex';
            await this.waitForPyScript();
            loadingDiv.style.display = 'none';
        }
        
        this.isRunning = true;
        outputDiv.style.display = 'block';
        outputContent.textContent = '运行中...';
        
        try {
            // 通过 PyScript 执行代码
            const result = await this.executePython(code);
            this.displayOutput(result);
        } catch (error) {
            outputContent.textContent = `错误: ${error.message}`;
            outputContent.classList.add('error');
        } finally {
            this.isRunning = false;
        }
    }

    async executePython(code) {
        // 检查是否有滑块变量需要替换
        code = this.interpolateVariables(code);
        
        // 使用 PyScript 的 Python 环境
        if (window.pyodide) {
            const { pyodide } = window;
            
            // 重定向输出
            pyodide.runPython(`
                import sys
                import io
                sys.stdout = io.StringIO()
                sys.stderr = io.StringIO()
            `);
            
            try {
                await pyodide.runPythonAsync(code);
                
                const stdout = pyodide.runPython('sys.stdout.getvalue()');
                const stderr = pyodide.runPython('sys.stderr.getvalue()');
                
                return {
                    stdout: stdout,
                    stderr: stderr,
                    error: null
                };
            } catch (e) {
                return {
                    stdout: '',
                    stderr: '',
                    error: e.message
                };
            }
        } else {
            throw new Error('Python 运行时尚未加载');
        }
    }

    interpolateVariables(code) {
        // 替换 {{slider.name}} 语法
        return code.replace(/\{\{\s*slider\.(\w+)\s*\}\}/g, (match, varName) => {
            const slider = document.querySelector(`param-slider[name="${varName}"]`);
            if (slider) {
                return slider.getValue();
            }
            return '0';
        });
    }

    displayOutput(result) {
        const outputContent = this.querySelector('.output-content');
        let output = '';
        
        if (result.stdout) {
            output += result.stdout;
        }
        
        if (result.stderr) {
            output += '\n[stderr]\n' + result.stderr;
        }
        
        if (result.error) {
            output += '\n[错误]\n' + result.error;
            outputContent.classList.add('error');
        } else {
            outputContent.classList.remove('error');
        }
        
        outputContent.textContent = output || '(无输出)';
    }

    resetCode() {
        this.textarea.value = this.originalCode;
        this.clearOutput();
    }

    clearOutput() {
        const outputDiv = this.querySelector('.code-output');
        const outputContent = outputDiv.querySelector('.output-content');
        outputDiv.style.display = 'none';
        outputContent.textContent = '';
        outputContent.classList.remove('error');
    }

    waitForPyScript() {
        return new Promise((resolve) => {
            const check = () => {
                if (window.pyodide) {
                    resolve();
                } else {
                    setTimeout(check, 100);
                }
            };
            check();
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 注册自定义元素
customElements.define('code-runner', CodeRunner);
