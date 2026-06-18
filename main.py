import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox

import cv2
import numpy as np
from PIL import Image, ImageTk


class ImageProcessorApp:
    """
    Главный класс приложения для обработки изображений.
    Управляет загрузкой, отображением и обработкой изображений.
     """
    def __init__(self, root):
        """
        Конструктор класса. Инициализирует главное окно интерфейса

        :param root: Корневой объект Tkinter (главное окно)
        """
        # Инициализация главного окна
        self.root = root
        self.root.title("Image Processor")
        self.root.geometry("1400x750")

        # Переменные для хранения изображений
        self.original_image = None # Исходное изображение
        self.current_image = None # Текущее обработанное изображение
        self.rectangle_coords = None # Координаты прямоугольника

        # Создание левой панели с элементами управления
        left_panel = tk.Frame(root, width=450, bg='#f0f0f0')
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)

        # Создание правой панели для отображения изображения
        right_panel = tk.Frame(root)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Холст для отображения изображения
        self.canvas_img = tk.Canvas(right_panel, bg='#2b2b2b')
        self.canvas_img.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Привязка события изменения размера окна
        self.canvas_img.bind("<Configure>", lambda e: self.update_display())

        # Строка статуса в нижней части окна
        self.status = tk.Label(root, text="Готов", bd=1,
                               relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        # Создание интерфейса на левой панели
        self.create_interface(left_panel)

    def create_interface(self, parent):
        """
        Создание графического интерфейса приложения.

        :param parent: Родительский контейнер (левая панель)
         """
        # Основной контейнер для элементов управления
        main_frame = tk.Frame(parent, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Блок 1 - Загрузка изображения с устройства
        frame1 = tk.LabelFrame(main_frame, text="1. Загрузка изображения",
                               font=('Arial', 10, 'bold'), padx=10,
                               pady=5, bg='#f0f0f0')
        frame1.pack(fill=tk.X, pady=5)
        tk.Button(frame1, text="Выбрать файл",
                  command=self.load_image, height=1).pack(fill=tk.X)
        tk.Label(frame1, text="Поддерживаемые форматы: PNG, JPG, JPEG",
                 font=('Arial', 7), fg='gray',
                 bg='#f0f0f0').pack(pady=2)

        # Блок 2 - Получение изображения с веб-камеры
        frame2 = tk.LabelFrame(main_frame, text="2. Веб-камера",
                               font=('Arial', 10, 'bold'), padx=10,
                               pady=5, bg='#f0f0f0')
        frame2.pack(fill=tk.X, pady=5)
        tk.Button(frame2, text="Сделать снимок",
                  command=self.capture_from_camera,
                  height=1).pack(fill=tk.X)
        tk.Label(frame2, text="ПРОБЕЛ - снимок | ESC - отмена",
                 font=('Arial', 8), fg='gray',
                 bg='#f0f0f0').pack(pady=2)

        # Блок 3 - Выбор цветового канала
        frame3 = tk.LabelFrame(main_frame, text="3. Цветовой канал",
                               font=('Arial', 10, 'bold'), padx=10,
                               pady=5, bg='#f0f0f0')
        frame3.pack(fill=tk.X, pady=5)

        self.channel_var = tk.StringVar(value="original")
        channels_frame = tk.Frame(frame3, bg='#f0f0f0')
        channels_frame.pack()

        tk.Radiobutton(channels_frame, text="Оригинал",
                       variable=self.channel_var,
                       value="original",
                       command=self.update_display,
                       bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(channels_frame, text="Красный",
                       variable=self.channel_var,
                       value="red",
                       command=self.update_display,
                       bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(channels_frame, text="Зеленый",
                       variable=self.channel_var,
                       value="green",
                       command=self.update_display,
                       bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(channels_frame, text="Синий",
                       variable=self.channel_var,
                       value="blue",
                       command=self.update_display,
                       bg='#f0f0f0').pack(side=tk.LEFT, padx=5)

        # Блок 4 - Изменение размера изображения
        frame4 = tk.LabelFrame(main_frame, text="4. Изменение размера",
                               font=('Arial', 10, 'bold'), padx=10,
                               pady=5, bg='#f0f0f0')
        frame4.pack(fill=tk.X, pady=5)

        size_row = tk.Frame(frame4, bg='#f0f0f0')
        size_row.pack()

        tk.Label(size_row, text="Ширина:",
                 bg='#f0f0f0').pack(side=tk.LEFT, padx=2)
        self.resize_w = tk.Entry(size_row, width=8)
        self.resize_w.pack(side=tk.LEFT, padx=5)

        tk.Label(size_row, text="Высота:",
                 bg='#f0f0f0').pack(side=tk.LEFT, padx=2)
        self.resize_h = tk.Entry(size_row, width=8)
        self.resize_h.pack(side=tk.LEFT, padx=5)

        tk.Button(size_row, text="Применить",
                  command=self.resize_image).pack(side=tk.LEFT, padx=10)

        # Блок 5 - Понижение яркости изображения
        frame5 = tk.LabelFrame(main_frame, text="5. Понижение яркости",
                               font=('Arial', 10, 'bold'), padx=10,
                               pady=5, bg='#f0f0f0')
        frame5.pack(fill=tk.X, pady=5)

        bright_row = tk.Frame(frame5, bg='#f0f0f0')
        bright_row.pack()

        tk.Label(bright_row, text="Значение (0-255):",
                 bg='#f0f0f0').pack(side=tk.LEFT, padx=2)
        self.bright_val = tk.Entry(bright_row, width=8)
        self.bright_val.pack(side=tk.LEFT, padx=5)
        tk.Button(bright_row, text="Понизить",
                  command=self.lower_brightness).pack(side=tk.LEFT, padx=10)

        # Блок 6 - Рисование синего прямоугольника
        frame6 = tk.LabelFrame(main_frame,
                               text="6. Синий прямоугольник (залитый)",
                               font=('Arial', 10, 'bold'), padx=10,
                               pady=5, bg='#f0f0f0')
        frame6.pack(fill=tk.X, pady=5)

        tk.Label(frame6, text="Левый верхний угол → Правый нижний угол",
                 font=('Arial', 9, 'italic'), fg='#333',
                 bg='#f0f0f0').pack(pady=2)

        top_row = tk.Frame(frame6, bg='#f0f0f0')
        top_row.pack(pady=2)

        tk.Label(top_row, text="X1 (отступ слева):",
                 bg='#f0f0f0', width=15, anchor='w').pack(side=tk.LEFT)
        self.rect_x1 = tk.Entry(top_row, width=8)
        self.rect_x1.pack(side=tk.LEFT, padx=2)

        tk.Label(top_row, text="Y1 (отступ сверху):",
                 bg='#f0f0f0', width=15, anchor='w').pack(side=tk.LEFT, padx=10)
        self.rect_y1 = tk.Entry(top_row, width=8)
        self.rect_y1.pack(side=tk.LEFT, padx=2)

        bottom_row = tk.Frame(frame6, bg='#f0f0f0')
        bottom_row.pack(pady=2)

        tk.Label(bottom_row, text="X2 (отступ слева):",
                 bg='#f0f0f0', width=15, anchor='w').pack(side=tk.LEFT)
        self.rect_x2 = tk.Entry(bottom_row, width=8)
        self.rect_x2.pack(side=tk.LEFT, padx=2)

        tk.Label(bottom_row, text="Y2 (отступ сверху):",
                 bg='#f0f0f0', width=15, anchor='w').pack(side=tk.LEFT, padx=10)
        self.rect_y2 = tk.Entry(bottom_row, width=8)
        self.rect_y2.pack(side=tk.LEFT, padx=2)

        tk.Button(frame6, text="Нарисовать прямоугольник",
                  command=self.draw_rectangle).pack(pady=5)

        tk.Label(frame6, text="Пример: X1=50, Y1=50, X2=250, Y2=200",
                 font=('Arial', 7), fg='gray',
                 bg='#f0f0f0').pack()

        # Кнопка возврата к исходному изображению
        self.reset_btn = tk.Button(main_frame,
                                   text="Вернуть исходное изображение",
                                   command=self.reset_image, bg='#ffcccc',
                                   height=1)
        self.reset_btn.pack(fill=tk.X, pady=10)

        # Список блоков, которые скрыты до загрузки изображения
        self.operations_frames = [frame3,
                                  frame4,
                                  frame5,
                                  frame6,
                                  self.reset_btn]
        for f in self.operations_frames:
            f.pack_forget()

    def show_operations(self):
        """
        Отображает блоки управления после загрузки изображения.
        """
        for f in self.operations_frames:
            f.pack(fill=tk.X, pady=5)

    def load_image(self):
        """
        Загружает изображение с устройства через диалоговое окно.
        Поддерживаемые форматы: PNG, JPG, JPEG.
        """
        # Открытие диалогового окна выбора файла
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )

        # Если файл не выбран, выход
        if not file_path:
            return

        # Проверка расширения файла
        if not file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            messagebox.showerror("Ошибка",
                                 "Поддерживаются форматы: PNG и JPG")
            return

        try:
            # Загрузка и конвертация изображения в RGB
            pil_image = Image.open(file_path)
            pil_image = pil_image.convert('RGB')
            self.original_image = np.array(pil_image)
            self.current_image = self.original_image.copy()
            self.rectangle_coords = None

            # Отображение блоков управления
            self.show_operations()
            self.update_display()
            self.status.config(
                text=f"Загружено: {os.path.basename(file_path)}"
            )

        except Exception as e:
            # Обработка ошибок загрузки
            messagebox.showerror(
                "Ошибка",
                f"Не удалось загрузить изображение:\n{str(e)}"
            )
            self.status.config(text="Ошибка загрузки")

    def capture_from_camera(self):
        """
        Захват изображения с веб-камеры.
        ПРОБЕЛ - сделать снимок, ESC - отмена.
        """
        camera = None
        try:
            # Попытка подключиться к камере
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                camera = cv2.VideoCapture(1)
            if not camera.isOpened():
                raise Exception("Камера не найдена")

            self.status.config(text="ПРОБЕЛ - снимок | ESC - отмена")

            # Цикл захвата кадров
            while True:
                ret, frame = camera.read()
                if not ret:
                    break

                cv2.imshow("Camera - SPACE to capture, ESC to cancel",
                                frame)
                key = cv2.waitKey(1) & 0xFF

                # ESC - отмена
                if key == 27:
                    break
                # ПРОБЕЛ - снимок
                elif key == 32:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.original_image = frame_rgb
                    self.current_image = self.original_image.copy()
                    self.rectangle_coords = None

                    # Создание папки для снимков, если её нет
                    if not os.path.exists("captures"):
                        os.makedirs("captures")
                    filename = (
                        f"captures/capture_"
                        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    )
                    cv2.imwrite(filename, frame)

                    self.show_operations()
                    self.update_display()
                    self.status.config(text=f"Снимок сохранен: {filename}")
                    break

            camera.release()
            cv2.destroyAllWindows()

        except Exception as e:
            # Обработка ошибок камеры
            msg = (
                f"Ошибка камеры:\n{str(e)}\n\nРешения:\n"
                "1. Проверьте подключение камеры\n"
                "2. Закройте другие программы (Zoom, Skype)\n"
                "3. Перезагрузите компьютер"
            )

            messagebox.showerror("Ошибка", msg)
            self.status.config(text="Ошибка камеры")

            if camera:
                camera.release()
            cv2.destroyAllWindows()

    def update_display(self):
        """
        Обновляет отображение изображения на холсте.
        Учитывает выбранный цветовой канал и наличие прямоугольника.
        """
        if self.current_image is None:
            return

        channel = self.channel_var.get()

        # Выбор цветового канала для отображения
        if channel == "original":
            display = self.current_image.copy()
        elif channel == "red":
            display = np.zeros_like(self.current_image)
            display[:, :, 0] = self.current_image[:, :, 0]
        elif channel == "green":
            display = np.zeros_like(self.current_image)
            display[:, :, 1] = self.current_image[:, :, 1]
        elif channel == "blue":
            display = np.zeros_like(self.current_image)
            display[:, :, 2] = self.current_image[:, :, 2]
        else:
            return

        # Наложение прямоугольника, если он задан
        if self.rectangle_coords is not None:
            x1, y1, x2, y2 = self.rectangle_coords
            display_bgr = cv2.cvtColor(display.astype('uint8'),
                                       cv2.COLOR_RGB2BGR)
            cv2.rectangle(display_bgr, (x1, y1), (x2, y2),
                          (255, 0, 0), -1)
            display = cv2.cvtColor(display_bgr, cv2.COLOR_BGR2RGB)

        # Масштабирование изображения под размер холста
        pil_img = Image.fromarray(display.astype('uint8'))

        canvas_w = self.canvas_img.winfo_width()
        canvas_h = self.canvas_img.winfo_height()

        if canvas_w <= 1 or canvas_h <= 1:
            canvas_w = 800
            canvas_h = 600

        img_w, img_h = pil_img.size
        scale = min(canvas_w / img_w, canvas_h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)

        if new_w > 0 and new_h > 0:
            pil_img = pil_img.resize((new_w, new_h),
                                     Image.Resampling.LANCZOS)

        # Отображение изображения на холсте
        self.tk_image = ImageTk.PhotoImage(pil_img)

        self.canvas_img.delete("all")
        x = (canvas_w - self.tk_image.width()) // 2
        y = (canvas_h - self.tk_image.height()) // 2
        self.canvas_img.create_image(x, y, anchor=tk.NW,
                                     image=self.tk_image)

    def resize_image(self):
        """
        Изменяет размер текущего изображения.
        Диапазон допустимых значений: 1-5000 пикселей.
        """
        if self.current_image is None:
            messagebox.showwarning("Ошибка",
                                   "Нет изображения")
            return
        try:
            w = int(self.resize_w.get())
            h = int(self.resize_h.get())
            if w > 0 and h > 0 and w <= 5000 and h <= 5000:
                self.current_image = cv2.resize(self.current_image, (w, h))
                self.rectangle_coords = None
                self.update_display()
                self.status.config(text=f"Размер изменен: {w} x {h}")
            else:
                raise ValueError
        except:
            messagebox.showerror("Ошибка",
                                 "Введите корректные размеры (1-5000)")

    def lower_brightness(self):
        """
        Уменьшает яркость изображения на указанное значение.
        Диапазон допустимых значений: 0-255.
        """
        if self.current_image is None:
            messagebox.showwarning("Ошибка",
                                   "Нет изображения")
            return
        try:
            val = int(self.bright_val.get())
            if 0 <= val <= 255:
                self.current_image = cv2.subtract(self.current_image, val)
                self.rectangle_coords = None
                self.update_display()
                self.status.config(text=f"Яркость понижена на {val}")
            else:
                raise ValueError
        except:
            messagebox.showerror("Ошибка",
                                 "Введите число от 0 до 255")

    def draw_rectangle(self):
        """
        Рисует залитый синий прямоугольник на изображении.
        Координаты: X1, Y1 - левый верхний угол, X2, Y2 - правый нижний.
        """
        if self.current_image is None:
            messagebox.showwarning("Ошибка",
                                   "Нет изображения")
            return

        try:
            x1 = int(self.rect_x1.get())
            y1 = int(self.rect_y1.get())
            x2 = int(self.rect_x2.get())
            y2 = int(self.rect_y2.get())

            # Проверка корректности координат
            if x1 >= x2 or y1 >= y2:
                messagebox.showerror(
                    "Ошибка",
                    "X2 должен быть больше X1, а Y2 больше Y1"
                )
                return

            h, w = self.current_image.shape[:2]

            # Проверка, что координаты не выходят за границы
            if x1 < 0 or y1 < 0 or x2 > w or y2 > h:
                messagebox.showerror(
                    "Ошибка",
                    f"Координаты выходят за границы "
                    f"(ширина={w}, высота={h})"
                )
                return

            # Сохранение координат и обновление отображения
            self.rectangle_coords = (x1, y1, x2, y2)
            self.update_display()
            self.status.config(
                text=f"Прямоугольник: ({x1},{y1}) → ({x2},{y2}), "
                     f"размер: {x2 - x1}×{y2 - y1}"
            )

        except ValueError:
            messagebox.showerror("Ошибка",
                                 "Введите целые числа")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def reset_image(self):
        """
        Возвращает изображение к исходному состоянию.
        Очищает все изменения и поля ввода.
        """
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.rectangle_coords = None
            self.channel_var.set("original")
            self.update_display()
            self.status.config(text="Изображение возвращено к исходному")

            # Очистка полей ввода
            self.resize_w.delete(0, tk.END)
            self.resize_h.delete(0, tk.END)
            self.bright_val.delete(0, tk.END)
            self.rect_x1.delete(0, tk.END)
            self.rect_y1.delete(0, tk.END)
            self.rect_x2.delete(0, tk.END)
            self.rect_y2.delete(0, tk.END)
        else:
            messagebox.showwarning("Ошибка",
                                   "Нет изображения")


def main():
    """
    Точка входа в приложение.
    Создаёт главное окно и запускает цикл обработки событий Tkinter.
    """
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()