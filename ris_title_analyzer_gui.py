import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import os
from datetime import datetime

class RISAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RIS文件标题词频分析工具")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        # 设置窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 设置现代化主题
        self.setup_style()

        # 数据存储
        self.titles = []
        self.word_counts = []
        self.custom_stop_words = set()
        self.analysis_thread = None  # 跟踪分析线程

        self.setup_ui()

    def setup_style(self):
        """设置现代化的UI样式"""
        style = ttk.Style()

        # 设置主题
        try:
            style.theme_use('clam')  # 使用更现代的主题
        except:
            pass

        # 设置ttk组件的背景为白色
        style.configure('TFrame', background='#ffffff')
        style.configure('TLabelFrame', background='#ffffff')
        style.configure('TLabelFrame.Label', background='#ffffff')
        style.configure('TNotebook', background='#ffffff')
        style.configure('TNotebook.Tab', background='#f8f9fa', padding=[12, 8])
        style.configure('TPanedwindow', background='#ffffff')
        style.configure('TEntry', fieldbackground='#ffffff')
        style.configure('TSpinbox', fieldbackground='#ffffff')
        style.configure('TText', fieldbackground='#ffffff')

        # 自定义样式 - 现代温暖主题
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#6366f1')
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), foreground='#8b5cf6')

        # 主要按钮样式 - 现代紫色
        style.configure('Custom.TButton',
                       font=('Arial', 10, 'bold'),
                       padding=(12, 8),
                       background='#6366f1',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        style.map('Custom.TButton',
                 background=[('active', '#5b21b6'),
                           ('pressed', '#4c1d95'),
                           ('disabled', '#a78bfa')],  # 禁用状态使用浅紫色
                 foreground=[('disabled', '#ffffff')])  # 禁用状态保持白色文字

        # 成功按钮样式 - 蓝色系，避免绿色
        style.configure('Success.TButton',
                       font=('Arial', 10, 'bold'),
                       padding=(12, 8),
                       background='#3b82f6',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        style.map('Success.TButton',
                 background=[('active', '#2563eb'),
                           ('pressed', '#1d4ed8'),
                           ('disabled', '#9ca3af')],  # 禁用状态使用灰色
                 foreground=[('disabled', '#ffffff')])  # 禁用状态保持白色文字

        # 现代化配色方案 - 温暖渐变主题
        self.colors = {
            'primary': '#6366f1',      # 主色调 - 现代紫色
            'secondary': '#8b5cf6',    # 次要色 - 深紫色
            'accent': '#ec4899',       # 强调色 - 粉红色
            'success': '#3b82f6',      # 成功色 - 蓝色
            'warning': '#f59e0b',      # 警告色 - 琥珀色
            'danger': '#ef4444',       # 危险色 - 红色
            'dark': '#1f2937',         # 深色文字
            'light': '#ffffff',        # 白色背景
            'background': '#ffffff',   # 主背景色
            'muted': '#9ca3af',        # 中性灰色
            'border': '#e5e7eb',       # 边框色
            'gradient_start': '#6366f1', # 渐变起始色
            'gradient_end': '#ec4899'    # 渐变结束色
        }
        
    def setup_ui(self):
        # 设置根窗口背景
        self.root.configure(bg=self.colors['light'])

        # 创建主容器 - 使用PanedWindow实现可调整布局
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧控制面板
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)

        # 右侧结果面板
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)

        # 设置左右面板
        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)

    def setup_left_panel(self, parent):
        """设置左侧控制面板"""
        # 标题区域
        title_frame = tk.Frame(parent, bg=self.colors['background'])
        title_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(title_frame, text="📊 RIS词频分析",
                               font=('Arial', 16, 'bold'), foreground=self.colors['primary'])
        title_label.pack()

        subtitle_label = ttk.Label(title_frame, text="学术文章标题分析工具",
                                 font=('Arial', 10), foreground=self.colors['muted'])
        subtitle_label.pack(pady=(5, 0))

        # 文件选择区域
        file_frame = ttk.LabelFrame(parent, text="📁 文件选择", padding="15")
        file_frame.pack(fill=tk.X, pady=(0, 15))

        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var,
                                   font=('Arial', 10))
        self.file_entry.pack(fill=tk.X, pady=(0, 10))

        self.browse_button = ttk.Button(file_frame, text="📂 浏览文件",
                                       command=self.browse_file, style='Custom.TButton')
        self.browse_button.pack(fill=tk.X)

        # 分析设置区域
        settings_frame = ttk.LabelFrame(parent, text="⚙️ 分析设置", padding="15")
        settings_frame.pack(fill=tk.X, pady=(0, 15))

        # 词汇数量设置
        ttk.Label(settings_frame, text="显示词汇数量:",
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W)

        count_frame = tk.Frame(settings_frame)
        count_frame.pack(fill=tk.X, pady=(5, 15))

        self.word_count_var = tk.StringVar(value="50")
        count_spinbox = ttk.Spinbox(count_frame, from_=10, to=200, width=10,
                                   textvariable=self.word_count_var, font=('Arial', 10))
        count_spinbox.pack(side=tk.LEFT)

        ttk.Label(count_frame, text="个 (10-200)",
                 font=('Arial', 9), foreground=self.colors['muted']).pack(side=tk.LEFT, padx=(10, 0))

        # 自定义停用词
        ttk.Label(settings_frame, text="自定义停用词:",
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(settings_frame, text="用空格或逗号分隔",
                 font=('Arial', 9), foreground=self.colors['muted']).pack(anchor=tk.W, pady=(2, 5))

        self.custom_stop_words_entry = tk.Text(settings_frame, height=4, font=('Arial', 10),
                                              relief=tk.SOLID, borderwidth=1, bg='#ffffff')
        self.custom_stop_words_entry.pack(fill=tk.X, pady=(0, 15))

        # 控制按钮
        self.analyze_button = ttk.Button(settings_frame, text="🚀 开始分析",
                                        command=self.start_analysis, style='Custom.TButton')
        self.analyze_button.pack(fill=tk.X, pady=(0, 10))

        # 保存选项
        save_frame = ttk.LabelFrame(parent, text="💾 保存选项", padding="15")
        save_frame.pack(fill=tk.X, pady=(0, 15))

        self.download_chart_button = ttk.Button(save_frame, text="📥 下载词频图表",
                                               command=self.download_chart,
                                               state="disabled", style='Custom.TButton')
        self.download_chart_button.pack(fill=tk.X, pady=(0, 5))

        self.save_txt_button = ttk.Button(save_frame, text="保存词频数据为TXT",
                                         command=lambda: self.save_results('txt'),
                                         state="disabled", style='Custom.TButton')
        self.save_txt_button.pack(fill=tk.X, pady=(0, 5))

        self.save_csv_button = ttk.Button(save_frame, text="保存词频数据为CSV",
                                         command=lambda: self.save_results('csv'),
                                         state="disabled", style='Custom.TButton')
        self.save_csv_button.pack(fill=tk.X)

        # 状态显示
        status_frame = ttk.LabelFrame(parent, text="📊 状态信息", padding="15")
        status_frame.pack(fill=tk.X)

        self.progress_var = tk.StringVar(value="等待选择文件...")
        self.status_label = ttk.Label(status_frame, textvariable=self.progress_var,
                                     font=('Arial', 11), foreground=self.colors['dark'],
                                     wraplength=250)  # 自动换行
        self.status_label.pack(anchor=tk.W, fill=tk.X)

    def setup_right_panel(self, parent):
        """设置右侧结果面板"""
        # 创建Notebook用于标签页
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 词频列表标签页
        self.word_list_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.word_list_frame, text="📋 词频列表")

        self.result_text = scrolledtext.ScrolledText(self.word_list_frame,
                                                    font=('Consolas', 11),
                                                    relief=tk.SOLID,
                                                    borderwidth=1,
                                                    bg='#ffffff')
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 图表标签页
        self.chart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chart_frame, text="📊 词频图表")

        # 图表显示区域（直接使用整个框架）
        self.chart_display_frame = self.chart_frame
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="选择RIS文件",
            filetypes=[("RIS files", "*.ris"), ("All files", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
    
    def get_custom_stop_words(self):
        """获取用户自定义的停用词"""
        custom_text = self.custom_stop_words_entry.get("1.0", tk.END).strip()
        if custom_text:
            # 支持空格和逗号分隔
            words = re.split(r'[,\s]+', custom_text.lower())
            return set(word.strip() for word in words if word.strip())
        return set()
    
    def start_analysis(self):
        file_path = self.file_path_var.get().strip()
        if not file_path:
            messagebox.showerror("❌ 错误", "请先选择RIS文件")
            return

        if not os.path.exists(file_path):
            messagebox.showerror("❌ 错误", "文件不存在，请检查文件路径")
            return

        # 验证词汇数量设置
        try:
            word_count = int(self.word_count_var.get())
            if word_count < 10 or word_count > 200:
                messagebox.showerror("❌ 错误", "词汇数量必须在10-200之间")
                return
        except ValueError:
            messagebox.showerror("❌ 错误", "请输入有效的词汇数量")
            return

        # 获取自定义停用词
        try:
            self.custom_stop_words = self.get_custom_stop_words()
        except Exception as e:
            messagebox.showerror("❌ 错误", f"处理自定义停用词时出错: {str(e)}")
            return

        # 在新线程中执行分析，避免界面冻结
        self.analyze_button.config(state="disabled")
        self.browse_button.config(state="disabled")
        self.progress_var.set("🔄 正在分析文件，请稍候...")

        # 清空之前的结果
        self.result_text.delete("1.0", tk.END)
        # 只清空图表显示区域，不清空控制按钮
        if hasattr(self, 'chart_display_frame'):
            for widget in self.chart_display_frame.winfo_children():
                widget.destroy()

        self.analysis_thread = threading.Thread(target=self.analyze_file, args=(file_path, word_count))
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
    
    def analyze_file(self, file_path, word_count):
        try:
            # 更新状态
            self.root.after(0, lambda: self.progress_var.set("📖 正在解析RIS文件..."))

            # 解析RIS文件
            self.titles = self.parse_ris_file(file_path)

            if not self.titles:
                self.root.after(0, lambda: messagebox.showerror("❌ 错误", "未找到任何标题，请检查文件格式是否正确"))
                return

            # 更新状态
            self.root.after(0, lambda: self.progress_var.set(f"🔍 正在分析 {len(self.titles)} 个标题的词频..."))

            # 词频分析（使用用户设定的词汇数量）
            self.word_counts = self.analyze_word_frequency(self.titles, word_count)

            if not self.word_counts:
                self.root.after(0, lambda: messagebox.showwarning("⚠️ 警告", "未能提取到有效词汇，请检查文件内容或调整停用词设置"))
                return

            # 更新UI
            self.root.after(0, self.update_results)

        except Exception as e:
            error_msg = f"分析过程中出错: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("❌ 错误", error_msg))
        finally:
            self.root.after(0, self.analysis_complete)

    def analysis_complete(self):
        self.analyze_button.config(state="normal")
        self.browse_button.config(state="normal")

        if self.word_counts:
            # 启用保存按钮
            try:
                self.save_txt_button.config(state="normal")
                self.save_csv_button.config(state="normal")
                if hasattr(self, 'download_chart_button'):
                    self.download_chart_button.config(state="normal")
            except Exception as e:
                print(f"按钮状态更新错误: {e}")
            self.progress_var.set(f"✅ 分析完成！找到 {len(self.word_counts)} 个高频词汇")
        else:
            self.progress_var.set("❌ 分析失败")
    
    def update_results(self):
        # 更新词频列表
        self.result_text.delete("1.0", tk.END)

        # 创建美观的结果显示
        result_text = "✨ 词频分析结果\n"
        result_text += "═" * 60 + "\n\n"
        result_text += f"� 解析标题数量: {len(self.titles):,} 个\n"
        result_text += f"🔍 高频词汇数量: {len(self.word_counts)} 个\n"

        if self.custom_stop_words:
            result_text += f"🚫 自定义停用词: {len(self.custom_stop_words)} 个\n"

        result_text += "\n" + "🏆 词频排行榜" + "\n"
        result_text += "─" * 60 + "\n"

        for i, (word, count) in enumerate(self.word_counts, 1):
            # 添加排名图标
            if i == 1:
                icon = "🥇"
                result_text += f"{icon} {word:<25} : {count:4d} 次\n"
            elif i == 2:
                icon = "🥈"
                result_text += f"{icon} {word:<25} : {count:4d} 次\n"
            elif i == 3:
                icon = "🥉"
                result_text += f"{icon} {word:<25} : {count:4d} 次\n"
            else:
                result_text += f"{i:2d}. {word:<24} : {count:4d} 次\n"

        result_text += "\n" + "─" * 60 + "\n"
        result_text += "💡 提示: 可以在左侧添加自定义停用词来过滤不需要的词汇\n"
        result_text += "📊 图表会根据设定的词汇数量动态调整尺寸和布局\n"

        self.result_text.insert("1.0", result_text)

        # 更新图表
        self.update_chart()
    
    def update_chart(self):
        # 清除之前的图表
        if hasattr(self, 'chart_display_frame'):
            for widget in self.chart_display_frame.winfo_children():
                widget.destroy()

        if not self.word_counts:
            # 显示空状态
            empty_label = ttk.Label(self.chart_display_frame, text="📈 暂无图表数据",
                                   font=('Arial', 14), foreground='#7f8c8d')
            empty_label.pack(expand=True)
            return

        try:
            # 设置中文字体支持 - 参考原始版本
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False

            # 获取用户设定的词汇数量
            try:
                user_count = int(self.word_count_var.get())
            except:
                user_count = 50  # 默认值
            display_count = min(user_count, len(self.word_counts))

            # 创建图表 - 参考原始版本的固定尺寸
            fig, ax = plt.subplots(figsize=(15, 8))
            fig.patch.set_facecolor('white')

            if display_count == 0:
                raise Exception("没有词汇数据可显示")

            words, counts = zip(*self.word_counts[:display_count])

            # 创建柱状图 - 使用原始版本的简洁样式
            bars = ax.bar(words, counts, color='skyblue', alpha=0.7)

            # 在柱状图上显示数值 - 参考原始版本
            for bar, count in zip(bars, counts):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                       str(count), ha='center', va='bottom', fontsize=10)

            # 设置标签和标题 - 参考原始版本，移除加粗
            ax.set_xticks(range(len(words)))
            ax.set_xticklabels(words, rotation=45, ha='right', fontsize=12)
            ax.set_title('标题词频分布 (Title Word Frequency)', fontsize=16)
            ax.set_xlabel('词语 (Words)', fontsize=14)
            ax.set_ylabel('频次 (Frequency)', fontsize=14)

            # 添加网格 - 参考原始版本
            ax.grid(axis='y', alpha=0.3)

            # 调整布局，确保标题和标签完整显示
            plt.tight_layout(pad=3.0)  # 增加边距
            plt.subplots_adjust(top=0.9, bottom=0.2)  # 为标题和X轴标签留出空间

            # 将图表嵌入到tkinter中 - 简化版本
            self.chart_canvas = FigureCanvasTkAgg(fig, self.chart_display_frame)
            self.chart_canvas.draw()

            # 获取图表widget
            canvas_widget = self.chart_canvas.get_tk_widget()

            # 简单的显示方式：让图表适应窗口，但保持宽高比
            canvas_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # 保存图表对象以便下载
            self.current_figure = fig

        except Exception as e:
            # 如果图表创建失败，显示错误信息
            error_label = ttk.Label(self.chart_display_frame, text=f"❌ 图表生成失败: {str(e)}",
                                   font=('Arial', 12), foreground='#e74c3c')
            error_label.pack(expand=True)

    def parse_ris_file(self, file_path):
        """解析RIS文件并提取标题"""
        titles = []
        current_title = ""
        in_title = False

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()

                    if line.startswith('TI  - '):  # 标题开始行
                        current_title = line[6:].strip()
                        in_title = True
                    elif in_title and line and not line.startswith(('TY  -', 'AU  -', 'PY  -', 'T2  -', 'VL  -', 'IS  -', 'SP  -', 'EP  -', 'DO  -', 'UR  -', 'AB  -', 'KW  -', 'M3  -', 'DB  -', 'N1  -', 'ER  -', 'C7  -', 'ST  -')):
                        # 标题可能跨多行，继续添加
                        current_title += " " + line
                    elif line.startswith('ER  - ') or (in_title and line.startswith(('AU  -', 'PY  -', 'T2  -', 'AB  -'))):  # 记录结束或其他字段开始
                        if current_title:
                            # 清理标题，移除多余空格
                            clean_title = ' '.join(current_title.split())
                            titles.append(clean_title)
                        current_title = ""
                        in_title = False

                # 处理文件末尾没有ER标记的情况
                if current_title:
                    clean_title = ' '.join(current_title.split())
                    titles.append(clean_title)

        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    for line in file:
                        line = line.strip()

                        if line.startswith('TI  - '):
                            current_title = line[6:].strip()
                            in_title = True
                        elif in_title and line and not line.startswith(('TY  -', 'AU  -', 'PY  -', 'T2  -', 'VL  -', 'IS  -', 'SP  -', 'EP  -', 'DO  -', 'UR  -', 'AB  -', 'KW  -', 'M3  -', 'DB  -', 'N1  -', 'ER  -', 'C7  -', 'ST  -')):
                            current_title += " " + line
                        elif line.startswith('ER  - ') or (in_title and line.startswith(('AU  -', 'PY  -', 'T2  -', 'AB  -'))):
                            if current_title:
                                clean_title = ' '.join(current_title.split())
                                titles.append(clean_title)
                            current_title = ""
                            in_title = False

                    if current_title:
                        clean_title = ' '.join(current_title.split())
                        titles.append(clean_title)
            except Exception as e:
                raise Exception(f"无法读取文件: {e}")
        except Exception as e:
            raise Exception(f"解析文件时出错: {e}")

        return titles

    def normalize_word(self, word):
        """词形规范化：将复数形式转换为单数形式"""
        # 处理常见的复数形式
        if word.endswith('ies') and len(word) > 4:
            # studies -> study, theories -> theory
            return word[:-3] + 'y'
        elif word.endswith('es') and len(word) > 3:
            # processes -> process, analyses -> analysis
            if word.endswith('ses'):
                return word[:-2]  # analyses -> analysis
            elif word.endswith('ches') or word.endswith('shes') or word.endswith('xes'):
                return word[:-2]  # approaches -> approach
            else:
                return word[:-1]  # nodes -> node
        elif word.endswith('s') and len(word) > 3:
            # systems -> system, networks -> network
            # 但要避免误处理以s结尾的单数词
            if not word.endswith(('ss', 'us', 'is', 'as', 'os')):
                return word[:-1]

        return word

    def analyze_word_frequency(self, titles, top_n=50):
        """分析标题中的词频"""
        # 学术文章标题专用停用词列表
        base_stop_words = {
            # 基础功能词
            'a', 'an', 'the', 'and', 'or', 'but', 'if', 'of', 'at', 'by',
            'for', 'with', 'about', 'to', 'from', 'in', 'on', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'can', 'this', 'that', 'these', 'those',

            # 代词
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their',

            # 疑问词和副词
            'what', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how',

            # 量词和限定词
            'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',

            # 常见副词和介词
            'just', 'now', 'also', 'as', 'up', 'out', 'down', 'off', 'over', 'under',
            'again', 'further', 'then', 'once', 'here', 'there', 'into', 'onto',
            'upon', 'within', 'without', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'among',

            # 学术标题中常见但信息量较低的词汇
            'study', 'studies', 'research', 'investigation', 'paper', 'article',
            'review', 'survey', 'overview', 'introduction', 'conclusion',
            'case', 'cases', 'example', 'examples', 'method', 'methods',
            'approach', 'approaches', 'technique', 'techniques', 'way', 'ways',
            'new', 'novel', 'improved', 'enhanced', 'advanced', 'modern',
            'recent', 'current', 'latest', 'state', 'art', 'based', 'using',
            'via', 'through', 'toward', 'towards', 'into', 'onto', 'upon'
        }

        # 合并基础停用词和用户自定义停用词
        stop_words = base_stop_words.union(self.custom_stop_words)

        # 使用简单的空格分词
        all_words = []

        for title in titles:
            # 转小写，移除标点符号，保留字母、数字和空格
            clean_title = re.sub(r'[^\w\s]', ' ', title.lower())
            # 分词
            words = clean_title.split()
            # 过滤并规范化：只保留字母单词，长度大于2，不在停用词中，然后进行词形规范化
            filtered_words = []
            for word in words:
                if word.isalpha() and len(word) > 2 and word not in stop_words:
                    normalized_word = self.normalize_word(word)
                    # 再次检查规范化后的词是否在停用词中
                    if normalized_word not in stop_words:
                        filtered_words.append(normalized_word)
            all_words.extend(filtered_words)

        # 计算词频
        word_counts = Counter(all_words)
        most_common = word_counts.most_common(top_n)

        return most_common

    def save_results(self, format_type='txt'):
        """保存分析结果 - 支持多种格式"""
        if not self.word_counts:
            messagebox.showwarning("⚠️ 警告", "没有分析结果可保存")
            return

        # 根据格式类型设置文件扩展名和过滤器
        format_config = {
            'txt': {
                'extension': '.txt',
                'filetypes': [("文本文件", "*.txt"), ("所有文件", "*.*")],
                'title': '保存为文本文件'
            },
            'csv': {
                'extension': '.csv',
                'filetypes': [("CSV文件", "*.csv"), ("所有文件", "*.*")],
                'title': '保存为CSV文件'
            }
        }

        config = format_config.get(format_type, format_config['txt'])

        filename = filedialog.asksaveasfilename(
            title=config['title'],
            defaultextension=config['extension'],
            filetypes=config['filetypes']
        )

        if filename:
            try:
                if format_type == 'csv':
                    self._save_csv(filename)
                else:
                    self._save_txt(filename)

                messagebox.showinfo("✅ 成功", f"结果已保存到:\n{filename}")
            except Exception as e:
                messagebox.showerror("❌ 错误", f"保存失败: {str(e)}")

    def _save_txt(self, filename):
        """保存为文本格式"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("📊 RIS文件标题词频分析结果\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"📅 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"📋 解析标题数量: {len(self.titles):,} 个\n")
            f.write(f"🔍 高频词汇数量: {len(self.word_counts)} 个\n")

            if self.custom_stop_words:
                f.write(f"🚫 自定义停用词: {len(self.custom_stop_words)} 个\n")

            f.write("\n🏆 词频排行榜\n")
            f.write("-" * 50 + "\n")

            for i, (word, count) in enumerate(self.word_counts, 1):
                if i <= 3:
                    icons = ["🥇", "🥈", "🥉"]
                    icon = icons[i-1]
                    f.write(f"{icon} {word:<25} : {count:4d} 次\n")
                else:
                    f.write(f"{i:2d}. {word:<24} : {count:4d} 次\n")

    def _save_csv(self, filename):
        """保存为CSV格式"""
        import csv
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['Rank', 'Word', 'Frequency'])  # 使用英文标题避免乱码
            for i, (word, count) in enumerate(self.word_counts, 1):
                writer.writerow([i, word, count])

    def download_chart(self):
        """下载图表为图片文件"""
        if not hasattr(self, 'current_figure') or self.current_figure is None:
            messagebox.showwarning("⚠️ 警告", "没有可下载的图表")
            return

        filename = filedialog.asksaveasfilename(
            title="保存图表",
            defaultextension=".png",
            filetypes=[
                ("PNG图片", "*.png"),
                ("JPG图片", "*.jpg"),
                ("PDF文件", "*.pdf"),
                ("SVG矢量图", "*.svg"),
                ("所有文件", "*.*")
            ]
        )

        if filename:
            try:
                # 根据文件扩展名确定格式
                file_ext = filename.lower().split('.')[-1]
                if file_ext in ['png', 'jpg', 'jpeg', 'pdf', 'svg']:
                    # 设置高分辨率
                    dpi = 300 if file_ext in ['png', 'jpg', 'jpeg'] else None
                    self.current_figure.savefig(filename, dpi=dpi, bbox_inches='tight',
                                              facecolor='white', edgecolor='none')
                    messagebox.showinfo("✅ 成功", f"图表已保存到:\n{filename}")
                else:
                    messagebox.showerror("❌ 错误", "不支持的文件格式")
            except Exception as e:
                messagebox.showerror("❌ 错误", f"保存图表失败: {str(e)}")

    def on_closing(self):
        """处理窗口关闭事件"""
        try:
            # 如果有分析线程正在运行，等待其完成或强制退出
            if self.analysis_thread and self.analysis_thread.is_alive():
                # daemon线程会自动结束
                pass

            # 销毁窗口并退出程序
            self.root.quit()
            self.root.destroy()

        except Exception:
            # 如果出现任何错误，强制退出
            import sys
            sys.exit(0)


def main():
    root = tk.Tk()
    RISAnalyzerGUI(root)  # 创建应用实例
    root.mainloop()

if __name__ == "__main__":
    main()
