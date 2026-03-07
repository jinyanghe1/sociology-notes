/**
 * 参数滑块组件
 * 用于动态调整模型参数，实时更新关联图表
 */

class ParamSlider extends HTMLElement {
    constructor() {
        super();
        this.value = 0;
        this.listeners = [];
    }

    static get observedAttributes() {
        return ['label', 'min', 'max', 'value', 'step'];
    }

    connectedCallback() {
        this.label = this.getAttribute('label') || '参数';
        this.min = parseFloat(this.getAttribute('min')) || 0;
        this.max = parseFloat(this.getAttribute('max')) || 100;
        this.value = parseFloat(this.getAttribute('value')) || (this.min + this.max) / 2;
        this.step = parseFloat(this.getAttribute('step')) || 1;
        this.name = this.getAttribute('name') || this.label;
        
        this.render();
        this.bindEvents();
    }

    render() {
        this.innerHTML = `
            <div class="param-slider">
                <div class="slider-header">
                    <label class="slider-label">${this.label}</label>
                    <span class="slider-value">${this.value}</span>
                </div>
                <div class="slider-control">
                    <span class="slider-min">${this.min}</span>
                    <input type="range" 
                           class="slider-input"
                           min="${this.min}" 
                           max="${this.max}" 
                           step="${this.step}"
                           value="${this.value}">
                    <span class="slider-max">${this.max}</span>
                </div>
                <div class="slider-description">
                    <slot></slot>
                </div>
            </div>
        `;
        
        this.input = this.querySelector('.slider-input');
        this.valueDisplay = this.querySelector('.slider-value');
    }

    bindEvents() {
        this.input.addEventListener('input', (e) => {
            this.value = parseFloat(e.target.value);
            this.valueDisplay.textContent = this.formatValue(this.value);
            this.dispatchEvent(new CustomEvent('change', {
                detail: { value: this.value, name: this.name },
                bubbles: true
            }));
            this.notifyListeners();
        });
    }

    formatValue(val) {
        // 根据 step 决定显示精度
        if (this.step >= 1) {
            return Math.round(val);
        } else if (this.step >= 0.1) {
            return val.toFixed(1);
        } else if (this.step >= 0.01) {
            return val.toFixed(2);
        }
        return val.toFixed(3);
    }

    getValue() {
        return this.value;
    }

    setValue(val) {
        this.value = parseFloat(val);
        this.input.value = this.value;
        this.valueDisplay.textContent = this.formatValue(this.value);
    }

    onChange(callback) {
        this.listeners.push(callback);
    }

    notifyListeners() {
        this.listeners.forEach(cb => cb(this.value));
    }
}

// 滑块组组件 - 管理多个相关滑块
class ParamSliderGroup extends HTMLElement {
    constructor() {
        super();
        this.sliders = {};
    }

    connectedCallback() {
        this.innerHTML = `
            <div class="slider-group">
                <div class="group-header">
                    <h4>${this.getAttribute('title') || '参数设置'}</h4>
                </div>
                <div class="group-content">
                    <slot></slot>
                </div>
                <div class="group-actions">
                    <button class="btn-reset-all">重置所有</button>
                </div>
            </div>
        `;
        
        // 收集所有子滑块
        setTimeout(() => {
            this.querySelectorAll('param-slider').forEach(slider => {
                this.sliders[slider.getAttribute('name')] = slider;
            });
        }, 0);
        
        this.querySelector('.btn-reset-all').addEventListener('click', () => {
            this.resetAll();
        });
    }

    getValues() {
        const values = {};
        for (const [name, slider] of Object.entries(this.sliders)) {
            values[name] = slider.getValue();
        }
        return values;
    }

    resetAll() {
        this.querySelectorAll('param-slider').forEach(slider => {
            const defaultValue = parseFloat(slider.getAttribute('value')) || 
                                 (parseFloat(slider.getAttribute('min')) + 
                                  parseFloat(slider.getAttribute('max'))) / 2;
            slider.setValue(defaultValue);
        });
    }
}

customElements.define('param-slider', ParamSlider);
customElements.define('param-slider-group', ParamSliderGroup);
