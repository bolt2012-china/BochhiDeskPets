import PyInstaller.__main__
import os
import shutil
import sys
import logging
import glob

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('build.log')
    ]
)


def validate_resources():
    """验证所有必需的资源文件是否存在"""
    required_resources = {
        'gifs': [
            'Bochhi/DeskPets/(1).gif',
            'Bochhi/DeskPets/(2).gif',
            'Bochhi/DeskPets/(3).gif',
            'Bochhi/DeskPets/(4).gif'
        ],
        'images': [
            'images/special.bmp'
        ],
        'sounds': [
            'sounds/Happy_Birthday_Crowd.wav'
        ],
        'icons': [
            'icon.ico'
        ]
    }

    missing_files = []

    # 检查GIF文件
    for gif in required_resources['gifs']:
        if not os.path.exists(gif):
            missing_files.append(gif)
            logging.error(f"缺少GIF文件: {gif}")

    # 检查图片文件
    for img in required_resources['images']:
        if not os.path.exists(img):
            missing_files.append(img)
            logging.error(f"缺少图片文件: {img}")

    # 检查图标文件
    for icon in required_resources['icons']:
        if not os.path.exists(icon):
            logging.warning(f"缺少图标文件: {icon} - 将使用默认图标")

    # 检查声音文件
    for sound in required_resources['sounds']:
        if not os.path.exists(sound):
            missing_files.append(sound)
            logging.error(f"缺少声音文件：{sound}")

    if missing_files:
        logging.critical("缺少关键资源文件，打包无法继续！")
        return False

    return True


def clean_build_artifacts():
    """清理之前的构建产物"""
    artifacts = ['dist', 'build', 'main.spec']

    for artifact in artifacts:
        if os.path.exists(artifact):
            try:
                if os.path.isdir(artifact):
                    shutil.rmtree(artifact)
                else:
                    os.remove(artifact)
                logging.info(f"已清理: {artifact}")
            except Exception as e:
                logging.error(f"清理 {artifact} 失败: {e}")


def get_resource_paths():
    """获取所有需要包含的资源路径"""
    resource_paths = []

    # 主资源目录
    resource_dir = 'Bochhi/DeskPets'
    target_dir = 'Bochhi'

    if os.path.exists(resource_dir):
        resource_paths.append(('Bochhi/DeskPets', 'Bochhi'))
    else:
        logging.error(f"资源目录不存在: {resource_dir}")

    # 图片目录
    image_dir = 'images'
    if os.path.exists(image_dir):
        resource_paths.append(('images', 'images'))
    else:
        logging.warning(f"图片目录不存在: {image_dir}")

    # 声音目录
    sounds_dir = 'sounds'
    if os.path.exists(sounds_dir):
        resource_paths.append(('sounds', 'sounds'))
    else:
        logging.warning(f"声音目录不存在: {sounds_dir}")

    # 添加所有其他必要的文件
    additional_files = [
        'icon.ico',
        'desktop_pet.log'  # 日志文件
    ]

    for file in additional_files:
        if os.path.exists(file):
            resource_paths.append((file, '.'))
        else:
            logging.warning(f"附加文件不存在: {file}")

    return resource_paths


def main():
    logging.info("=" * 50)
    logging.info("开始桌面宠物打包过程")
    logging.info("=" * 50)

    # 步骤1: 验证资源文件
    logging.info("验证资源文件...")
    if not validate_resources():
        logging.critical("资源验证失败，打包中止！")
        sys.exit(1)

    # 步骤2: 清理之前的构建产物
    logging.info("清理构建产物...")
    clean_build_artifacts()

    # 步骤3: 准备打包参数
    logging.info("准备打包参数...")
    params = [
        'main.py',  # 主程序文件
        '--onefile',  # 打包为单个exe
        '--windowed',  # 不显示控制台窗口
        '--name=DesktopPet',  # 生成的exe名称
        '--clean',  # 清理临时文件
        '--noconfirm',  # 不询问确认
        '--log-level=WARN'  # 减少PyInstaller日志
    ]

    # 步骤4: 添加资源文件
    resource_paths = get_resource_paths()
    for source, target in resource_paths:
        params.extend(['--add-data', f'{source}{os.pathsep}{target}'])
        logging.info(f"添加资源: {source} -> {target}")

    # 步骤5: 添加图标
    if os.path.exists('icon.ico'):
        params.extend(['--icon', 'icon.ico'])
        logging.info("添加应用程序图标")

    # 步骤6: 添加隐藏导入（如果需要）
    hidden_imports = [
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageSequence'
    ]

    for imp in hidden_imports:
        params.extend(['--hidden-import', imp])

    # 步骤7: 执行打包
    logging.info("开始打包过程...")
    logging.info(f"PyInstaller 参数: {' '.join(params)}")

    try:
        PyInstaller.__main__.run(params)
        logging.info("打包成功完成!")
    except Exception as e:
        logging.critical(f"打包过程中出错: {e}")
        sys.exit(1)

    # 步骤8: 后处理
    logging.info("执行后处理...")

    # 复制额外的文件到dist目录
    dist_dir = 'dist'
    if os.path.exists(dist_dir):
        # 复制资源目录
        if os.path.exists('Bochhi'):
            try:
                shutil.copytree('Bochhi', os.path.join(dist_dir, 'Bochhi'))
                logging.info("复制 Bochhi 目录到 dist")
            except Exception as e:
                logging.error(f"复制 Bochhi 目录失败: {e}")

        # 复制图片目录
        if os.path.exists('images'):
            try:
                shutil.copytree('images', os.path.join(dist_dir, 'images'))
                logging.info("复制 images 目录到 dist")
            except Exception as e:
                logging.error(f"复制 images 目录失败: {e}")
        # 复制声音目录
        if os.path.exists('sounds'):
            try:
                shutil.copytree('sounds', os.path.join(dist_dir, 'sounds'))
                logging.info("复制 sounds 目录到 dist")
            except Exception as e:
                logging.error(f"复制 sounds 目录失败: {e}")

        # 创建配置文件
        config_files = ['image_config.json', 'music_config.json']
        for config in config_files:
            if os.path.exists(config):
                try:
                    shutil.copy(config, dist_dir)
                    logging.info(f"复制配置文件: {config}")
                except Exception as e:
                    logging.error(f"复制 {config} 失败: {e}")

    logging.info("=" * 50)
    logging.info("打包过程完成!")
    logging.info("=" * 50)
    print("\n打包完成! 可执行文件位于 dist 文件夹")
    print("请确保以下目录与 DesktopPet.exe 放在同一目录下:")
    print("  - Bochhi/ (包含所有GIF资源)")
    print("  - images/ (包含特殊图片)")
    print("  - sounds/ (包含声音文件)")
    print("  - 配置文件 (如 image_config.json)")


if __name__ == "__main__":
    main()