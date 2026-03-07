"""
交互式笔记的 Python 工具函数
"""
import json
import sys
from io import StringIO

# 重定向输出以捕获结果
class OutputCapture:
    def __init__(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.figures = []
    
    def __enter__(self):
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        return self
    
    def __exit__(self, *args):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
    
    def get_output(self):
        return {
            'stdout': self.stdout.getvalue(),
            'stderr': self.stderr.getvalue(),
            'figures': self.figures
        }

def capture_output(func):
    """装饰器：捕获函数输出"""
    def wrapper(*args, **kwargs):
        with OutputCapture() as cap:
            try:
                result = func(*args, **kwargs)
                output = cap.get_output()
                output['result'] = result
                return output
            except Exception as e:
                output = cap.get_output()
                output['error'] = str(e)
                return output
    return wrapper

def render_plot(fig, format='svg'):
    """将 matplotlib 图表转换为可嵌入格式"""
    import matplotlib.pyplot as plt
    import base64
    from io import BytesIO
    
    buf = BytesIO()
    fig.savefig(buf, format=format, bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f'data:image/{format};base64,{img_str}'

# 常用的社会学分析函数
def gini_coefficient(x):
    """计算基尼系数"""
    import numpy as np
    x = np.array(x, dtype=float)
    x = np.sort(x)
    n = len(x)
    cumsum = np.cumsum(x)
    return (2 * np.sum((np.arange(1, n+1) * x))) / (n * cumsum[-1]) - (n+1)/n

def concentration_index(x, y):
    """计算集中度指数"""
    import numpy as np
    # 假设 x 是排序后的累积人口比例，y 是累积收入比例
    return np.trapz(y, x) - 0.5

print("✅ Sociology Notes Python utils loaded")
