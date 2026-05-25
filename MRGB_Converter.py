import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re
import os
import threading

# ---------- 转换核心（与你之前用的脚本完全一致）----------
def split_hex_line(line):
    hex_str = re.sub(r'\s+', '', line.strip())
    values = []
    for i in range(0, len(hex_str), 8):
        chunk = hex_str[i:i+8]
        if len(chunk) == 8:
            values.append(chunk)
        else:
            # GUI中不print，可以忽略，此处保留但不输出
            pass
    return values

def convert_mrgb_to_vertex_color(input_path, output_path, log_func=print):
    try:
        with open(input_path, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        log_func(f"读取文件失败：{e}")
        return False

    vertex_lines = []
    other_lines = []
    mrgb_values = []
    inside_mrgb = False
    mrgb_header = "#MRGB"

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(mrgb_header):
            inside_mrgb = True
            data_part = stripped[len(mrgb_header):].strip()
            if data_part:
                mrgb_values.extend(split_hex_line(data_part))
            continue

        if inside_mrgb:
            if stripped == '' or stripped.startswith('#'):
                inside_mrgb = False
            else:
                mrgb_values.extend(split_hex_line(stripped))
                continue

        if line.startswith('v '):
            parts = line.split()
            if len(parts) >= 4:
                x, y, z = parts[1], parts[2], parts[3]
                vertex_lines.append((len(vertex_lines), x, y, z))
                other_lines.append(f"v {x} {y} {z}\n")
            else:
                other_lines.append(line)
        else:
            other_lines.append(line)

    if not mrgb_values:
        log_func("错误：未找到有效的MRGB颜色数据。")
        return False

    if len(mrgb_values) != len(vertex_lines):
        log_func(f"警告：顶点数 ({len(vertex_lines)}) 与颜色数 ({len(mrgb_values)}) 不一致，转换可能错位。")

    rgb_floats = []
    for hex_str in mrgb_values:
        if len(hex_str) != 8:
            continue
        try:
            rr = int(hex_str[2:4], 16)
            gg = int(hex_str[4:6], 16)
            bb = int(hex_str[6:8], 16)
        except ValueError:
            continue
        r = rr / 255.0
        g = gg / 255.0
        b = bb / 255.0
        rgb_floats.append((r, g, b))

    final_lines = []
    vertex_idx = 0
    for line in other_lines:
        if line.startswith('v ') and vertex_idx < len(rgb_floats):
            x, y, z = vertex_lines[vertex_idx][1], vertex_lines[vertex_idx][2], vertex_lines[vertex_idx][3]
            r, g, b = rgb_floats[vertex_idx]
            final_lines.append(f"v {x} {y} {z} {r:.6f} {g:.6f} {b:.6f}\n")
            vertex_idx += 1
        else:
            final_lines.append(line)

    try:
        with open(output_path, 'w') as f:
            f.writelines(final_lines)
        log_func(f"转换成功！文件已保存至：\n{output_path}")
        return True
    except Exception as e:
        log_func(f"写入文件失败：{e}")
        return False


# ---------- 图形界面 ----------
class MRGBConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ZBrush MRGB → KeyShot 顶点色转换器")
        self.root.geometry("600x400")
        self.root.resizable(True, True)

        # 输入文件路径变量
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()

        # ----- 界面布局 -----
        # 输入文件选择
        frame_in = tk.Frame(self.root)
        frame_in.pack(pady=10, padx=20, fill=tk.X)
        tk.Label(frame_in, text="输入 OBJ 文件：").pack(side=tk.LEFT)
        tk.Entry(frame_in, textvariable=self.input_path, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_in, text="浏览...", command=self.select_input).pack(side=tk.LEFT)

        # 输出文件选择
        frame_out = tk.Frame(self.root)
        frame_out.pack(pady=10, padx=20, fill=tk.X)
        tk.Label(frame_out, text="输出 OBJ 文件：").pack(side=tk.LEFT)
        tk.Entry(frame_out, textvariable=self.output_path, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_out, text="浏览...", command=self.select_output).pack(side=tk.LEFT)
        tk.Label(self.root, text="不指定输出路径时，自动在输入同目录生成“_keyshot.obj”", fg="gray").pack(anchor='w', padx=25)

        # 转换按钮
        self.btn_convert = tk.Button(self.root, text="开始转换", command=self.start_conversion,
                                     bg="#4CAF50", fg="white", font=("微软雅黑", 12, "bold"), height=1, width=15)
        self.btn_convert.pack(pady=15)

        # 日志显示区域
        self.log_area = scrolledtext.ScrolledText(self.root, height=10, state='normal', wrap=tk.WORD)
        self.log_area.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    def select_input(self):
        path = filedialog.askopenfilename(filetypes=[("OBJ files", "*.obj"), ("All files", "*.*")])
        if path:
            self.input_path.set(path)
            # 自动生成默认输出路径
            if not self.output_path.get():
                dir_name = os.path.dirname(path)
                base_name = os.path.splitext(os.path.basename(path))[0]
                default_out = os.path.join(dir_name, f"{base_name}_keyshot.obj")
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

    def start_conversion(self):
        input_file = self.input_path.get()
        output_file = self.output_path.get()

        if not input_file:
            messagebox.showwarning("提示", "请先选择输入文件。")
            return
        if not os.path.exists(input_file):
            messagebox.showerror("错误", "输入文件不存在。")
            return

        # 如果未指定输出路径，自动生成
        if not output_file:
            dir_name = os.path.dirname(input_file)
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(dir_name, f"{base_name}_keyshot.obj")
            self.output_path.set(output_file)

        # 禁用按钮，防止重复点击
        self.btn_convert.config(state='disabled', text="转换中...")
        self.log_area.delete(1.0, tk.END)
        self.log("开始转换...")

        # 在单独线程中执行，避免界面卡死
        def task():
            success = convert_mrgb_to_vertex_color(input_file, output_file, log_func=self.log)
            # 回到主线程更新界面
            self.root.after(0, self.on_conversion_finished, success)

        threading.Thread(target=task, daemon=True).start()

    def on_conversion_finished(self, success):
        self.btn_convert.config(state='normal', text="开始转换")
        if success:
            messagebox.showinfo("完成", "转换成功！\n文件已保存至：\n" + self.output_path.get())
        else:
            messagebox.showerror("失败", "转换失败，请查看日志信息。")

if __name__ == "__main__":
    root = tk.Tk()
    app = MRGBConverterApp(root)
    root.mainloop()