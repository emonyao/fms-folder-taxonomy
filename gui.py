import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import yaml
from datetime import datetime
import subprocess
import queue

# 添加scripts目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.config import load_config
from scripts.renamer import ImageRenamer
from scripts.scanner import ImageScanner
from scripts.logger import RenameLogger

class FMSFolderTaxonomyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FMS Folder Taxonomy - 图像重命名工具")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 设置图标（如果有的话）
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
        
        # 创建消息队列用于线程间通信
        self.message_queue = queue.Queue()
        
        # 加载配置
        self.config = self.load_config()
        
        # 创建界面
        self.create_widgets()
        
        # 定期检查消息队列
        self.check_message_queue()
        
    def load_config(self):
        """加载配置文件"""
        try:
            return load_config("config.yaml")
        except Exception as e:
            messagebox.showerror("错误", f"无法加载配置文件: {e}")
            return {
                "input_folder": "images/",
                "output_renamed": "output/renamed/",
                "output_dnu": "output/dnu/",
                "output_review": "output/review/",
                "log_file": "output/rename_log.csv"
            }
    
    def save_config(self):
        """保存配置文件"""
        try:
            config_data = {
                "input_folder": self.input_folder_var.get(),
                "output_renamed": self.output_renamed_var.get(),
                "output_dnu": self.output_dnu_var.get(),
                "output_review": self.output_review_var.get(),
                "log_file": self.log_file_var.get(),
                "use_ai": self.use_ai_var.get(),
                "ai_confidence_threshold": float(self.ai_threshold_var.get()),
                "ai_source": self.ai_source_var.get(),
                "default_version": int(self.default_version_var.get()),
                "version_format": self.version_format_var.get(),
                "publish_values": ["yes", "y", "true"]
            }
            
            with open("config.yaml", "w", encoding="utf-8") as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            
            messagebox.showinfo("成功", "配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="FMS Folder Taxonomy", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 创建选项卡
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 主操作选项卡
        main_tab = ttk.Frame(notebook)
        notebook.add(main_tab, text="主操作")
        
        # 配置选项卡
        config_tab = ttk.Frame(notebook)
        notebook.add(config_tab, text="配置")
        
        # 日志选项卡
        log_tab = ttk.Frame(notebook)
        notebook.add(log_tab, text="日志")
        
        # 设置主操作选项卡
        self.setup_main_tab(main_tab)
        
        # 设置配置选项卡
        self.setup_config_tab(config_tab)
        
        # 设置日志选项卡
        self.setup_log_tab(log_tab)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 配置网格权重
        main_frame.rowconfigure(1, weight=1)
    
    def setup_main_tab(self, parent):
        """设置主操作选项卡"""
        # 输入输出目录框架
        dir_frame = ttk.LabelFrame(parent, text="目录设置", padding="10")
        dir_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
        
        # 输入目录
        ttk.Label(dir_frame, text="输入目录:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.input_folder_var = tk.StringVar(value=self.config.get("input_folder", "images/"))
        input_entry = ttk.Entry(dir_frame, textvariable=self.input_folder_var, width=50)
        input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(dir_frame, text="浏览", command=self.browse_input_folder).grid(row=0, column=2, pady=2)
        
        # 输出目录
        ttk.Label(dir_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.output_renamed_var = tk.StringVar(value=self.config.get("output_renamed", "output/renamed/"))
        output_entry = ttk.Entry(dir_frame, textvariable=self.output_renamed_var, width=50)
        output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(dir_frame, text="浏览", command=self.browse_output_folder).grid(row=1, column=2, pady=2)
        
        # 操作按钮框架
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=1, column=0, columnspan=2, pady=20)
        
        # 扫描按钮
        self.scan_btn = ttk.Button(button_frame, text="扫描图像", 
                                  command=self.scan_images, style="Accent.TButton")
        self.scan_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 重命名按钮
        self.rename_btn = ttk.Button(button_frame, text="开始重命名", 
                                    command=self.start_rename, style="Accent.TButton")
        self.rename_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 预览按钮
        self.preview_btn = ttk.Button(button_frame, text="预览重命名", 
                                     command=self.preview_rename)
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 打开输出目录按钮
        self.open_output_btn = ttk.Button(button_frame, text="打开输出目录", 
                                         command=self.open_output_folder)
        self.open_output_btn.pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(parent, variable=self.progress_var, 
                                           maximum=100, mode='determinate')
        self.progress_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(parent, text="操作日志", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)
    
    def setup_config_tab(self, parent):
        """设置配置选项卡"""
        # 创建滚动框架
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 目录配置框架
        dir_config_frame = ttk.LabelFrame(scrollable_frame, text="目录配置", padding="10")
        dir_config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_config_frame.columnconfigure(1, weight=1)
        
        # DNU输出目录
        ttk.Label(dir_config_frame, text="DNU输出目录:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.output_dnu_var = tk.StringVar(value=self.config.get("output_dnu", "output/dnu/"))
        dnu_entry = ttk.Entry(dir_config_frame, textvariable=self.output_dnu_var, width=50)
        dnu_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(dir_config_frame, text="浏览", command=self.browse_dnu_folder).grid(row=0, column=2, pady=2)
        
        # Review输出目录
        ttk.Label(dir_config_frame, text="Review输出目录:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.output_review_var = tk.StringVar(value=self.config.get("output_review", "output/review/"))
        review_entry = ttk.Entry(dir_config_frame, textvariable=self.output_review_var, width=50)
        review_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(dir_config_frame, text="浏览", command=self.browse_review_folder).grid(row=1, column=2, pady=2)
        
        # 日志文件
        ttk.Label(dir_config_frame, text="日志文件:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.log_file_var = tk.StringVar(value=self.config.get("log_file", "output/rename_log.csv"))
        log_entry = ttk.Entry(dir_config_frame, textvariable=self.log_file_var, width=50)
        log_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(dir_config_frame, text="浏览", command=self.browse_log_file).grid(row=2, column=2, pady=2)
        
        # AI配置框架
        ai_config_frame = ttk.LabelFrame(scrollable_frame, text="AI配置", padding="10")
        ai_config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ai_config_frame.columnconfigure(1, weight=1)
        
        # 启用AI
        self.use_ai_var = tk.BooleanVar(value=self.config.get("use_ai", True))
        ttk.Checkbutton(ai_config_frame, text="启用AI fallback", 
                       variable=self.use_ai_var).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # AI置信度阈值
        ttk.Label(ai_config_frame, text="AI置信度阈值:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.ai_threshold_var = tk.StringVar(value=str(self.config.get("ai_confidence_threshold", 0.8)))
        ttk.Entry(ai_config_frame, textvariable=self.ai_threshold_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # AI源
        ttk.Label(ai_config_frame, text="AI源:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.ai_source_var = tk.StringVar(value=self.config.get("ai_source", "deepseek"))
        ai_source_combo = ttk.Combobox(ai_config_frame, textvariable=self.ai_source_var, 
                                      values=["deepseek", "blip"], state="readonly", width=20)
        ai_source_combo.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # 版本配置框架
        version_config_frame = ttk.LabelFrame(scrollable_frame, text="版本配置", padding="10")
        version_config_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        version_config_frame.columnconfigure(1, weight=1)
        
        # 默认版本
        ttk.Label(version_config_frame, text="默认版本:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.default_version_var = tk.StringVar(value=str(self.config.get("default_version", 1)))
        ttk.Entry(version_config_frame, textvariable=self.default_version_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # 版本格式
        ttk.Label(version_config_frame, text="版本格式:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.version_format_var = tk.StringVar(value=self.config.get("version_format", "_v{n}"))
        ttk.Entry(version_config_frame, textvariable=self.version_format_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # 保存按钮
        save_btn = ttk.Button(scrollable_frame, text="保存配置", 
                             command=self.save_config, style="Accent.TButton")
        save_btn.grid(row=3, column=0, pady=20)
        
        # 配置网格权重
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
    
    def setup_log_tab(self, parent):
        """设置日志选项卡"""
        # 日志显示区域
        log_frame = ttk.Frame(parent)
        log_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)
        
        # 按钮框架
        button_frame = ttk.Frame(log_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(button_frame, text="刷新日志", command=self.refresh_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="导出日志", command=self.export_log).pack(side=tk.LEFT)
        
        # 日志文本区域
        self.log_display = scrolledtext.ScrolledText(log_frame, height=25, width=80)
        self.log_display.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # 加载初始日志
        self.refresh_log()
    
    def browse_input_folder(self):
        """浏览输入目录"""
        folder = filedialog.askdirectory(title="选择输入目录")
        if folder:
            self.input_folder_var.set(folder)
    
    def browse_output_folder(self):
        """浏览输出目录"""
        folder = filedialog.askdirectory(title="选择输出目录")
        if folder:
            self.output_renamed_var.set(folder)
    
    def browse_dnu_folder(self):
        """浏览DNU输出目录"""
        folder = filedialog.askdirectory(title="选择DNU输出目录")
        if folder:
            self.output_dnu_var.set(folder)
    
    def browse_review_folder(self):
        """浏览Review输出目录"""
        folder = filedialog.askdirectory(title="选择Review输出目录")
        if folder:
            self.output_review_var.set(folder)
    
    def browse_log_file(self):
        """浏览日志文件"""
        file = filedialog.asksaveasfilename(title="选择日志文件", 
                                          defaultextension=".csv",
                                          filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file:
            self.log_file_var.set(file)
    
    def scan_images(self):
        """扫描图像"""
        def scan_thread():
            try:
                self.log_message("开始扫描图像...")
                self.status_var.set("正在扫描图像...")
                
                # 更新配置
                self.update_config()
                
                # 创建扫描器
                scanner = ImageScanner("config.yaml")
                image_paths = scanner.scan_image_paths()
                
                self.log_message(f"扫描完成，找到 {len(image_paths)} 个图像文件")
                self.status_var.set(f"扫描完成，找到 {len(image_paths)} 个图像文件")
                
            except Exception as e:
                self.log_message(f"扫描失败: {e}")
                self.status_var.set("扫描失败")
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def start_rename(self):
        """开始重命名"""
        def rename_thread():
            try:
                self.log_message("开始重命名图像...")
                self.status_var.set("正在重命名图像...")
                self.progress_var.set(0)
                
                # 更新配置
                self.update_config()
                
                # 创建重命名器
                renamer = ImageRenamer("config.yaml")
                renamer.rename_images(dry_run=False)
                
                self.log_message("重命名完成")
                self.status_var.set("重命名完成")
                self.progress_var.set(100)
                
            except Exception as e:
                self.log_message(f"重命名失败: {e}")
                self.status_var.set("重命名失败")
        
        threading.Thread(target=rename_thread, daemon=True).start()
    
    def preview_rename(self):
        """预览重命名"""
        def preview_thread():
            try:
                self.log_message("开始预览重命名...")
                self.status_var.set("正在预览重命名...")
                self.progress_var.set(0)
                
                # 更新配置
                self.update_config()
                
                # 创建重命名器
                renamer = ImageRenamer("config.yaml")
                renamer.rename_images(dry_run=True)
                
                self.log_message("预览完成")
                self.status_var.set("预览完成")
                self.progress_var.set(100)
                
            except Exception as e:
                self.log_message(f"预览失败: {e}")
                self.status_var.set("预览失败")
        
        threading.Thread(target=preview_thread, daemon=True).start()
    
    def open_output_folder(self):
        """打开输出目录"""
        output_dir = self.output_renamed_var.get()
        if os.path.exists(output_dir):
            if sys.platform == "win32":
                os.startfile(output_dir)
            elif sys.platform == "darwin":
                subprocess.run(["open", output_dir])
            else:
                subprocess.run(["xdg-open", output_dir])
        else:
            messagebox.showwarning("警告", "输出目录不存在")
    
    def update_config(self):
        """更新配置"""
        try:
            config_data = {
                "input_folder": self.input_folder_var.get(),
                "output_renamed": self.output_renamed_var.get(),
                "output_dnu": self.output_dnu_var.get(),
                "output_review": self.output_review_var.get(),
                "log_file": self.log_file_var.get(),
                "use_ai": self.use_ai_var.get(),
                "ai_confidence_threshold": float(self.ai_threshold_var.get()),
                "ai_source": self.ai_source_var.get(),
                "default_version": int(self.default_version_var.get()),
                "version_format": self.version_format_var.get(),
                "publish_values": ["yes", "y", "true"]
            }
            
            with open("config.yaml", "w", encoding="utf-8") as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                
        except Exception as e:
            self.log_message(f"更新配置失败: {e}")
    
    def log_message(self, message):
        """记录日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # 添加到消息队列
        self.message_queue.put(log_entry)
    
    def check_message_queue(self):
        """检查消息队列"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                self.log_text.insert(tk.END, message)
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        
        # 每100ms检查一次
        self.root.after(100, self.check_message_queue)
    
    def refresh_log(self):
        """刷新日志显示"""
        try:
            log_file = self.log_file_var.get()
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.read()
                self.log_display.delete(1.0, tk.END)
                self.log_display.insert(1.0, content)
            else:
                self.log_display.delete(1.0, tk.END)
                self.log_display.insert(1.0, "日志文件不存在")
        except Exception as e:
            self.log_display.delete(1.0, tk.END)
            self.log_display.insert(1.0, f"读取日志失败: {e}")
    
    def clear_log(self):
        """清空日志"""
        if messagebox.askyesno("确认", "确定要清空日志吗？"):
            try:
                log_file = self.log_file_var.get()
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write("")
                self.refresh_log()
                messagebox.showinfo("成功", "日志已清空")
            except Exception as e:
                messagebox.showerror("错误", f"清空日志失败: {e}")
    
    def export_log(self):
        """导出日志"""
        file = filedialog.asksaveasfilename(title="导出日志", 
                                          defaultextension=".txt",
                                          filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file:
            try:
                content = self.log_display.get(1.0, tk.END)
                with open(file, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("成功", "日志已导出")
            except Exception as e:
                messagebox.showerror("错误", f"导出日志失败: {e}")

def main():
    root = tk.Tk()
    app = FMSFolderTaxonomyGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 