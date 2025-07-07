import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import random
import time
import os
import sys
import pygame

class DesktopPet:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.geometry("450x450+500+500")

        # 获取当前脚本所在目录
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        self.base_path = base_path

        # 创建透明画布 - 使用跨平台透明色
        self.canvas_frame = tk.Frame(root, bg='#abcdef')
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            self.canvas_frame,
            highlightthickness=0,
            bg='#abcdef',
            width=450,
            height=450
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)


        # 设置透明色 - 使用独特颜色
        self.root.attributes("-transparentcolor", "#abcdef")

        self.x = 500
        self.y = 500
        self.is_dragging = False
        self.pre_drag_state = None
        self.drag_start_time = 0
        self.load_images()

        # 在画布上创建图像
        self.pet_image = self.canvas.create_image(225, 225, image=self.sing_frames[0])

        self.state = "sing"
        self.frame_index = 0
        self.current_frames = self.sing_frames

        self.state_change_time = 5
        self.last_state_change = time.time()

        # 绑定事件
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.show_context_menu)

        # 使用单独的动画更新线程
        self.animation_running = True
        self.update_animation()
        self.update_behavior()

        # 添加图片显示配置
        self.image_config = {
            "image_path": "images/special_image.png",  # 默认图片路径
            "image_size": (600, 600),  # 默认显示尺寸
            "display_time": 10000  # 显示时间(毫秒)
        }

        pygame.mixer.init()
        self.drag_sound = pygame.mixer.Sound("sounds/结束乐队-ラブソングが歌えない.wav")  # Path to your sound file
        self.xi_sound = pygame.mixer.Sound("sounds/結束バンド - 転がる岩、君に朝が降る (翻转岩石，晨光洒落你身).mp3")


    def load_images(self):
        """加载并优化GIF图像处理"""
        # self.idle_frames = self.optimize_gif(os.path.join(self.base_path, "Bochhi/DeskPets/enjoyingMusic_Bocchi.gif"))
        # idle抠图效果一直不好我就放弃了
        self.walk_frames = self.optimize_gif("Bochhi/DeskPets/(4).gif")
        self.dance_frames = self.optimize_gif("Bochhi/DeskPets/(3).gif")
        self.sing_frames = self.optimize_gif("Bochhi/DeskPets/(1).gif")
        self.crazy_frames = self.optimize_gif("Bochhi/DeskPets/(2).gif")

    def optimize_gif(self, path, target_size=(120, 120)):
        """加载并优化GIF，保持透明度和清晰度"""
        try:
            gif = Image.open(path)
            frames = []

            # 获取全局调色板
            global_palette = gif.getpalette()

            for frame in ImageSequence.Iterator(gif):
                # 保留原始模式处理
                if frame.mode == 'P':
                    # 应用全局调色板保持一致性
                    if global_palette:
                        frame.putpalette(global_palette)

                    # 转换为RGBA并保留原始颜色
                    frame = frame.convert("RGBA")

                    # 精确提取透明度
                    if 'transparency' in frame.info:
                        transparency = frame.info['transparency']
                        # 创建精确的透明度蒙版
                        mask = Image.new("L", frame.size, 255)
                        mask_data = []
                        for y in range(frame.size[1]):
                            for x in range(frame.size[0]):
                                pix = frame.getpixel((x, y))
                                # 检查是否透明像素
                                if isinstance(pix, int) and pix == transparency:
                                    mask_data.append(0)
                                elif isinstance(pix, tuple) and pix[3] == 0:
                                    mask_data.append(0)
                                else:
                                    mask_data.append(255)
                        mask.putdata(mask_data)
                        frame.putalpha(mask)

                # 高质量缩放
                if frame.size != target_size:
                    frame = frame.resize(target_size, Image.LANCZOS)

                # 创建PhotoImage时保留透明度
                photo = ImageTk.PhotoImage(frame)
                frames.append(photo)

            return frames
        except Exception as e:
            print(f"GIF加载错误: {e}")
            # 回退到简单加载
            try:
                gif = Image.open(path)
                return [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(gif)]
            except:
                print(f"无法加载GIF: {path}")
                return []

    def update_animation(self):
        """专用的动画更新函数"""
        if self.animation_running and self.current_frames:
            # 计算帧索引
            if self.is_dragging:
                elapsed = time.time() - self.drag_start_time
                frame_rate = 10
                self.frame_index = int(elapsed * frame_rate) % len(self.crazy_frames)
            else:
                self.frame_index = (self.frame_index + 1) % len(self.current_frames)

            # 更新画布上的图像
            self.canvas.itemconfig(self.pet_image, image=self.current_frames[self.frame_index])

            self.canvas_frame.configure(bg='#abcdef')
            self.canvas.configure(bg='#abcdef')


        # 使用after_idle避免动画阻塞
        self.root.after_idle(lambda: self.root.after(50, self.update_animation))

    def update_behavior(self):
        """行为更新函数，与动画更新分离"""
        if not self.is_dragging:
            current_time = time.time()
            if current_time - self.last_state_change > self.state_change_time:
                all_states = ["walk", "dance", "sing"]
                possible_states = [s for s in all_states if s != self.state]
                if not possible_states:
                    possible_states = all_states

                self.state = random.choice(possible_states)
                self.last_state_change = current_time

                # if self.state == "idle":
                #     self.current_frames = self.idle_frames
                if self.state == "walk":
                    self.current_frames = self.walk_frames
                elif self.state == "dance":
                    self.current_frames = self.dance_frames
                elif self.state == "sing":
                    self.current_frames = self.sing_frames
                self.frame_index = 0

            if self.state == "walk":
                self.move_randomly()
            if self.state == "dance":
                self.dance_randomly()

        self.root.after(100, self.update_behavior)

    def move_randomly(self):
        self.x += random.randint(-50, 50)
        # self.y += random.randint(-10, 10)
        # 确保宠物在屏幕内
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = max(0, min(screen_width - 300, self.x))
        self.y = max(0, min(screen_height - 300, self.y))
        self.root.geometry(f"450x450+{self.x}+{self.y}")

    def dance_randomly(self):
        self.x += random.randint(-10, 10)
        self.y += random.randint(-10, 10)
        # 确保宠物在屏幕内
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = max(0, min(screen_width - 300, self.x))
        self.y = max(0, min(screen_height - 300, self.y))
        self.root.geometry(f"450x450+{self.x}+{self.y}")

    def on_click(self, event):
        all_states = ["walk", "dance", "sing"]
        possible_states = [state for state in all_states if state != self.state]
        if not possible_states:
            possible_states = all_states

        new_state = random.choice(possible_states)
        self.state = new_state

        # if self.state == "idle":
        #     self.current_frames = self.idle_frames
        if self.state == "walk":
            self.current_frames = self.walk_frames
        elif self.state == "dance":
            self.current_frames = self.dance_frames
        elif self.state == "sing":
            self.current_frames = self.sing_frames

        self.frame_index = 0

    def on_drag(self, event):
        if not self.is_dragging:
            self.is_dragging = True
            self.pre_drag_state = self.state
            self.drag_start_time = time.time()
            self.current_frames = self.crazy_frames
            self.frame_index = 0
            self.drag_sound.play()

        posX = event.x_root - 225
        posY = event.y_root - 225

        # 确保窗口在屏幕内
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        posX = max(0, min(screen_width - 300, posX))
        posY = max(0, min(screen_height - 300, posY))
        self.x = int(posX)
        self.y = int(posY)

        self.root.geometry(f"450x450+{self.x}+{self.y}")

    def on_release(self, event):
        if self.is_dragging:
            self.is_dragging = False
            self.drag_sound.fadeout(1)

            if self.pre_drag_state:
                self.state = self.pre_drag_state

                # if self.state == "idle":
                #     self.current_frames = self.idle_frames
                if self.state == "walk":
                    self.current_frames = self.walk_frames
                elif self.state == "dance":
                    self.current_frames = self.dance_frames
                elif self.state == "sing":
                    self.current_frames = self.sing_frames

                self.frame_index = 0
                self.pre_drag_state = None

    def show_context_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="删除桌宠", command=self.exit_program)
        # 添加显示图片选项
        menu.add_command(label="“波奇酱是一个可爱的女人捏”", command=self.show_special_image)

        menu.post(event.x_root, event.y_root)

    def exit_program(self):
        self.animation_running = False
        self.root.destroy()
        sys.exit(0)

    def show_special_image(self):
        """显示特殊图片"""
        try:
            # 创建新窗口
            image_window = tk.Toplevel(self.root)
            image_window.title("Man Fuck U")
            image_window.attributes("-topmost", True)  # 保持在最前面

            # 加载并调整图片大小
            img = Image.open("images/special.bmp")
            img = img.convert("RGBA")  # 确保有alpha通道

            # 按比例调整大小
            target_size = self.image_config["image_size"]
            img_ratio = img.width / img.height
            target_ratio = target_size[0] / target_size[1]

            if img_ratio > target_ratio:
                # 宽度是限制因素
                new_width = target_size[0]
                new_height = int(target_size[0] / img_ratio)
            else:
                # 高度是限制因素
                new_height = target_size[1]
                new_width = int(target_size[1] * img_ratio)

            img = img.resize((new_width, new_height), Image.LANCZOS)

            # 创建PhotoImage
            photo = ImageTk.PhotoImage(img)

            # 创建标签显示图片
            img_label = tk.Label(image_window, image=photo)
            img_label.image = photo  # 保持引用
            img_label.pack(padx=10, pady=10)

            # 播放音效
            self.xi_sound.play(0, 10000)

            # 自动关闭定时器
            image_window.after(self.image_config["display_time"], image_window.destroy)


        except Exception as e:
            print(f"显示图片失败: {e}")
            # 显示错误消息
            error_window = tk.Toplevel(self.root)
            error_window.title("错误")
            error_label = tk.Label(
                error_window,
                text=f"无法加载图片: {self.image_config['image_path']}\n{e}",
                fg="red",
                padx=20,
                pady=20
            )
            error_label.pack()
            error_window.after(3000, error_window.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    pet = DesktopPet(root)
    root.mainloop()