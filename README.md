# ZBrush MRGB → 顶点色转换器

一个用于将 ZBrush 导出的 OBJ 文件中 MRGB 格式的顶点色数据转换为通用 RGB 浮点顶点色的 GUI 工具，适用于 KeyShot、Maya、Blender 等 DCC 软件。

## 功能

- 读取 ZBrush 导出的带 `#MRGB` 顶点色数据的 OBJ 文件
- 将 MRGB 十六进制颜色转换为标准 RGB 浮点格式（0.0 ~ 1.0）
- 自动去除 `mtllib` 和 `usemtl` 引用（v5）
- 使用 `mmap` 流式处理，支持大文件高效转换（v5）
- 简洁的 tkinter 图形界面，支持拖放式文件选择
- 进度条显示转换进度（v5）

## 版本说明

| 文件 | 说明 |
|------|------|
| `MRGB_Converter.py` | 初版 GUI 版本 |
| `convert_mrgb_v2.py` | 迭代版本 |
| `convert_mrgb_v3.py` | 迭代版本 |
| `convert_mrgb_v4.py` | 迭代版本 |
| **`convert_mrgb_v5.py`** | **最新版** — 使用 mmap 流式处理，支持进度条，性能最佳 |
| `MRGB_Converter.spec` | PyInstaller 打包配置文件（基于 v5） |

## 使用方法

### 方式一：直接运行 Python 脚本

1. 确保已安装 Python 3.x（无需额外依赖，仅使用标准库 tkinter）

2. 运行最新版本：
```bash
python convert_mrgb_v5.py
```

3. 在界面中选择输入的 ZBrush OBJ 文件，点击"开始转换"

### 方式二：使用打包好的 EXE

直接运行 `dist/MRGB_Converter.exe`（如果已构建）

### 自行打包 EXE

```bash
pip install pyinstaller
cd MRGB_Converter
pyinstaller MRGB_Converter.spec
```

可执行文件将输出到 `dist/` 目录。

## 转换原理

ZBrush 导出的 OBJ 文件中，顶点色以 `#MRGB` 开头的区块存储，格式为十六进制编码（如 `FF7F3F80`）。本工具：

1. 解析 `#MRGB` 数据块，提取十六进制颜色值
2. 将每个颜色的 R、G、B 通道转换为 0.0 ~ 1.0 的浮点数
3. 将颜色值追加到对应的 `v x y z` 顶点行，变为 `v x y z r g b` 格式
4. 去除原有的 MTL 材质引用

这使得 OBJ 文件可以被 KeyShot、Maya、Blender 等软件正确识别顶点色。

## 许可证

MIT License

## 作者

Aniraiden

---

# ZBrush MRGB → Vertex Color Converter

A GUI tool for converting MRGB-format vertex color data from ZBrush-exported OBJ files into standard RGB floating-point vertex colors, compatible with KeyShot, Maya, Blender, and other DCC applications.

## Features

- Reads ZBrush-exported OBJ files with `#MRGB` vertex color data
- Converts MRGB hex colors to standard RGB float format (0.0 ~ 1.0)
- Automatically strips `mtllib` and `usemtl` references (v5)
- Uses `mmap` streaming for efficient large-file conversion (v5)
- Clean tkinter GUI with file browser support
- Progress bar for conversion progress (v5)

## Version Overview

| File | Description |
|------|-------------|
| `MRGB_Converter.py` | Initial GUI version |
| `convert_mrgb_v2.py` | Iterative version |
| `convert_mrgb_v3.py` | Iterative version |
| `convert_mrgb_v4.py` | Iterative version |
| **`convert_mrgb_v5.py`** | **Latest** — mmap streaming, progress bar, best performance |
| `MRGB_Converter.spec` | PyInstaller build config (based on v5) |

## Usage

### Option 1: Run Python Script Directly

1. Ensure Python 3.x is installed (no extra dependencies, standard library tkinter only)

2. Run the latest version:
```bash
python convert_mrgb_v5.py
```

3. Select the input ZBrush OBJ file in the GUI and click "Start Conversion"

### Option 2: Use Pre-built EXE

Run `dist/MRGB_Converter.exe` directly (if already built)

### Build EXE Yourself

```bash
pip install pyinstaller
cd MRGB_Converter
pyinstaller MRGB_Converter.spec
```

The executable will be output to the `dist/` directory.

## How It Works

In ZBrush-exported OBJ files, vertex colors are stored in blocks starting with `#MRGB`, encoded as hexadecimal values (e.g., `FF7F3F80`). This tool:

1. Parses the `#MRGB` data block and extracts hexadecimal color values
2. Converts each color's R, G, B channels to 0.0 ~ 1.0 floating-point numbers
3. Appends color values to the corresponding `v x y z` vertex lines, producing `v x y z r g b` format
4. Removes original MTL material references

This allows OBJ files to be correctly recognized for vertex colors by KeyShot, Maya, Blender, and other software.

## License

MIT License

## Author

Aniraiden
