import requests
from bs4 import BeautifulSoup
import time
import os
import re
from urllib.parse import urljoin


class QianlongPoetrySpider:
    def __init__(self):
        self.base_url = "https://www.gushicimingju.com"
        self.start_url = "https://www.gushicimingju.com/shiren/qianlong/"
        self.output_file = r"C:\Users\任宇轩\Desktop\信息系统设计与分析\乾隆诗词.txt"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        })
        self.processed_count = 0

    def get_page_content(self, url):
        """获取页面内容"""
        try:
            response = self.session.get(url)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return response.text
            else:
                print(f"请求失败，状态码：{response.status_code}")
                return None
        except Exception as e:
            print(f"请求出错：{e}")
            return None

    def get_poetry_detail(self, detail_url):
        """获取诗词详情页的完整内容"""
        try:
            html = self.get_page_content(detail_url)
            if not html:
                return None

            soup = BeautifulSoup(html, 'html.parser')

            # 尝试多种选择器来获取完整的诗词内容
            content_selectors = [
                '.shici-content',  # 常见的诗词内容选择器
                '.shici-text',
                '.poem-content',
                '.main-content .content',
                '.shici-quan',
                'div[class*="content"]',
                'div[class*="text"]'
            ]

            full_content = None
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    # 清理内容，移除多余的标签和空白
                    text = content_element.get_text().strip()
                    # 移除可能的注释、说明等
                    lines = text.split('\n')
                    clean_lines = []
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith(('注：', '注释：', '说明：', '【', '（')):
                            clean_lines.append(line)
                    full_content = '\n'.join(clean_lines)
                    if len(full_content) > 20:  # 确保内容足够长
                        break

            # 如果上述选择器都没找到，尝试获取页面中所有的文本内容
            if not full_content:
                main_content = soup.select_one('.main-content')
                if main_content:
                    full_content = main_content.get_text().strip()

            return full_content

        except Exception as e:
            print(f"获取详情页内容出错：{e}")
            return None

    def parse_poetry_list(self, html):
        """解析诗词列表"""
        soup = BeautifulSoup(html, 'html.parser')
        poetry_list = []

        # 查找诗词列表
        poetry_items = soup.select('ul.simple-shiciqu li')

        for item in poetry_items:
            try:
                # 提取诗词标题和链接
                title_tag = item.select_one('a[href*="/gushi/shi/"]')
                if not title_tag:
                    continue

                title = title_tag.get_text().strip()
                relative_url = title_tag.get('href')
                detail_url = urljoin(self.base_url, relative_url)

                # 提取列表页中的内容片段
                content_tag = item.select_one('span.content')
                list_content = content_tag.get_text().strip() if content_tag else ""

                # 检查内容是否有省略号
                has_ellipsis = '...' in list_content or '…' in list_content or '...' in title_tag.get_text()

                # 如果内容有省略号，获取详情页完整内容
                if has_ellipsis and list_content:
                    print(f"  获取完整内容: {title}")
                    full_content = self.get_poetry_detail(detail_url)

                    # 如果详情页获取失败，使用列表页内容
                    if full_content and len(full_content) > len(list_content):
                        content = full_content
                    else:
                        content = list_content
                    time.sleep(0.5)  # 详情页请求间隔
                else:
                    content = list_content

                if title and content:
                    poetry_list.append({
                        'title': title,
                        'content': content,
                        'detail_url': detail_url
                    })

            except Exception as e:
                print(f"解析诗词项出错：{e}")
                continue

        return poetry_list

    def get_total_pages(self, html):
        """获取总页数"""
        soup = BeautifulSoup(html, 'html.parser')

        # 从分页信息中获取总页数
        page_info = soup.select_one('li.info span')
        if page_info:
            info_text = page_info.get_text()
            # 使用正则表达式提取页数
            match = re.search(r'共(\d+)页', info_text)
            if match:
                return int(match.group(1))

        # 如果没有找到分页信息，从分页链接中获取最大页数
        page_links = soup.select('ul.pagination li a[href*="/shiren/qianlong/page"]')
        if page_links:
            page_numbers = []
            for link in page_links:
                href = link.get('href', '')
                match = re.search(r'/page(\d+)/', href)
                if match:
                    page_numbers.append(int(match.group(1)))
            if page_numbers:
                return max(page_numbers)

        return 1  # 默认只有1页

    def save_poetry(self, poetry_list, page_num):
        """保存诗词到文件"""
        with open(self.output_file, 'a', encoding='utf-8') as f:
            for i, poetry in enumerate(poetry_list, 1):
                # 计算全局序号
                self.processed_count += 1
                f.write(f"{self.processed_count}.《{poetry['title']}》\n")
                f.write(f"{poetry['content']}\n")
                f.write("-" * 50 + "\n\n")

    def run(self, max_pages=None):
        """运行爬虫"""
        print("开始爬取乾隆诗词...")

        # 检查输出目录是否存在
        output_dir = os.path.dirname(self.output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 清空或创建输出文件
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("乾隆诗词全集\n")
            f.write("=" * 50 + "\n\n")

        # 获取第一页内容
        first_page_html = self.get_page_content(self.start_url)
        if not first_page_html:
            print("无法获取第一页内容，程序退出")
            return

        # 获取总页数
        total_pages = self.get_total_pages(first_page_html)
        if max_pages and max_pages < total_pages:
            total_pages = max_pages
        print(f"总页数：{total_pages}")

        # 处理第一页
        print(f"正在处理第1页...")
        poetry_list = self.parse_poetry_list(first_page_html)
        self.save_poetry(poetry_list, 1)
        print(f"第1页完成，获取到{len(poetry_list)}首诗词")

        # 处理后续页面
        for page in range(2, total_pages + 1):
            print(f"正在处理第{page}页...")

            # 构建页面URL
            if page == 1:
                url = self.start_url
            else:
                url = f"{self.base_url}/shiren/qianlong/page{page}/"

            # 获取页面内容
            html = self.get_page_content(url)
            if not html:
                print(f"第{page}页获取失败，跳过")
                continue

            # 解析诗词列表
            poetry_list = self.parse_poetry_list(html)
            if poetry_list:
                self.save_poetry(poetry_list, page)
                print(f"第{page}页完成，获取到{len(poetry_list)}首诗词")
            else:
                print(f"第{page}页没有找到诗词")

            # 添加延迟，避免请求过于频繁
            time.sleep(1)

        print(f"\n爬取完成！诗词已保存到：{self.output_file}")
        print(f"总共爬取了{self.processed_count}首诗词")


def main():
    spider = QianlongPoetrySpider()

    # 测试模式：只爬取前3页
    # spider.run(max_pages=3)

    # 完整模式：爬取所有页面
    spider.run()


if __name__ == "__main__":
    main()