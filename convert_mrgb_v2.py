import re
import argparse

def split_hex_line(line):
    """按每8个字符切割连续十六进制颜色值"""
    # 移除所有空白字符（空格、换行等），只保留十六进制字符
    hex_str = re.sub(r'\s+', '', line.strip())
    # 如果长度不是8的倍数，则可能格式错误，但仍尝试切割，最后不完整的部分丢弃
    values = []
    for i in range(0, len(hex_str), 8):
        chunk = hex_str[i:i+8]
        if len(chunk) == 8:
            values.append(chunk)
        else:
            print(f"警告：残余字符 '{chunk}' 长度不足8，已忽略")
    return values

def convert_mrgb_to_vertex_color(input_path, output_path):
    with open(input_path, 'r') as f:
        lines = f.readlines()

    vertex_lines = []     # (索引, x, y, z)
    other_lines = []
    mrgb_values = []      # 所有解析出的8位十六进制颜色值
    inside_mrgb = False
    mrgb_header = "#MRGB"

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(mrgb_header):
            inside_mrgb = True
            # 有可能 "#MRGB" 后直接跟数据，比如 "#MRGB ff584839..."
            data_part = stripped[len(mrgb_header):].strip()
            if data_part:
                mrgb_values.extend(split_hex_line(data_part))
            continue

        if inside_mrgb:
            # 如果在MRGB块内且该行不是空行或注释（除MRGB外的其他#），则视为数据
            if stripped == '' or stripped.startswith('#'):
                # 遇到空行或新注释（非MRGB），结束MRGB块
                inside_mrgb = False
                # 当前行仍需按普通行处理，不能跳过
                # 用类似逻辑，但需要重新判断此行
                # 简便做法：将当前行重新加入判断，用 continue 会跳过，所以用标志
                pass
            else:
                # 数据行，按每8字符切割并添加
                mrgb_values.extend(split_hex_line(stripped))
                continue

        # 普通内容处理
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

    # 检查颜色与顶点数量
    if not mrgb_values:
        print("错误：未找到有效的MRGB颜色数据。")
        return
    if len(mrgb_values) != len(vertex_lines):
        print(f"警告：顶点数 ({len(vertex_lines)}) 与颜色数 ({len(mrgb_values)}) 不一致，转换可能错位。")

    # 将十六进制MMRRGGBB转换为RGB浮点 (0~1)
    rgb_floats = []
    for hex_str in mrgb_values:
        if len(hex_str) != 8:
            print(f"警告：颜色值 '{hex_str}' 长度不是8，跳过。")
            continue
        # 提取RRGGBB (索引2-7)
        try:
            rr = int(hex_str[2:4], 16)
            gg = int(hex_str[4:6], 16)
            bb = int(hex_str[6:8], 16)
        except ValueError:
            print(f"警告：无法解析颜色 '{hex_str}'，跳过。")
            continue
        r = rr / 255.0
        g = gg / 255.0
        b = bb / 255.0
        rgb_floats.append((r, g, b))

    # 生成最终行
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

    if vertex_idx < len(rgb_floats):
        print(f"警告：额外颜色数据 ({len(rgb_floats)-vertex_idx} 个) 已忽略。")

    with open(output_path, 'w') as f:
        f.writelines(final_lines)
    print(f"转换完成！已保存为：{output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将ZBrush MRGB顶点色转换为KeyShot可读标准OBJ（支持无空格连续格式）")
    parser.add_argument("input", help="输入的OBJ文件路径")
    parser.add_argument("-o", "--output", help="输出的OBJ文件路径，默认为原文件名_keyshot.obj")
    args = parser.parse_args()

    if not args.output:
        args.output = args.input.replace(".obj", "_keyshot.obj") or "output_keyshot.obj"

    convert_mrgb_to_vertex_color(args.input, args.output)