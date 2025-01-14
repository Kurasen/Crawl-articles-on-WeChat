def is_gzh_logo(img_url):
    """
    判断是否为公众号图标图片，通过 URL 特定特征判断。
    """
    # 根据 URL 的特征进行判断（例如包含 wxfrom=5）
    return "wxfrom=5" in img_url or "wx_lazy=1" in img_url
