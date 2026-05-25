import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import re
import os
import threading
import mmap

def split_hex_line(line):
    hex_str = re.sub(r'\s+', '', line.strip())
    values = []
    for i in range(0, len(hex_str), 8):
        chunk = hex_str[i:i+8]
        if len(chunk) == 8:
            values.append(chunk)
    return values

def extract_mrgb_colors_mmap(input_path, log_func):
    mrgb_marker = b"#MRGB"
    colors = []

    try:
        with open(input_path, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                inside_mrgb = False
                line = mm.readline()

                while line:
                    try:
                        decoded = line.decode('utf-8', errors='replace').strip()
                    except Exception:
                        decoded = ''

                    if decoded.startswith('#MRGB'):
                        inside_mrgb = True
                        data_part = decoded[5:].strip()
                        if data_part:
                            colors.extend(split_hex_line(data_part))
                        line = mm.readline()
                        continue

                    if inside_mrgb:
                        if decoded == '' or decoded.startswith('#'):
                            log_func(f"颜色提取完成，共 {len(colors)} 个颜色值")
                            return colors
                        else:
                            colors.extend(split_hex_line(decoded))

                    line = mm.readline()

                log_func(f"颜色提取完成，共 {len(colors)} 个颜色值")
                return colors
    except Exception as e:
        log_func(f"提取颜色失败：{e}")
        return None

def convert_mrgb_stream(input_path, output_path, log_func=print, progress_func=None):
    log_func("第一阶段：提取MRGB颜色数据...")
    colors = extract_mrgb_colors_mmap(input_path, log_func)
    if colors is None:
        return False
    if not colors:
        log_func("错误：未找到有效的MRGB颜色数据。")
        return False

    rgb_floats = []
    for hex_str in colors:
        if len(hex_str) == 8:
            try:
                rr = int(hex_str[2:4], 16)
                gg = int(hex_str[4:6], 16)
                bb = int(hex_str[6:8], 16)
                rgb_floats.append((rr / 255.0, gg / 255.0, bb / 255.0))
            except ValueError:
                pass

    log_func(f"颜色数据准备完成：{len(rgb_floats)} 个有效颜色")

    log_func("第二阶段：mmap 流式转换顶点色...")
    total_size = os.path.getsize(input_path)

    try:
        with open(input_path, 'rb') as infile, \
             open(output_path, 'wb', buffering=1024 * 1024) as outfile:
            with mmap.mmap(infile.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                color_idx = 0
                vertex_count = 0
                stripped_mtl_lines = 0
                write_buffer = []
                BUFFER_SIZE = 50000
                last_progress_pos = 0
                PROGRESS_INTERVAL = 10 * 1024 * 1024

                line = mm.readline()
                while line:
                    if len(line) >= 2 and line[:2] == b'v ':
                        line_str = line.decode('utf-8', errors='replace').rstrip('\n\r')
                        parts = line_str.split()
                        if len(parts) >= 4 and color_idx < len(rgb_floats):
                            x, y, z = parts[1], parts[2], parts[3]
                            r, g, b = rgb_floats[color_idx]
                            write_buffer.append(
                                f"v {x} {y} {z} {r:.6f} {g:.6f} {b:.6f}\n".encode()
                            )
                            color_idx += 1
                            vertex_count += 1
                        else:
                            write_buffer.append(line)
                    elif line.startswith(b'mtllib ') or line.startswith(b'usemtl '):
                        stripped_mtl_lines += 1
                    else:
                        write_buffer.append(line)

                    if len(write_buffer) >= BUFFER_SIZE:
                        outfile.writelines(write_buffer)
                        write_buffer.clear()

                    current_pos = mm.tell()
                    if current_pos - last_progress_pos >= PROGRESS_INTERVAL:
                        if progress_func:
                            progress_func(current_pos, total_size)
                        last_progress_pos = current_pos

                    line = mm.readline()

                if write_buffer:
                    outfile.writelines(write_buffer)

                if progress_func:
                    progress_func(total_size, total_size)

        log_func(f"转换完成！处理顶点数：{vertex_count}，去掉MTL引用：{stripped_mtl_lines}行")
        log_func(f"文件已保存至：\n{output_path}")
        return True
    except Exception as e:
        log_func(f"转换失败：{e}")
        import traceback
        log_func(traceback.format_exc())
        return False


class MRGBConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ZBrush顶点色转通用顶点色")
        self.root.geometry("700x500")
        self.root.resizable(True, True)

        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()

        frame_in = tk.Frame(self.root)
        frame_in.pack(pady=10, padx=20, fill=tk.X)
        tk.Label(frame_in, text="输入 OBJ 文件：").pack(side=tk.LEFT)
        tk.Entry(frame_in, textvariable=self.input_path, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_in, text="浏览...", command=self.select_input).pack(side=tk.LEFT)

        frame_out = tk.Frame(self.root)
        frame_out.pack(pady=10, padx=20, fill=tk.X)
        tk.Label(frame_out, text="输出 OBJ 文件：").pack(side=tk.LEFT)
        tk.Entry(frame_out, textvariable=self.output_path, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_out, text="浏览...", command=self.select_output).pack(side=tk.LEFT)
        tk.Label(self.root, text='不指定输出路径时，自动在输入同目录生成 "_vertexcolor.obj"', fg="gray").pack(anchor='w', padx=25)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(pady=10, padx=20, fill=tk.X)
        self.progress_label = tk.Label(self.root, text="就绪", fg="gray")
        self.progress_label.pack()

        self.btn_convert = tk.Button(self.root, text="开始转换", command=self.start_conversion,
                                     bg="#4CAF50", fg="white", font=("微软雅黑", 12, "bold"),
                                     height=1, width=15)
        self.btn_convert.pack(pady=10)

        self.log_area = scrolledtext.ScrolledText(self.root, height=14, state='normal', wrap=tk.WORD)
        self.log_area.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    def select_input(self):
        path = filedialog.askopenfilename(filetypes=[("OBJ files", "*.obj"), ("All files", "*.*")])
        if path:
            self.input_path.set(path)
            if not self.output_path.get():
                dir_name = os.path.dirname(path)
                base_name = os.path.splitext(os.path.basename(path))[0]
                default_out = os.path.join(dir_name, f"{base_name}_vertexcolor.obj")
                self.output_path.set(default_out)

    def select_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".obj",
                                            filetypes=[("OBJ files", "*.obj"), ("All files", "*.*")])
        if path:
            self.output_path.set(path)

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.root.update_idletasks()

    def update_progress(self, current_bytes, total_bytes):
        if total_bytes > 0:
            pct = min((current_bytes / total_bytes) * 100, 100)
            self.progress_var.set(pct)
            cur_mb = current_bytes // (1024 * 1024)
            tot_mb = total_bytes // (1024 * 1024)
            self.progress_label.config(text=f"转换进度：{pct:.1f}% ({cur_mb}MB / {tot_mb}MB)")
            self.root.update_idletasks()

    def start_conversion(self):
        input_file = self.input_path.get()
        output_file = self.output_path.get()

        if not input_file:
            messagebox.showwarning("提示", "请先选择输入文件。")
            return
        if not os.path.exists(input_file):
            messagebox.showerror("错误", "输入文件不存在。")
            return

        if not output_file:
            dir_name = os.path.dirname(input_file)
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(dir_name, f"{base_name}_vertexcolor.obj")
            self.output_path.set(output_file)

        self.btn_convert.config(state='disabled', text="转换中...")
        self.log_area.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.progress_label.config(text="提取颜色数据...")
        self.log("=== ZBrush顶点色转通用顶点色 ===")
        self.log(f"输入文件：{input_file}")

        def task():
            success = convert_mrgb_stream(
                input_file, output_file,
                log_func=self.log,
                progress_func=self.update_progress
            )
            self.root.after(0, self.on_conversion_finished, success)

        threading.Thread(target=task, daemon=True).start()

    def on_conversion_finished(self, success):
        self.btn_convert.config(state='normal', text="开始转换")
        if success:
            self.progress_var.set(100)
            self.progress_label.config(text="转换完成！")
            messagebox.showinfo("完成", "转换成功！\n文件已保存至：\n" + self.output_path.get())
        else:
            self.progress_label.config(text="转换失败")
            messagebox.showerror("失败", "转换失败，请查看日志信息。")


if __name__ == "__main__":
    root = tk.Tk()
    app = MRGBConverterApp(root)
    root.mainloop()
