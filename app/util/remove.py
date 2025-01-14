import unicodedata
from bs4 import BeautifulSoup
from app.util.save import save_image
from app.util.utils import is_gzh_logo


#移除嵌套重复的段落
def remove_nested_duplicates(content_list):
    cleaned_content = []
    for i, item in enumerate(content_list):
        if item["type"] == "text":
            current_text = item["content"].strip()
            is_nested = False
            for other_item in content_list:
                if other_item["type"] == "text" and other_item["content"] != current_text:
                    # 如果当前段落完全包含在另一段中，则标记为嵌套重复
                    if current_text in other_item["content"]:
                        is_nested = True
                        break
            if not is_nested:
                cleaned_content.append(item)
        else:
            cleaned_content.append(item)  # 图片直接保留
    return cleaned_content

def extract_content_with_types(html_content, title, image_folder):
    soup = BeautifulSoup(html_content, "html.parser")

    # 用于存储内容及其类型的列表
    content_with_types = []

    # 去重集合，记录已添加的内容
    seen_contents = set()
    seen_images = set()

    image_index = 1  # 图片序号


    for section in soup.find_all("section"):
        # 提取 <section> 内的文本和图片
        for element in section.find_all(["p", "img", "span"]):
            if element.name in ["p", "span"]:  # 处理段落和内联文本
                # 确保段落没有被隐藏
                if "visibility" in element.attrs.get("style", "") and "hidden" in element.attrs["style"]:
                    continue  # 跳过隐藏内容
                cleaned_text = ' '.join(element.stripped_strings).strip()
                if cleaned_text and cleaned_text not in seen_contents:  # 避免重复添加
                    content_with_types.append({"type": "text", "content": cleaned_text})
                    seen_contents.add(cleaned_text)
            elif element.name == "img":
                img_url = element.get("data-src") or element.get("src")
                if img_url and img_url not in seen_images:
                    img_path = save_image(img_url, title, image_index, folder=image_folder)
                    if img_path:
                        content_with_types.append({"type": "images", "content": img_path})
                        seen_images.add(img_url)
                        image_index += 1

    # 清理嵌套重复内容
    content_with_types = remove_nested_duplicates(content_with_types)
    return content_with_types
