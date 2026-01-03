import requests
from bs4 import BeautifulSoup
import time
import os
import re


class QianlongPoetryCrawler:
    def __init__(self):
        self.base_url = "https://www.diancang.xyz"
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.output_file = r"C:\Users\任宇轩\Desktop\信息系统设计与分析\乾隆诗词2.txt"

    def get_chapter_links(self, url):
        """获取所有章节链接"""
        try:
            print(f"正在访问: {url}")
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            print(f"响应状态码: {response.status_code}")

            soup = BeautifulSoup(response.text, 'html.parser')

            # 调试：保存HTML内容以便分析
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("已保存页面HTML到 debug_page.html")

            # 多种方式查找章节链接
            chapter_links = []

            # 方式1：通过ID查找
            booklist = soup.find('ul', {'id': 'booklist'})
            if booklist:
                print("找到ID为booklist的ul元素")
                links = booklist.find_all('a', href=True)
                print(f"在booklist中找到 {len(links)} 个链接")
            else:
                # 方式2：通过class查找
                booklist = soup.find('ul', class_='list-group')
                if booklist:
                    print("找到class为list-group的ul元素")
                    links = booklist.find_all('a', href=True)
                    print(f"在list-group中找到 {len(links)} 个链接")
                else:
                    # 方式3：查找所有包含章节的链接
                    print("尝试查找所有可能的章节链接...")
                    links = soup.find_all('a', href=True)
                    print(f"在页面中找到 {len(links)} 个总链接")

            # 过滤出有效的章节链接
            for link in links:
                href = link.get('href', '')
                title = link.get_text().strip()

                # 检查是否是有效的章节链接
                if (href and
                        ('shicixiqu/8921' in href or '/175' in href) and
                        title and
                        len(title) > 0):

                    # 构建完整URL
                    if href.startswith('http'):
                        full_url = href
                    else:
                        full_url = self.base_url + href if href.startswith('/') else f"{self.base_url}/{href}"

                    chapter_links.append((title, full_url))
                    print(f"找到章节: {title} -> {full_url}")

            # 去重
            chapter_links = list(dict.fromkeys(chapter_links))
            print(f"最终找到 {len(chapter_links)} 个唯一章节")

            return chapter_links

        except Exception as e:
            print(f"获取章节链接时出错: {e}")
            import traceback
            traceback.print_exc()
            return []

    def extract_poetry_content(self, html_content):
        """从HTML内容中提取诗词文本，去除翻译"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # 移除不需要的元素
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form']):
                element.decompose()

            # 尝试多种方式获取内容
            content_areas = [
                soup.find('div', class_='panel-body'),
                soup.find('div', class_='content'),
                soup.find('div', id='content'),
                soup.find('article'),
                soup.find('div', class_='m-summary')
            ]

            main_content = None
            for area in content_areas:
                if area:
                    main_content = area
                    break

            if not main_content:
                # 如果没有找到特定区域，使用body
                main_content = soup.find('body')

            if main_content:
                # 获取文本内容
                text = main_content.get_text(separator='\n', strip=True)

                # 处理文本，去除翻译和注释
                lines = text.split('\n')
                poetry_lines = []

                for line in lines:
                    line = line.strip()
                    if (line and
                            len(line) > 1 and
                            not any(keyword in line for keyword in [
                                '翻译', '注释', '赏析', '注：', '译：', '【注】',
                                '导航', '菜单', '首页', '搜索', '书架', '下载',
                                'Copyright', '版权', '©'
                            ]) and
                            not line.startswith('function') and
                            not 'var ' in line):
                        poetry_lines.append(line)

                content = '\n'.join(poetry_lines)
                return content
            else:
                return "未能提取到内容"

        except Exception as e:
            print(f"提取内容时出错: {e}")
            return f"提取内容时出错: {e}"

    def crawl_chapter(self, chapter_url):
        """爬取单个章节的内容"""
        try:
            print(f"正在爬取: {chapter_url}")
            response = self.session.get(chapter_url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code == 200:
                content = self.extract_poetry_content(response.text)
                return content
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return ""
        except Exception as e:
            print(f"爬取章节时出错 {chapter_url}: {e}")
            return ""

    def save_to_file(self, title, content):
        """保存内容到文件"""
        try:
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n{'=' * 60}\n")
                f.write(f"{title}\n")
                f.write(f"{'=' * 60}\n\n")
                f.write(content)
                f.write("\n")
            print(f"已保存: {title}")
        except Exception as e:
            print(f"保存文件时出错: {e}")

    def run(self, start_url):
        """运行爬虫"""
        print("开始爬取乾隆诗词...")
        print(f"输出文件: {self.output_file}")

        # 确保输出目录存在
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

        # 清空或创建输出文件
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("乾隆诗词全集\n")
            f.write("=" * 60 + "\n")
            f.write("爬取时间: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
            f.write("=" * 60 + "\n\n")

        # 获取所有章节链接
        chapter_links = self.get_chapter_links(start_url)

        if not chapter_links:
            print("未找到章节链接，尝试备用方案...")
            # 尝试使用目录页
            catalog_url = "https://www.diancang.xyz/shicixiqu/8921/"
            if start_url != catalog_url:
                chapter_links = self.get_chapter_links(catalog_url)

        if not chapter_links:
            print("仍然未找到章节链接，程序退出")
            return

        print(f"开始爬取 {len(chapter_links)} 个章节...")

        # 爬取每个章节
        success_count = 0
        for i, (title, url) in enumerate(chapter_links, 1):
            print(f"\n进度: {i}/{len(chapter_links)} - {title}")

            content = self.crawl_chapter(url)
            if content and len(content.strip()) > 10:  # 只有有实际内容才保存
                self.save_to_file(title, content)
                success_count += 1
            else:
                print(f"章节 {title} 内容为空或过短，跳过")

            # 添加延迟，避免请求过于频繁
            time.sleep(2)

        print(f"\n爬取完成！成功爬取 {success_count}/{len(chapter_links)} 个章节")
        print(f"诗词已保存到: {self.output_file}")


def main():
    # 您提供的URL
    start_url = "https://www.shidianguji.com/book/HY0939/chapter/1kduqnljmht83?version=41"

    crawler = QianlongPoetryCrawler()

    try:
        crawler.run(start_url)
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()