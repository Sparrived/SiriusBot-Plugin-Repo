def get_image_base64(image_path: str) -> str:
    """将图片文件转换为Base64编码字符串"""
    import base64
    file_exension = image_path.split('.')[-1].lower()
    if file_exension == "png":
        mime_type = "image/png"
    elif file_exension in ["jpg", "jpeg"]:
        mime_type = "image/jpeg"
    else:
        raise ValueError("仅支持 PNG 和 JPG/JPEG 格式的图片")
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')