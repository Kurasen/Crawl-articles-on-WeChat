# -*- coding: UTF-8 -*-
import os
import re

import requests
import time
import math
import random
from bs4 import BeautifulSoup
import json

from app.util.Array_format import fix_json_format
from app.util.remove import extract_content_with_types
from app.util.read_json import read_json
from app.util.save import save_image, save_article_json

# User agent list
user_agent_list = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Mobile Safari/537.36",
]

# 目标url
url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
cookie = "xxx"

# Headers
headers = {
    "Cookie": cookie,
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Mobile Safari/537.36",
}

data = {
    "token": "xxx",
    "lang": "zh_CN",
    "f": "json",
    "ajax": "1",
    "action": "list_ex",
    "begin": "0",
    "count": "5",
    "query": "",
    "fakeid": "",
    "type": "9",
}

fakeids = []

# 从文件中读取数据
file_path = "app/Source.json"
data_item = read_json(file_path)

# 保存所有文章信息的列表
all_articles = []

def get_page():

    # 获取总的文章数量
    content_json = requests.get(url, headers=headers, params=data).json()

    count = int(content_json["app_msg_cnt"]) if "app_msg_cnt" in content_json else 0

    # 检查JSON结构体数据
    #print(json.dumps(content_json, ensure_ascii=False, indent=4))

    if "app_msg_cnt" in content_json:
        count = int(content_json["app_msg_cnt"])
    else:
        print("无法获取文章数量，返回的数据结构可能有误")
        print(json.dumps(content_json, ensure_ascii=False, indent=4))
        count = 0

    print(f"总文章数量: {count}")
    # 计算页数，确保使用 math.ceil 来向上取整
    page = math.ceil(count / 5)
    print(f"总页数: {page}")
    return page

# 模拟请求的频率控制
def control_request_frequency():
    # 随机等待时间模拟正常用户行为
    time.sleep(random.randint(3, 10))  # 3到10秒之间

# 去重集合，记录已添加的内容
seen_titles = set()
seen_images = set()

for i in range(len(data_item)):

    if i == 2:
        break

    data["fakeid"] = data_item[i]["fakeid"]
    gzh_name = data_item[i]["name"]  # 公众号名称
    print(f"正在爬取公众号: {gzh_name}")


    # 公众号名称目录（存放图片）
    gzh_image_folder = os.path.join("data", "images", re.sub(r'[\\/*?:"<>|]', "_", gzh_name))  # 公众号根目录

    page = get_page()

    # 从第一页开始抓取所有文章
    for page_num in range(1, page + 1):
        # 测试
        if page_num == 2:
            break

        data["begin"] = (page_num - 1) * 5
        print(f"请求起始位置: {data['begin']}")
        content_json = requests.get(url, headers=headers, params=data).json()

        if "app_msg_list" not in content_json:
            print(f"无法获取文章列表，响应内容: {content_json}")
            break

        for item in content_json["app_msg_list"]:
            title = item["title"]

            # 检查文章标题是否已爬取
            if title in seen_titles:
                print(f"文章已爬取，跳过: {title}")
                continue
            seen_titles.add(title)

            article_url = item["link"]
            t = time.localtime(item["create_time"])
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", t)

            # 打印当前文章的标题和时间
            print(f"文章标题: {item['title']}, 发布时间: {create_time}")

            # 获取文章正文内容
            article_response = requests.get(article_url, headers=headers)
            soup = BeautifulSoup(article_response.content, "html.parser")

            # 获取正文内容，这里使用 HTML 内容传递给 `extract_content_with_types`
            article_html_content = str(soup.find("div", class_="rich_media_content"))
            if not article_html_content:
                # 尝试使用更通用的选择器
                article_html_content = str(soup.find("div", id="js_content"))
            # 提取并标记段落和图片的内容
            article_content = extract_content_with_types(article_html_content, title, gzh_image_folder)

            # 下载正文中的所有图片并替换为本地路径
            image_paths = []
            for img_tag in soup.find_all("img"):
                img_url = img_tag.get("data-src") or img_tag.get("src")
                if img_url:
                    # 根据 img_url 查找对应的本地路径
                    for content_item in article_content:
                        if content_item["type"] == "images" and content_item["content"].endswith(os.path.basename(img_url)):
                            img_tag['src'] = content_item["content"]  # 替换为本地路径

            article_data = {
                "title": title,
                "link": article_url,
                "create_time": create_time,
                "content": article_content,  # 已标记类型的内容
                "timestamp": item["create_time"],  # 用于排序
                "gzh_name": gzh_name
            }

            all_articles.append(article_data)
            control_request_frequency()

        control_request_frequency()  # 控制请求间隔时间


# 打印所有文章数据的时间戳以验证
# for article in all_articles:
#     print(f"文章标题: {article['title']}, 时间戳: {article['timestamp']}, 发布时间: {article['create_time']}")

# 确保 `timestamp` 是整数

    for article in all_articles:
        article["timestamp"] = int(article["timestamp"])  # 如果是字符串，转为整数

    # 按时间戳升序排序（最早的文章排在前面）
    all_articles.sort(key=lambda x: x["timestamp"])

    # 保存排序后的文章
    json_path = os.path.join("data", "word", "articles.json")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)  # 确保目录存在

    for article in all_articles:
        print(f"排序后文章标题: {article['title']}, 发布时间: {article['create_time']}")

        gzh_name = article['gzh_name']  # 获取当前文章所属的公众号名称
        # 公众号名称目录（存放文章JSON文件）
        gzh_word_folder = os.path.join("data", "word", re.sub(r'[\\/*?:"<>|]', "_", gzh_name))

        # 为每个公众号生成独立的 articles.json 文件
        json_path = os.path.join(gzh_word_folder, "articles.json")

        save_article_json(article, folder=gzh_word_folder, filename="articles.json")

        fix_json_format()

