import json

def fix_json_format():

    # 读取文件内容
    with open('D:\\Technology\\Code\\Python\\Crawl articles on WeChat\\data\\word\\土壤观察\\articles.json', 'r', encoding='utf-8') as file:
        content = file.read()

    # 用逗号连接所有对象，并包裹在列表中
    fixed_content = "[" + content.strip().rstrip(',') + "]"

    # 将修复后的内容写回到一个新的 JSON 文件
    with open('D:\\Technology\\Code\\Python\\Crawl articles on WeChat\\data\\word\\土壤观察\\fixed_articles.json', 'w', encoding='utf-8') as file:
        file.write(fixed_content)

print("文件格式已修复，已保存为 fixed_articles.json")

# 修复文件格式并去掉最后一篇文章的逗号
# def fix_json_format(file_path, output_path):
#     with open(file_path, 'r', encoding='utf-8') as file:
#         content = file.read()
#
#     # 用逗号连接所有对象，并包裹在列表中
#     fixed_content = "[" + content.strip().rstrip(',') + "]"
#
#     # 加载为 JSON 数据以验证格式
#     articles = json.loads(fixed_content)
#
#     # 保存修复后的内容到新的 JSON 文件
#     with open(output_path, 'w', encoding='utf-8') as file:
#         json.dump(articles, file, ensure_ascii=False, indent=4)
