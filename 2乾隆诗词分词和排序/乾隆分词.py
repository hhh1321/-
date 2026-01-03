import jieba
import jieba.posseg as pseg
from collections import Counter
import re


def process_qianlong_poems():
    # 文件路径
    input_file = r"C:\Users\任宇轩\Desktop\用户数据\乾隆诗词1.txt"
    output_seg_file = r"C:\Users\任宇轩\Desktop\用户数据\乾隆分词.txt"
    output_sort_file = r"C:\Users\任宇轩\Desktop\用户数据\乾隆排序.txt"

    # 加载自定义词典（针对古诗词优化）
    def load_poem_dict():
        # 古诗词常见意象词汇
        poem_words = [
            '青山', '绿水', '明月', '清风', '白云', '碧波', '烟霞', '云雾', '松柏', '梅花',
            '竹子', '菊花', '荷花', '杨柳', '梧桐', '兰花', '牡丹', '桃花', '杏花', '梨花',
            '春风', '秋雨', '冬雪', '夏日', '霜露', '雷电', '虹霓', '星辰', '日月', '天地',
            '江河', '湖海', '山川', '峰峦', '溪涧', '泉水', '瀑布', '波涛', '舟船', '桥梁',
            '亭台', '楼阁', '宫殿', '寺庙', '园林', '庭院', '书房', '琴瑟', '棋局', '书画',
            '酒杯', '茶具', '香炉', '宝剑', '弓箭', '马匹', '牛羊', '鸡犬', '鸟雀', '鱼龙',
            '蝴蝶', '蜜蜂', '蝉鸣', '雁阵', '孤帆', '远影', '落日', '朝阳', '黄昏', '夜晚',
            '思念', '忧愁', '欢乐', '寂寞', '孤独', '逍遥', '自在', '清闲', '忙碌', '辛勤',
            '功名', '富贵', '贫贱', '荣辱', '得失', '成败', '兴衰', '古今', '往来', '始终'
        ]

        # 将这些词添加到分词词典中
        for word in poem_words:
            jieba.add_word(word, freq=1000, tag='n')

    # 加载古诗词词典
    load_poem_dict()

    # 读取文件
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"文件 {input_file} 未找到")
        return
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return

    # 提取诗词内容（去除标题和分隔线）
    poems = []
    lines = content.split('\n')
    current_poem = []

    for line in lines:
        line = line.strip()
        if line.startswith('《') or line.startswith('1.') or line.startswith('2.') or line.isdigit():
            # 标题行，跳过
            continue
        elif line.startswith('--------------------------------------------------'):
            # 分隔线，如果当前有诗词内容则保存
            if current_poem:
                poems.append(''.join(current_poem))
                current_poem = []
        elif line and not line.startswith('乾隆诗词全集') and not line.startswith('='):
            # 诗词内容行
            current_poem.append(line)

    # 处理最后一首诗词
    if current_poem:
        poems.append(''.join(current_poem))

    print(f"共提取到 {len(poems)} 首诗词")

    # 分词处理
    all_words = []
    segmented_poems = []

    for i, poem in enumerate(poems):
        if not poem.strip():
            continue

        # 使用jieba进行分词和词性标注
        words = pseg.cut(poem)

        # 筛选有意义的词汇（名词、动词、形容词等）
        filtered_words = []
        for word, flag in words:
            # 保留有意义的词性：名词、动词、形容词、成语等
            if flag.startswith(('n', 'v', 'a', 'j', 'l')) and len(word) >= 2:
                filtered_words.append(word)
            # 也保留一些常见的单字意象词
            elif len(word) == 1 and word in '风花雪月山水天地人':
                filtered_words.append(word)

        segmented_poems.append(filtered_words)
        all_words.extend(filtered_words)

    # 保存分词结果
    try:
        with open(output_seg_file, 'w', encoding='utf-8') as f:
            for i, words in enumerate(segmented_poems):
                f.write(f"第{i + 1}首诗词分词结果:\n")
                f.write(' '.join(words) + '\n')
                f.write('-' * 50 + '\n')
        print(f"分词结果已保存到: {output_seg_file}")
    except Exception as e:
        print(f"保存分词结果时出错: {e}")
        return

    # 统计词频
    word_counts = Counter(all_words)

    # 保存排序结果
    try:
        with open(output_sort_file, 'w', encoding='utf-8') as f:
            f.write("乾隆诗词意象词汇频率统计（从高到低）\n")
            f.write("=" * 60 + "\n")
            f.write(f"总词汇数: {len(all_words)}\n")
            f.write(f"不重复词汇数: {len(word_counts)}\n")
            f.write("=" * 60 + "\n\n")

            for i, (word, count) in enumerate(word_counts.most_common()):
                f.write(f"{i + 1:4d}. {word:8s} : {count:4d} 次\n")

        print(f"词频统计结果已保存到: {output_sort_file}")

        # 显示前20个高频词
        print("\n前20个高频意象词汇:")
        for word, count in word_counts.most_common(20):
            print(f"  {word}: {count}次")

    except Exception as e:
        print(f"保存词频统计时出错: {e}")
        return


if __name__ == "__main__":
    # 安装依赖的提示
    try:
        import jieba
        import jieba.posseg as pseg
    except ImportError:
        print("请先安装jieba分词库:")
        print("pip install jieba")
        exit(1)

    process_qianlong_poems()