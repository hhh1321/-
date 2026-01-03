import re
import os
from collections import Counter, defaultdict

def parse_segmented_file(file_path):
    """解析分词文件"""
    poems_data = []
    current_poem_words = []
    current_poem_num = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        
        # 跳过空行
        if not line:
            continue
            
        # 检查是否是新的诗词开始
        if line.startswith('第') and '首诗词分词结果:' in line:
            # 如果已经有收集的词语，保存前一首诗
            if current_poem_words:
                poems_data.append((current_poem_num, current_poem_words.copy()))
                current_poem_words = []
            
            # 提取诗词编号
            match = re.search(r'第(\d+)首', line)
            if match:
                current_poem_num = int(match.group(1))
            else:
                current_poem_num = len(poems_data) + 1
                
        # 检查是否是分隔线
        elif line.startswith('---'):
            # 分隔线表示一首诗结束
            if current_poem_words:
                poems_data.append((current_poem_num, current_poem_words.copy()))
                current_poem_words = []
        # 否则可能是分词行
        elif current_poem_words is not None:
            # 分割词语
            words = line.split()
            current_poem_words.extend(words)
    
    # 添加最后一首诗（如果有）
    if current_poem_words:
        poems_data.append((current_poem_num, current_poem_words.copy()))
    
    return poems_data

def identify_and_categorize_images(all_words_counter):
    """识别和分类意象词语"""
    # 定义各个类别的关键词集合
    categories = {
        '食物': {
            'keywords': {
                '茶', '酒', '肉', '饭', '粥', '汤', '菜', '果', '饼', '糕',
                '糖', '蜜', '盐', '油', '酱', '醋', '姜', '蒜', '葱', '椒',
                '米', '面', '豆', '麦', '粟', '黍', '稷', '稻', '粱', '菽',
                '葡萄', '龙井', '碧螺', '乌龙', '普洱', '毛峰', '铁观音',
                '白酒', '黄酒', '米酒', '花酒', '醇酒', '佳酿',
                '猪肉', '牛肉', '羊肉', '鸡肉', '鸭肉', '鱼肉', '虾肉', '蟹肉',
                '腊肉', '火腿', '香肠', '熏肉',
                '米饭', '面条', '馒头', '包子', '饺子', '汤圆', '粽子', '月饼',
                '糕点', '糖果', '蜜饯', '果脯',
                '豆腐', '豆浆', '豆干', '豆皮', '腐竹',
                '蔬菜', '瓜果', '水果', '干果', '坚果'
            },
            'words': Counter()
        },
        '自然景物': {
            'keywords': {
                '山', '水', '云', '风', '雨', '雪', '月', '日', '星', '天',
                '江', '河', '湖', '海', '溪', '泉', '池', '塘', '波', '浪',
                '石', '岩', '峰', '岭', '丘', '壑', '谷', '洞', '崖', '壁',
                '林', '树', '木', '花', '草', '叶', '枝', '根', '松', '柏',
                '梅', '兰', '竹', '菊', '柳', '桃', '李', '杏', '樱', '桂',
                '荷', '莲', '菊', '枫', '梧', '桐', '杨', '槐', '桑', '榆',
                '明月', '清风', '白云', '青山', '绿水', '碧波', '蓝天', '红日',
                '星辰', '云雾', '烟雨', '雪花', '霜露', '雷电', '彩虹', '瀑布',
                '溪流', '江河', '湖海', '池塘', '山峰', '峡谷', '森林', '草原',
                '沙漠', '田园', '花园', '竹林', '松林', '梅林', '桃园', '杏林',
                '荷塘', '菊花', '牡丹', '玫瑰', '芙蓉', '杜鹃', '海棠', '兰花',
                '松柏', '杨柳', '梧桐', '枫叶', '桂树', '桑田', '麦田', '稻田',
                '春风', '夏雨', '秋霜', '冬雪', '朝霞', '晚霞', '夕阳', '朝阳',
                '明月', '繁星', '北斗', '银河', '白云', '乌云', '彩云', '雾霭',
                '露珠', '冰霜', '冰雹', '雷电', '彩虹', '霓虹'
            },
            'words': Counter()
        },
        '贵物': {
            'keywords': {
                '金', '玉', '宝', '贵', '珠', '翠', '翡', '玛', '瑙', '珊',
                '瑚', '珍', '华', '美', '丽', '鼎', '画', '瓷', '陶', '青铜',
                '银', '铜', '铁', '锡', '铅', '汞', '铂', '钻石', '宝石',
                '黄金', '白银', '玉石', '珠宝', '珍珠', '翡翠', '玛瑙', '珊瑚',
                '琥珀', '琉璃', '钻石', '宝石', '金器', '银器', '玉器', '瓷器',
                '陶器', '青铜器', '铁器', '铜器',
                '金簪', '玉镯', '玉佩', '金钗', '银环', '宝珠', '珍珠', '翡翠',
                '珊瑚', '玛瑙', '金杯', '银碗', '玉壶', '宝鼎', '金炉', '银瓶',
                '玉盘', '宝盒', '金锁', '银钥', '金冠', '玉带', '宝座', '金鞍',
                '玉马', '宝刀', '金剑', '玉弓', '宝箭', '金甲', '玉盔'
            },
            'words': Counter()
        },
        '时间意象': {
            'keywords': {
                # 按一天的时间顺序排列
                '晨', '朝', '旦', '晓', '黎明', '拂晓', '清晨', '早晨', '早朝',
                '午', '日中', '正午', '午时', '下午',
                '夕', '暮', '晚', '黄昏', '傍晚', '日暮', '夕阳', '夕照',
                '夜', '晚', '黑夜', '深夜', '子夜', '午夜', '三更', '五更',
                '月', '明月', '皎月', '弯月', '圆月', '残月', '新月', '满月',
                '星', '星辰', '繁星', '北斗', '银河',
                '灯', '烛', '灯笼', '烛光', '灯火', '灯花', '灯烛',
                '春', '夏', '秋', '冬', '四季', '时节', '时光', '岁月',
                '年', '岁', '载', '代', '世纪', '时代',
                '元宵', '清明', '端午', '七夕', '中秋', '重阳', '除夕', '元旦'
            },
            'words': Counter()
        }
    }
    
    # 所有意象词语的统计
    all_images = Counter()
    
    # 遍历所有词语
    for word, count in all_words_counter.items():
        # 检查词语是否包含任何类别的关键词
        for category_name, category_data in categories.items():
            keywords = category_data['keywords']
            
            # 检查词语本身是否是关键词
            if word in keywords:
                categories[category_name]['words'][word] += count
                all_images[word] += count
                continue
            
            # 检查词语是否包含关键词
            for keyword in keywords:
                if len(keyword) == 1:  # 单字关键词
                    if keyword in word:
                        categories[category_name]['words'][word] += count
                        all_images[word] += count
                        break
                else:  # 多字关键词
                    if keyword in word:
                        categories[category_name]['words'][word] += count
                        all_images[word] += count
                        break
    
    return all_images, categories

def analyze_images(poems_data):
    """分析所有诗词中的意象"""
    all_words_counter = Counter()
    total_poems = len(poems_data)
    
    print(f"开始分析意象，共有{total_poems}首诗词...")
    
    for idx, (poem_num, poem_words) in enumerate(poems_data, 1):
        # 每100首诗显示一次进度
        if idx % 100 == 0 or idx == total_poems:
            print(f"当前已分析了{idx}/{total_poems}首诗词")
        
        # 统计所有词语
        for word in poem_words:
            all_words_counter[word] += 1
    
    # 识别和分类意象词语
    all_images, categories = identify_and_categorize_images(all_words_counter)
    
    return all_words_counter, all_images, categories

def save_results(output_path, all_words_counter, all_images, categories):
    """保存分析结果"""
    with open(output_path, 'w', encoding='utf-8') as f:
        # 写入总体统计
        f.write("=" * 80 + "\n")
        f.write("意象统计总体信息\n")
        f.write("=" * 80 + "\n\n")
        
        total_words = sum(all_words_counter.values())
        total_images = sum(all_images.values())
        
        f.write(f"总词语数: {total_words:,}\n")
        f.write(f"意象词语数: {total_images:,} ({total_images/total_words*100:.2f}%)\n")
        f.write(f"不同意象词语数: {len(all_images):,}\n\n")
        
        # 写入所有意象词语频率排行
        f.write("=" * 80 + "\n")
        f.write("所有意象词语频率排行（TOP 500）\n")
        f.write("=" * 80 + "\n")
        f.write("{:<5} {:<20} {:<10}\n".format("排名", "意象词语", "出现次数"))
        f.write("-" * 40 + "\n")
        
        for i, (word, count) in enumerate(all_images.most_common(500), 1):
            f.write("{:<5} {:<20} {:<10}\n".format(i, word, count))
        f.write("\n")
        
        # 写入各个类别的意象词语统计
        for category_name, category_data in categories.items():
            f.write("=" * 80 + "\n")
            f.write(f"{category_name}意象词语统计（TOP 300）\n")
            f.write("=" * 80 + "\n")
            
            words_counter = category_data['words']
            if words_counter:
                f.write(f"总词数: {sum(words_counter.values()):,}\n")
                f.write(f"不同词语数: {len(words_counter):,}\n\n")
                
                f.write("{:<5} {:<20} {:<10}\n".format("排名", "意象词语", "出现次数"))
                f.write("-" * 40 + "\n")
                
                for i, (word, count) in enumerate(words_counter.most_common(300), 1):
                    f.write("{:<5} {:<20} {:<10}\n".format(i, word, count))
            else:
                f.write("未发现该类别意象词语\n")
            
            f.write("\n")
        
        # 写入时间意象的详细分类（按一天的时间顺序）
        f.write("=" * 80 + "\n")
        f.write("时间意象详细分类（按一天时间顺序）\n")
        f.write("=" * 80 + "\n")
        
        time_categories = {
            '清晨时段': ['晨', '朝', '旦', '晓', '黎明', '拂晓', '清晨', '早晨', '早朝'],
            '上午时段': ['午前', '上午'],
            '中午时段': ['午', '日中', '正午', '午时'],
            '下午时段': ['午后', '下午'],
            '傍晚时段': ['夕', '暮', '晚', '黄昏', '傍晚', '日暮', '夕阳', '夕照'],
            '夜晚时段': ['夜', '晚', '黑夜', '深夜', '子夜', '午夜', '三更', '五更'],
            '月亮相关': ['月', '明月', '皎月', '弯月', '圆月', '残月', '新月', '满月'],
            '星辰相关': ['星', '星辰', '繁星', '北斗', '银河'],
            '灯火相关': ['灯', '烛', '灯笼', '烛光', '灯火', '灯花', '灯烛'],
            '季节相关': ['春', '夏', '秋', '冬', '四季'],
            '节日相关': ['元宵', '清明', '端午', '七夕', '中秋', '重阳', '除夕', '元旦']
        }
        
        time_words_counter = categories['时间意象']['words']
        
        for time_category, keywords in time_categories.items():
            f.write(f"\n{time_category}:\n")
            category_words = Counter()
            
            for word, count in time_words_counter.items():
                for keyword in keywords:
                    if keyword in word:
                        category_words[word] += count
                        break
            
            if category_words:
                for i, (word, count) in enumerate(category_words.most_common(50), 1):
                    f.write(f"  {i:2d}. {word:15s}: {count:6d}次\n")
            else:
                f.write("  未发现相关意象词语\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("分析完成\n")
        f.write("=" * 80 + "\n")

def main():
    """主函数"""
    # 询问文件路径
    input_file = input("请输入分词文件路径（例如：C:\\Users\\26010\\Desktop\\乾隆分词.txt）: ")
    
    # 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：文件 '{input_file}' 不存在！")
        return
    
    # 询问输出文件路径
    output_file = input("请输入结果文件路径（例如：C:\\Users\\26010\\Desktop\\意象统计结果.txt）: ")
    
    # 解析分词文件
    print("解析分词文件...")
    poems_data = parse_segmented_file(input_file)
    
    print(f"成功解析了{len(poems_data)}首诗词")
    
    # 分析意象
    all_words_counter, all_images, categories = analyze_images(poems_data)
    
    # 保存结果
    print(f"保存分析结果到: {output_file}")
    save_results(output_file, all_words_counter, all_images, categories)
    
    print("意象统计完成！")
    print(f"共分析{len(poems_data)}首诗词，{sum(all_words_counter.values()):,}个词语")
    print(f"发现{len(all_images):,}个不同的意象词语")
    
    # 打印各类别的统计摘要
    print("\n各类别意象统计摘要:")
    for category_name, category_data in categories.items():
        words_counter = category_data['words']
        if words_counter:
            print(f"  {category_name}: {sum(words_counter.values()):,}次出现，{len(words_counter):,}个不同词语")

if __name__ == "__main__":
    main()