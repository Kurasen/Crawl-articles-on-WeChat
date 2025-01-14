import os
import re
from uuid import uuid4

import requests
import json

from app.util.utils import is_gzh_logo


# 创建文件夹并保存图片
def save_image(img_url, title, index,  folder):
    try:

        # 检查是否为公众号图标
        if is_gzh_logo(img_url):
            return None

        # 处理文件夹名称，替换非法字符
        safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)
        save_folder = os.path.join(folder, safe_title)

        # 创建文件夹（如果不存在）
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # 获取图片数据
        img_data = requests.get(img_url, timeout=10).content

        # 生成图片文件名（标题加三位序号）
        img_name = f"{safe_title}{index:03}.jpg"  # 图片序号格式为三位数字
        #img_name =f"{uuid4().hex}.jpg" #使用uUID生成唯一图片名
        img_path = os.path.join(save_folder, img_name)

        # 检查图片是否已存在
        if os.path.exists(img_path):
            #print(f"图片已存在，跳过: {img_path}")
            return img_path

        # 保存图片
        with open(img_path, "wb") as f:
            f.write(img_data)

        return img_path
    except Exception as e:
        print(f"下载图片失败: {img_url}, 错误: {e}")
        return None


# 保存文章信息到JSON文件
def save_article_json(article_data, folder, filename="articles.json"):

    save_path = os.path.join(folder, filename)

    # 确保目录存在
    os.makedirs(folder, exist_ok=True)

    # 检查是否已有文章
    if os.path.exists(save_path):
        with open(save_path, "r", encoding="utf-8") as file:
            try:
                existing_articles = json.load(file)
            except json.JSONDecodeError:
                existing_articles = []
    else:
        existing_articles = []

        # 检查标题是否已存在
    existing_titles = {article["title"] for article in existing_articles}
    if article_data["title"] in existing_titles:
        print(f"文章已存在，跳过保存: {article_data['title']}")
        return

    # 添加新文章
    existing_articles.append(article_data)

    # 保存数据到JSON文件
    with open(save_path, "a", encoding="utf-8") as file:
        json.dump(article_data, file, ensure_ascii=False, indent=4)
        file.write(",\n")  # 每篇文章之间添加逗号
