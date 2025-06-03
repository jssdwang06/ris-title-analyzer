import re
from collections import Counter
import matplotlib.pyplot as plt

def parse_ris_file(file_path):
    """解析RIS文件并提取标题"""
    titles = []
    current_title = ""
    in_title = False

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            print(f"成功打开文件: {file_path}")
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
                print(f"文件末尾标题: {clean_title}")

            if len(titles) == 0:
                print("警告: 未找到任何以'TI  - '开头的标题行")
                print("文件前20行内容预览:")
                with open(file_path, 'r', encoding='utf-8') as preview:
                    for i, line in enumerate(preview):
                        if i < 20:
                            print(f"{i+1}: {line.strip()}")
                        else:
                            break
    except UnicodeDecodeError:
        print("UTF-8编码打开失败，尝试其他编码...")
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                print("使用latin-1编码重新解析...")
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
            print(f"打开文件时出错: {e}")
    except Exception as e:
        print(f"打开文件时出错: {e}")

    return titles

def normalize_word(word):
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

def analyze_word_frequency(titles, top_n=50):
    """分析标题中的词频"""
    print(f"开始分析 {len(titles)} 个标题的词频...")

    # 学术文章标题专用停用词列表
    # 保留学术价值高的词汇，移除常见的功能词和连接词
    stop_words = {
        # 基础功能词
        'a', 'an', 'the', 'and', 'or', 'but', 'if', 'of', 'at', 'by',
        'for', 'with', 'about', 'to', 'from', 'in', 'on', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
        'might', 'must', 'can', 'this', 'that', 'these', 'those',

        # 代词（在学术标题中很少出现，但保留以防万一）
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
        'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their',

        # 疑问词和副词（某些在学术标题中可能有意义，谨慎移除）
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

    # 使用简单的空格分词
    all_words = []
    total_titles = len(titles)

    # 显示进度，每处理500个标题显示一次进度
    for i, title in enumerate(titles):
        if (i + 1) % 500 == 0 or i == 0 or i == total_titles - 1:
            print(f"  处理进度: {i+1}/{total_titles} ({(i+1)/total_titles*100:.1f}%)")

        # 转小写，移除标点符号，保留字母、数字和空格
        clean_title = re.sub(r'[^\w\s]', ' ', title.lower())
        # 分词
        words = clean_title.split()
        # 过滤并规范化：只保留字母单词，长度大于2，不在停用词中，然后进行词形规范化
        filtered_words = []
        for word in words:
            if word.isalpha() and len(word) > 2 and word not in stop_words:
                normalized_word = normalize_word(word)
                # 再次检查规范化后的词是否在停用词中
                if normalized_word not in stop_words:
                    filtered_words.append(normalized_word)
        all_words.extend(filtered_words)

    print(f"✓ 总共提取到 {len(all_words)} 个词汇")

    # 计算词频
    word_counts = Counter(all_words)
    most_common = word_counts.most_common(top_n)

    print(f"✓ 找到 {len(word_counts)} 个不同的词汇")
    return most_common

def plot_word_frequency(word_counts):
    """绘制词频分布图"""
    if len(word_counts) == 0:
        print("没有足够的数据来生成词频图")
        return

    words, counts = zip(*word_counts)

    # 设置中文字体支持
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False

    plt.figure(figsize=(15, 8))
    bars = plt.bar(words, counts, color='skyblue', alpha=0.7)

    # 在柱状图上显示数值
    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                str(count), ha='center', va='bottom', fontsize=10)

    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.title('标题词频分布 (Title Word Frequency)', fontsize=16, fontweight='bold')
    plt.xlabel('词语 (Words)', fontsize=14)
    plt.ylabel('频次 (Frequency)', fontsize=14)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    # 保存图片
    plt.savefig('title_word_frequency.png', dpi=300, bbox_inches='tight')
    print("词频图已保存为 'title_word_frequency.png'")
    plt.show()

if __name__ == "__main__":
    file_path = input("请输入RIS文件路径: ")

    print("=" * 60)
    print("RIS文件标题解析和词频分析工具")
    print("=" * 60)

    titles = parse_ris_file(file_path)
    print(f"\n✓ 成功解析出 {len(titles)} 个标题")

    if len(titles) == 0:
        print("❌ 未找到标题，请检查文件路径和格式是否正确")
    else:
        # 显示前几个标题作为示例
        print("\n📋 标题示例:")
        for i, title in enumerate(titles[:5]):
            print(f"  {i+1}. {title}")
        if len(titles) > 5:
            print(f"  ... 还有 {len(titles) - 5} 个标题")

        print("\n" + "=" * 60)
        print("开始词频分析...")
        print("=" * 60)

        word_counts = analyze_word_frequency(titles)

        if word_counts:
            print(f"\n📊 词频统计结果 (前 {len(word_counts)} 个高频词):")
            print("-" * 40)
            for i, (word, count) in enumerate(word_counts, 1):
                print(f"{i:2d}. {word:<20} : {count:3d} 次")

            print("\n📈 正在生成词频分布图...")
            plot_word_frequency(word_counts)
            print("✓ 分析完成！")
        else:
            print("❌ 未能提取到有效词汇，请检查标题内容")

    print("\n" + "=" * 60)
    print("程序执行完毕")
    print("=" * 60)

