import os
import re
from fuzzywuzzy import fuzz, process
import difflib


def read_qianlong_poems(file_path):
    """读取乾隆诗词.txt文件并解析内容"""
    print(f"正在读取文件: {file_path}")
    poems = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 按分隔符分割诗词
    poem_blocks = content.split('--------------------------------------------------')

    for i, block in enumerate(poem_blocks):
        if not block.strip():
            continue

        lines = block.strip().split('\n')
        if not lines:
            continue

        # 提取标题（第一行）
        title_line = lines[0].strip()

        # 使用正则表达式提取标题（去除序号）
        title_match = re.search(r'\d+\.《(.+)》', title_line)
        if title_match:
            title = title_match.group(1)
        else:
            # 如果没有标准格式，使用整行作为标题（去除序号）
            title = re.sub(r'^\d+\.', '', title_line).strip('《》').strip()

        # 提取内容（去除标题行）
        content_lines = lines[1:] if len(lines) > 1 else []
        content = '\n'.join(line.strip() for line in content_lines if line.strip())

        poems.append({
            'original_title': title_line,
            'clean_title': title,
            'content': content,
            'original_block': block.strip()
        })

        if (i + 1) % 50 == 0:
            print(f"已解析 {i + 1} 首诗词...")

    print(f"成功解析 {len(poems)} 首诗词")
    return poems


def read_qianlong2_order(file_path):
    """读取乾隆诗词2.txt并提取标题顺序"""
    print(f"正在读取排序文件: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 尝试提取可能的标题行
    lines = content.split('\n')
    titles = []

    # 匹配可能的标题模式
    title_patterns = [
        r'《(.+)》',  # 《标题》
        r'（(.+)）',  # （标题）
        r'【(.+)】',  # 【标题】
        r'「(.+)」',  # 「标题」
        r'(.+)',  # 普通文本行
    ]

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 跳过明显的非标题行
        if any(marker in line for marker in
               ['================================', '钦定', '提要', '目录', '奏折', '御制']):
            continue

        # 尝试匹配各种标题格式
        title = None
        for pattern in title_patterns:
            match = re.search(pattern, line)
            if match:
                candidate = match.group(1) if match.groups() else line
                # 过滤掉过长的行（可能是正文）
                if len(candidate) <= 50:  # 假设标题不会超过50个字符
                    title = candidate
                    break

        if title and title not in titles:
            titles.append(title)

    print(f"从排序文件中提取到 {len(titles)} 个可能的标题")
    return titles


def normalize_title(title):
    """标准化标题，用于模糊匹配"""
    # 移除标点符号和空格
    title = re.sub(r'[《》【】（）()「」〈〉“”‘’\s]', '', title)
    # 转换为小写
    title = title.lower()
    return title


def find_best_match(target_title, poems, threshold=60):
    """使用模糊匹配找到最佳匹配的诗词"""
    normalized_target = normalize_title(target_title)

    best_match = None
    best_score = 0

    for poem in poems:
        normalized_poem = normalize_title(poem['clean_title'])

        # 使用多种匹配策略
        score1 = fuzz.ratio(normalized_target, normalized_poem)
        score2 = fuzz.partial_ratio(normalized_target, normalized_poem)
        score3 = fuzz.token_sort_ratio(normalized_target, normalized_poem)

        # 取最高分
        score = max(score1, score2, score3)

        if score > best_score and score >= threshold:
            best_score = score
            best_match = poem

    return best_match, best_score


def sort_poems_by_order(poems, order_titles):
    """按照指定的标题顺序对诗词进行排序"""
    print("开始进行模糊匹配排序...")

    sorted_poems = []
    matched_indices = set()
    unmatched_poems = poems.copy()

    # 第一阶段：精确匹配和高质量模糊匹配
    high_quality_matches = []

    for i, title in enumerate(order_titles):
        if (i + 1) % 20 == 0:
            print(f"处理排序文件中第 {i + 1} 个标题...")

        best_match, score = find_best_match(title, unmatched_poems, threshold=75)

        if best_match:
            high_quality_matches.append((title, best_match, score))
            unmatched_poems.remove(best_match)

    print(f"第一阶段匹配完成，找到 {len(high_quality_matches)} 个高质量匹配")

    # 第二阶段：较低质量的模糊匹配
    medium_quality_matches = []

    for i, title in enumerate(order_titles):
        # 跳过已经匹配的标题
        if any(t[0] == title for t in high_quality_matches):
            continue

        best_match, score = find_best_match(title, unmatched_poems, threshold=50)

        if best_match:
            medium_quality_matches.append((title, best_match, score))
            unmatched_poems.remove(best_match)

    print(f"第二阶段匹配完成，找到 {len(medium_quality_matches)} 个中等质量匹配")

    # 按照原始顺序组合匹配结果
    all_matches = []
    for title in order_titles:
        # 查找高质量匹配
        hq_match = next((m for t, m, s in high_quality_matches if t == title), None)
        if hq_match:
            all_matches.append(hq_match)
            continue

        # 查找中等质量匹配
        mq_match = next((m for t, m, s in medium_quality_matches if t == title), None)
        if mq_match:
            all_matches.append(mq_match)

    print(f"总共匹配到 {len(all_matches)} 首诗词")
    print(f"剩余 {len(unmatched_poems)} 首诗词无法匹配")

    # 将匹配的诗词按顺序排列，未匹配的放在最后
    final_poems = all_matches + unmatched_poems

    return final_poems


def save_sorted_poems(poems, output_path):
    """保存排序后的诗词"""
    print(f"正在保存排序结果到: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        for i, poem in enumerate(poems, 1):
            if isinstance(poem, dict):
                # 匹配的诗词
                f.write(f"{i}.{poem['original_title']}\n")
                f.write(poem['content'])
            else:
                # 未匹配的诗词（直接写入原始块）
                f.write(f"{i}.{poem['original_title']}\n")
                f.write(poem['content'])

            f.write("\n--------------------------------------------------\n\n")

    print("保存完成！")


def main():
    # 文件路径
    poems_path = r"C:\Users\任宇轩\Desktop\信息系统设计与分析\乾隆诗词.txt"
    order_path = r"C:\Users\任宇轩\Desktop\信息系统设计与分析\乾隆诗词2.txt"
    output_path = r"C:\Users\任宇轩\Desktop\信息系统设计与分析\乾隆诗词_排序后（模糊版）.txt"

    try:
        # 步骤1：读取原始诗词
        print("=" * 50)
        print("步骤1: 读取原始诗词文件")
        poems = read_qianlong_poems(poems_path)

        # 步骤2：读取排序顺序
        print("\n" + "=" * 50)
        print("步骤2: 读取排序文件")
        order_titles = read_qianlong2_order(order_path)

        # 显示前几个提取的标题作为示例
        print("\n排序文件中的前10个标题示例:")
        for i, title in enumerate(order_titles[:10]):
            print(f"  {i + 1}. {title}")

        # 步骤3：进行模糊匹配排序
        print("\n" + "=" * 50)
        print("步骤3: 进行模糊匹配排序")
        sorted_poems = sort_poems_by_order(poems, order_titles)

        # 步骤4：保存结果
        print("\n" + "=" * 50)
        print("步骤4: 保存排序结果")
        save_sorted_poems(sorted_poems, output_path)

        # 统计信息
        print("\n" + "=" * 50)
        print("排序完成！统计信息:")
        print(f"原始诗词数量: {len(poems)}")
        print(f"排序文件标题数量: {len(order_titles)}")
        print(f"成功匹配数量: {len([p for p in sorted_poems if isinstance(p, dict) and 'clean_title' in p])}")
        print(
            f"未匹配数量: {len([p for p in sorted_poems if isinstance(p, dict)]) - len([p for p in sorted_poems if isinstance(p, dict) and 'clean_title' in p])}")

    except FileNotFoundError as e:
        print(f"错误: 找不到文件 - {e}")
    except Exception as e:
        print(f"程序执行过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 检查是否需要安装依赖
    try:
        from fuzzywuzzy import fuzz
    except ImportError:
        print("需要安装 fuzzywuzzy 库，请运行: pip install fuzzywuzzy python-Levenshtein")
        exit(1)

    main()