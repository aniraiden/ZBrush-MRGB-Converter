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
