import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re

class DnDEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("🎲 D&D Scenario Editor - Подземелья Политеха")
        self.root.geometry("1000x700")
        self.current_file = None
        self.is_dark_theme = True
        
        self.dnd_tags = {
            'combat': ['[БОЙ]', '[COMBAT]', '[FIGHT]'],
            'check': ['[ПРОВЕРКА:', '[CHECK:', '[SAVE:'],
            'loot': ['[ЛУТ]', '[LOOT]', '[ITEM]'],
            'npc': ['[NPC]', '[НПС]', '[CHARACTER]'],
            'location': ['[ЛОКАЦИЯ]', '[LOCATION]', '[PLACE]'],
            'event': ['[СОБЫТИЕ]', '[EVENT]', '[TRIGGER]'],
            'dialogue': ['[ДИАЛОГ]', '[DIALOGUE]', '[SPEAK]'],
            'secret': ['[СЕКРЕТ]', '[SECRET]', '[HIDDEN]'],
        }
        
        # Цвета для тегов
        self.tag_colors = {
            'combat': '#e74c3c',      # Красный - бой
            'check': '#f39c12',       # Оранжевый - проверки
            'loot': '#27ae60',        # Зелёный - лут
            'npc': '#9b59b6',         # Фиолетовый - НПС
            'location': '#3498db',    # Синий - локации
            'event': '#e67e22',       # Оранжевый - события
            'dialogue': '#1abc9c',    # Бирюзовый - диалоги
            'secret': '#8e44ad',      # Тёмно-фиолетовый - секреты
        }

        self._create_widgets()
        self._create_menu()
        self._bind_shortcuts()
        self._apply_theme()

    def _create_widgets(self):
        self.toolbar = tk.Frame(self.root, height=40)
        self.toolbar.pack(side="top", fill="x")
        
        tags_buttons = [
            ("[БОЙ]", "combat"),
            ("[ПРОВЕРКА:]", "check"),
            ("[ЛУТ]", "loot"),
            ("[NPC]", "npc"),
            ("[ЛОКАЦИЯ]", "location"),
            ("[СОБЫТИЕ]", "event"),
            ("[ДИАЛОГ]", "dialogue"),
            ("[СЕКРЕТ]", "secret"),
        ]
        
        for tag_text, tag_type in tags_buttons:
            btn = tk.Button(
                self.toolbar, 
                text=tag_text,
                command=lambda t=tag_text: self._insert_tag(t),
                bg=self.tag_colors[tag_type],
                fg="white",
                relief="raised",
                cursor="hand2"
            )
            btn.pack(side="left", padx=2, pady=5)

        text_frame = tk.Frame(self.root)
        text_frame.pack(expand=True, fill="both")
        
        self.text_area = tk.Text(
            text_frame, 
            wrap="word", 
            undo=True, 
            font=("Consolas", 12),
            spacing1=5,
            spacing3=5
        )
        self.text_area.pack(side="left", expand=True, fill="both")
        
        scrollbar = tk.Scrollbar(text_frame, command=self.text_area.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=scrollbar.set)
        
        self._setup_tags()
        
        self.text_area.bind("<KeyRelease>", self._highlight_tags)
        self.text_area.bind("<ButtonRelease>", self._update_status)

        self.status_bar = tk.Label(
            self.root, 
            text="Готов к работе | Строк: 0 | Слов: 0",
            anchor="w", 
            relief="sunken", 
            bd=1
        )
        self.status_bar.pack(side="bottom", fill="x")

    def _setup_tags(self):
        """Настройка тегов для подсветки синтаксиса"""
        for tag_type in self.tag_colors:
            self.text_area.tag_configure(
                tag_type,
                foreground=self.tag_colors[tag_type],
                font=("Consolas", 12, "bold")
            )
        

        self.text_area.tag_configure("md_bold", font=("Consolas", 12, "bold"))
        self.text_area.tag_configure("md_asterisk", foreground="#666666")

    def _insert_tag(self, tag):
        """Вставка тега в позицию курсора"""
        self.text_area.insert(tk.INSERT, tag + " ")
        self.text_area.focus()
        self._highlight_tags()

    def _highlight_tags(self, event=None):
        """Подсветка D&D тегов и Markdown в тексте"""
        content = self.text_area.get("1.0", tk.END)
        

        for tag_type in self.tag_colors:
            self.text_area.tag_remove(tag_type, "1.0", tk.END)
        self.text_area.tag_remove("md_bold", "1.0", tk.END)
        self.text_area.tag_remove("md_asterisk", "1.0", tk.END)
        
        for tag_type, tag_list in self.dnd_tags.items():
            for tag in tag_list:
                pattern = re.escape(tag)
                for match in re.finditer(pattern, content):
                    start = f"1.0 + {match.start()} chars"
                    end = f"1.0 + {match.end()} chars"
                    self.text_area.tag_add(tag_type, start, end)


        md_pattern = r'(\*\*)(.*?)(\*\*)'
        for match in re.finditer(md_pattern, content):
            asterisk_start = f"1.0 + {match.start(1)} chars"
            asterisk_end = f"1.0 + {match.end(1)} chars"
            self.text_area.tag_add("md_asterisk", asterisk_start, asterisk_end)
            
            asterisk2_start = f"1.0 + {match.start(3)} chars"
            asterisk2_end = f"1.0 + {match.end(3)} chars"
            self.text_area.tag_add("md_asterisk", asterisk2_start, asterisk2_end)

            bold_start = f"1.0 + {match.start(2)} chars"
            bold_end = f"1.0 + {match.end(2)} chars"
            self.text_area.tag_add("md_bold", bold_start, bold_end)
        
        self._update_status()

    def _update_status(self, event=None):
        """Обновление строки состояния"""
        content = self.text_area.get("1.0", tk.END)
        lines = content.count('\n')
        words = len(content.split())
        
        combat_count = sum(content.count(tag) for tag in self.dnd_tags['combat'])
        check_count = sum(content.count(tag) for tag in self.dnd_tags['check'])
        loot_count = sum(content.count(tag) for tag in self.dnd_tags['loot'])
        
        self.status_bar.config(
            text=f"🎲 D&D Editor | Строк: {lines} | Слов: {words} | "
                 f"Бои: {combat_count} | Проверки: {check_count} | Лут: {loot_count}"
        )

    def _create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новый сценарий", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Открыть", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить как...", command=self.save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Экспорт в HTML", command=self.export_html, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit, accelerator="Ctrl+Q")

        template_menu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label="Шаблоны", menu=template_menu)
        template_menu.add_command(label="Новая локация", command=self._insert_location_template)
        template_menu.add_command(label="NPC", command=self._insert_npc_template)
        template_menu.add_command(label="Боевая сцена", command=self._insert_combat_template)
        template_menu.add_command(label="Сокровище", command=self._insert_loot_template)
        template_menu.add_command(label="Диалог", command=self._insert_dialogue_template)

        tools_menu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label="Инструменты", menu=tools_menu)
        tools_menu.add_command(label="Генератор бросков", command=self._roll_dice, accelerator="Ctrl+D")
        tools_menu.add_command(label="Статистика сценария", command=self._show_stats)
        tools_menu.add_separator()
        tools_menu.add_command(label="Тёмная/Светлая тема", command=self.toggle_theme, accelerator="Ctrl+T")

        help_menu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="Справка по тегам", command=self._show_help)
        help_menu.add_command(label="О программе", command=self._show_about)

    def _insert_location_template(self):
        template = """[ЛОКАЦИЯ] Название локации
**Тип:** [Таверна/Подземелье/Лес/Город]
**Описание:**
[Подробное описание локации]

**Особенности:**
- 
- 

[СОБЫТИЕ] Триггер события:

[ЛУТ] Возможная добыча:

[СЕКРЕТ] Скрытые детали:
"""
        self.text_area.insert(tk.END, template)
        self._highlight_tags()

    def _insert_npc_template(self):
        template = """[NPC] Имя персонажа
**Раса/Класс:** 
**Характер:** 
**Внешность:** 

[ДИАЛОГ] Важные фразы:
- 

[ПРОВЕРКА:Харизма] Сложность убеждения: 15

[СОБЫТИЕ] Что даёт игрокам:
"""
        self.text_area.insert(tk.END, template)
        self._highlight_tags()

    def _insert_combat_template(self):
        template = """[БОЙ] Название сражения
**Противники:**
- 

**Инициатива:**
1. 
2. 

**Тактика:**

[ПРОВЕРКА:Интеллект] Знание о противнике: DC 12

[ЛУТ] Награда за победу:
"""
        self.text_area.insert(tk.END, template)
        self._highlight_tags()

    def _insert_loot_template(self):
        template = """[ЛУТ] Название предмета
**Тип:** [Оружие/Броня/Зелье/Артефакт]
**Редкость:** [Обычный/Необычный/Редкий/Эпический/Легендарный]

**Описание:**

**Эффект:**

[ПРОВЕРКА:Интеллект] Идентификация: DC 10

[СЕКРЕТ] Особые свойства:
"""
        self.text_area.insert(tk.END, template)
        self._highlight_tags()

    def _insert_dialogue_template(self):
        template = """[ДИАЛОГ] С кем:
**Контекст:**

**Реплики:**
- Игрок: 
- NPC: 

[ПРОВЕРКА:Харизма] Убеждение/Запугивание: 

[СОБЫТИЕ] Результат диалога:
"""
        self.text_area.insert(tk.END, template)
        self._highlight_tags()

    def _roll_dice(self):
        """Простой генератор бросков кубиков"""
        import random
        
        dialog = tk.Toplevel(self.root)
        dialog.title("🎲 Генератор бросков")
        dialog.geometry("300x200")
        
        tk.Label(dialog, text="Тип кубика:").pack(pady=5)
        
        dice_var = tk.StringVar(value="d20")
        dice_options = ["d4", "d6", "d8", "d10", "d12", "d20", "d100"]
        
        for dice in dice_options:
            tk.Radiobutton(dialog, text=dice, variable=dice_var, value=dice).pack(anchor="w")
        
        def roll():
            dice = dice_var.get()
            sides = int(dice[1:])
            result = random.randint(1, sides)
            result_label.config(text=f"🎲 Результат: {result} {dice}")
            
            # Вставить в текст
            self.text_area.insert(tk.END, f"[БРОСОК: {dice}] = {result}\n")
        
        tk.Button(dialog, text="Бросить!", command=roll, bg="#27ae60", fg="white").pack(pady=10)
        
        result_label = tk.Label(dialog, text="", font=("Arial", 14, "bold"))
        result_label.pack()

    def _show_stats(self):
        """Показать статистику сценария"""
        content = self.text_area.get("1.0", tk.END)
        
        stats = {
            "Локаций": sum(content.count(tag) for tag in self.dnd_tags['location']),
            "NPC": sum(content.count(tag) for tag in self.dnd_tags['npc']),
            "Боёв": sum(content.count(tag) for tag in self.dnd_tags['combat']),
            "Проверок": sum(content.count(tag) for tag in self.dnd_tags['check']),
            "Лута": sum(content.count(tag) for tag in self.dnd_tags['loot']),
            "Событий": sum(content.count(tag) for tag in self.dnd_tags['event']),
            "Диалогов": sum(content.count(tag) for tag in self.dnd_tags['dialogue']),
            "Секретов": sum(content.count(tag) for tag in self.dnd_tags['secret']),
        }
        
        dialog = tk.Toplevel(self.root)
        dialog.title("📊 Статистика сценария")
        dialog.geometry("300x250")
        
        for key, value in stats.items():
            tk.Label(dialog, text=f"{key}: {value}", font=("Arial", 11)).pack(anchor="w", padx=10, pady=2)

    def _show_help(self):
        help_text = """
        Доступные теги для подсветки:
        
        [БОЙ] / [COMBAT] - Сцены сражений
        [ПРОВЕРКА:] / [CHECK:] - Проверки характеристик
        [ЛУТ] / [LOOT] - Предметы и награды
        [NPC] / [НПС] - Персонажи
        [ЛОКАЦИЯ] / [LOCATION] - Места
        [СОБЫТИЕ] / [EVENT] - Триггеры
        [ДИАЛОГ] / [DIALOGUE] - Разговоры
        [СЕКРЕТ] / [SECRET] - Скрытая информация
        
        Markdown: **текст** станет жирным автоматически.
        
        Горячие клавиши:
        Ctrl+N - Новый сценарий
        Ctrl+O - Открыть
        Ctrl+S - Сохранить
        Ctrl+E - Экспорт в HTML
        Ctrl+D - Бросок кубика
        Ctrl+T - Смена темы
        """
        
        messagebox.showinfo("📖 Справка по тегам", help_text)

    def _show_about(self):
        messagebox.showinfo(
            "О программе",
            "🎲 D&D Scenario Editor\n\n"
            "Специализированный редактор для проекта\n"
            "«Подземелья Политеха»\n\n"
            "Версия 1.0 | 2026"
        )

    def _apply_theme(self):
        """Применение текущей темы"""
        if self.is_dark_theme:
            bg_color = "#1e1e1e"
            fg_color = "#d4d4d4"
            text_bg = "#2d2d2d"
            asterisk_color = "#666666"
        else:
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            text_bg = "#ffffff"
            asterisk_color = "#999999"
        
        self.root.config(bg=bg_color)
        self.text_area.config(bg=text_bg, fg=fg_color, insertbackground=fg_color)
        self.status_bar.config(bg="#2d2d2d" if self.is_dark_theme else "#f0f0f0", 
                               fg="#cccccc" if self.is_dark_theme else "#000000")
        self.toolbar.config(bg=bg_color)
        
        # Обновляем цвет звёздочек под тему
        self.text_area.tag_configure("md_asterisk", foreground=asterisk_color)

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self._apply_theme()
        self._highlight_tags()

    def _bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-Shift-S>", lambda e: self.save_as())
        self.root.bind("<Control-e>", lambda e: self.export_html())
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        self.root.bind("<Control-d>", lambda e: self._roll_dice())
        self.root.bind("<Control-t>", lambda e: self.toggle_theme())

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.root.title("🎲 D&D Scenario Editor - Подземелья Политеха")
        self._highlight_tags()

    def open_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, f.read())
                self.current_file = file_path
                self.root.title(f"🎲 D&D Editor - {os.path.basename(file_path)}")
                self._highlight_tags()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(self.text_area.get(1.0, tk.END))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")
        else:
            self.save_as()

    def save_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.text_area.get(1.0, tk.END))
                self.root.title(f" D&D Editor - {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def export_html(self):
        """Экспорт сценария в HTML формат"""
        if not self.current_file:
            messagebox.showwarning("Предупреждение", "Сначала сохраните файл!")
            return
        
        content = self.text_area.get("1.0", tk.END)
        

        import re
        html_content_body = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
        
        html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>D&D Сценарий - {os.path.basename(self.current_file)}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
        .combat {{ color: #e74c3c; font-weight: bold; }}
        .check {{ color: #f39c12; font-weight: bold; }}
        .loot {{ color: #27ae60; font-weight: bold; }}
        .npc {{ color: #9b59b6; font-weight: bold; }}
        .location {{ color: #3498db; font-weight: bold; }}
        .event {{ color: #e67e22; font-weight: bold; }}
        .dialogue {{ color: #1abc9c; font-weight: bold; }}
        .secret {{ color: #8e44ad; font-weight: bold; }}
        h1, h2, h3 {{ border-bottom: 2px solid #3498db; }}
        pre {{ white-space: pre-wrap; }}
    </style>
</head>
<body>
    <h1>🎲 D&D Сценарий</h1>
    <p><em>Проект «Подземелья Политеха»</em></p>
    <hr>
    <pre>{html_content_body}</pre>
</body>
</html>"""
        
        html_path = self.current_file.rsplit('.', 1)[0] + ".html"
        try:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            messagebox.showinfo("Успех", f"HTML экспортирован:\n{html_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать HTML:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DnDEditor(root)
    root.mainloop()