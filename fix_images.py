# fix_images.py
import os
from PIL import Image
from tqdm import tqdm


def remove_icc_profile(image_path):
    """移除图像的ICC配置文件"""
    try:
        img = Image.open(image_path)

        # 检查是否存在ICC配置文件
        if 'icc_profile' in img.info:
            # 创建无ICC配置文件的图像副本
            data = list(img.getdata())
            new_img = Image.new(img.mode, img.size)
            new_img.putdata(data)

            # 保存格式取决于原始文件扩展名
            ext = os.path.splitext(image_path)[1].lower()
            if ext in ['.png', '.gif']:
                new_img.save(image_path, format=ext[1:])
            else:
                new_img.save(image_path)
            print(f"Removed ICC profile from: {image_path}")
        else:
            print(f"No ICC profile found in: {image_path}")
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")


def process_folder(folder_path):
    """处理文件夹中的所有图像"""
    supported_exts = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    for root, dirs, files in os.walk(folder_path):
        for file in tqdm(files):
            if any(file.lower().endswith(ext) for ext in supported_exts):
                remove_icc_profile(os.path.join(root, file))


if __name__ == "__main__":
    # 处理包含所有GIF的文件夹
    process_folder("Bochhi/DeskPets")
    print("所有图像处理完成！")