# Техническое руководство: Разработка специализированного редактора сценариев DnDEditor на Python

> **Цель документа:** Пошаговое руководство по созданию GUI-приложения «DnDEditor» — специализированного текстового редактора для проекта «Подземелья Политеха». Документ описывает исследование предметной области, архитектуру, реализацию функционала и процесс документирования.

---

## 1. Исследование предметной области

### Ключевые вопросы исследования

1. **Какие компоненты обязательны для редактора сценариев настольных ролевых игр?**
   - Графическое окно с поддержкой кастомизации интерфейса
   - Многострочное текстовое поле с прокруткой и подсветкой синтаксиса
   - Система тегов для разметки игровых элементов ([БОЙ], [ПРОВЕРКА:], [ЛУТ] и др.)
   - Панель быстрых кнопок для вставки часто используемых тегов
   - Библиотека шаблонов для типовых сцен (локации, NPC, боевые сцены)
   - Инструменты анализа: счётчики элементов, генератор бросков кубиков
   - Экспорт в форматы .md, .txt, .html с сохранением разметки

2. **Почему выбран tkinter?**
   - Встроен в стандартную библиотеку Python — не требует установки внешних зависимостей
   - Кроссплатформенность: приложение работает на Windows, macOS, Linux
   - Поддержка тегов для текстового виджета Text позволяет реализовать подсветку синтаксиса без сторонних библиотек
   - Простая событийная модель (command, bind) удобна для прототипирования и учебных проектов

3. **Анализ аналогов:** Изучены редакторы для мастеров (GM) в проектах с открытым исходным кодом. Выделены требования:
   - Минималистичный интерфейс, не отвлекающий от написания текста
   - Быстрый доступ к часто используемым элементам сценария
   - Возможность экспорта для совместного использования с игроками

### Сравнение подходов к реализации подсветки синтаксиса

| Метод | Сложность | Производительность | Гибкость | Подходит для проекта |
|---|---|---|---|---|
| Text.tag_configure + re | Низкая | Высокая | Средняя | Да |
| pygments + tkinter | Средняя | Средняя | Высокая | Нет (избыточно) |
| Внешний веб-движок | Высокая | Зависит от окружения | Очень высокая | Нет (нарушает принцип «без зависимостей») |

---

## 2. Подготовка окружения

### Требования

- Python 3.10 или выше
- ОС: Windows 10/11, macOS 10.15+, Linux с поддержкой Tkinter
- Git для контроля версий (рекомендуется)

### Проверка установки

```bash
python3 --version
python3 -m tkinter
git --version
```

> **Примечание:** Для Linux (Ubuntu/Mint) при отсутствии tkinter выполните: `sudo apt install python3-tk`

---

## 3. Пошаговая реализация

### Шаг 1: Создание базового класса приложения

```python
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re

class DnDEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("D&D Scenario Editor - Подземелья Политеха")
        self.root.geometry("1000x700")
        self.current_file = None
        self.is_dark_theme = True
```

### Шаг 2: Настройка системы тегов для подсветки

```python
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

self.tag_colors = {
    'combat': '#e74c3c',
    'check': '#f39c12',
    'loot': '#27ae60',
    'npc': '#9b59b6',
    'location': '#3498db',
    'event': '#e67e22',
    'dialogue': '#1abc9c',
    'secret': '#8e44ad',
}
```

### Шаг 3: Создание текстового поля и настройка тегов

```python
def _setup_tags(self):
    for tag_type in self.tag_colors:
        self.text_area.tag_configure(
            tag_type,
            foreground=self.tag_colors[tag_type],
            font=("Consolas", 12, "bold")
        )
    self.text_area.tag_configure("md_bold", font=("Consolas", 12, "bold"))
    self.text_area.tag_configure("md_asterisk", foreground="#666666")
```

### Шаг 4: Реализация функции подсветки синтаксиса

```python
def _highlight_tags(self, event=None):
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
```

### Шаг 5: Реализация системы меню и файловых операций

```python
def _create_menu(self):
    menu = tk.Menu(self.root)
    self.root.config(menu=menu)
    
    file_menu = tk.Menu(menu, tearoff=False)
    menu.add_cascade(label="Файл", menu=file_menu)
    file_menu.add_command(label="Новый сценарий", command=self.new_file, accelerator="Ctrl+N")
    file_menu.add_command(label="Открыть", command=self.open_file, accelerator="Ctrl+O")
    file_menu.add_command(label="Сохранить", command=self.save_file, accelerator="Ctrl+S")
    file_menu.add_command(label="Экспорт в HTML", command=self.export_html, accelerator="Ctrl+E")
```

### Шаг 6: Реализация экспорта в HTML

```python
def export_html(self):
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
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .combat {{ color: #e74c3c; font-weight: bold; }}
        .check {{ color: #f39c12; font-weight: bold; }}
        .loot {{ color: #27ae60; font-weight: bold; }}
    </style>
</head>
<body>
    <pre>{html_content_body}</pre>
</body>
</html>"""
    
    html_path = self.current_file.rsplit('.', 1)[0] + ".html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
```

---

## 4. Архитектура приложения

### Структура класса DnDEditor

```
DnDEditor
├── Атрибуты
│   ├── root: tk.Tk — главное окно приложения
│   ├── current_file: str — путь к текущему файлу
│   ├── text_area: tk.Text — основное текстовое поле
│   ├── dnd_tags: dict — словарь категорий тегов
│   ├── tag_colors: dict — цветовая схема для подсветки
│   └── is_dark_theme: bool — флаг текущей темы
│
├── Методы инициализации
│   ├── __init__() — настройка окна и компонентов
│   ├── _create_widgets() — создание элементов интерфейса
│   ├── _create_menu() — построение системы меню
│   ├── _setup_tags() — конфигурация тегов для подсветки
│   └── _bind_shortcuts() — привязка горячих клавиш
│
├── Методы обработки текста
│   ├── _highlight_tags() — динамическая подсветка синтаксиса
│   ├── _insert_tag() — вставка тега в позицию курсора
│   ├── _update_status() — обновление строки состояния
│   └── _apply_theme() — применение цветовой схемы
│
├── Методы работы с файлами
│   ├── new_file() — создание нового документа
│   ├── open_file() — открытие существующего файла
│   ├── save_file() — сохранение в текущий файл
│   ├── save_as() — сохранение с выбором пути
│   └── export_html() — экспорт в HTML-формат
│
└── Методы дополнительных функций
    ├── _insert_*_template() — вставка шаблонов сцен
    ├── _roll_dice() — генератор бросков кубиков
    ├── _show_stats() — отображение статистики сценария
    ├── toggle_theme() — переключение темы интерфейса
    └── _show_help() / _show_about() — справочные окна
```

### Диаграмма последовательности: Процесс сохранения файла

```
Пользователь -> DnDEditor: Нажимает Ctrl+S / Файл → Сохранить
alt current_file определён
    DnDEditor -> FileSystem: open(path, "w", encoding="utf-8")
    FileSystem --> DnDEditor: file object
    DnDEditor -> FileSystem: write(text_area.get(1.0, END))
    FileSystem --> DnDEditor: success
else current_file не определён
    DnDEditor -> Пользователь: Открыть диалог "Сохранить как"
    Пользователь -> DnDEditor: Выбрать путь и имя файла
    DnDEditor -> FileSystem: Запись + обновление current_file
end
DnDEditor -> Пользователь: Обновить заголовок окна
```

---

## 5. Документирование ключевых модификаций

### Модификация 1: Система подсветки D&D-тегов

**Задача:** Обеспечить визуальное выделение игровых элементов сценария для ускорения навигации мастера.

**Реализация:**
```python
def _highlight_tags(self, event=None):
    content = self.text_area.get("1.0", tk.END)
    
    for tag_type, tag_list in self.dnd_tags.items():
        for tag in tag_list:
            pattern = re.escape(tag)
            for match in re.finditer(pattern, content):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                self.text_area.tag_add(tag_type, start, end)
```

**Технические детали:**
- Используется модуль `re` для поиска вхождений тегов с учётом возможных спецсимволов
- Метод `tag_add` применяет заранее настроенные стили к найденным фрагментам
- Привязка к событию `<KeyRelease>` обеспечивает обновление подсветки в реальном времени
- Производительность: линейная сложность O(n) по длине текста, что приемлемо для сценариев до 100 КБ

### Модификация 2: Генератор бросков кубиков

**Задача:** Предоставить мастеру инструмент для симуляции бросков игровых кубиков без переключения между окнами.

**Реализация:**
```python
def _roll_dice(self):
    import random
    dialog = tk.Toplevel(self.root)
    dialog.title("Генератор бросков")
    
    dice_var = tk.StringVar(value="d20")
    dice_options = ["d4", "d6", "d8", "d10", "d12", "d20", "d100"]
    
    for dice in dice_options:
        tk.Radiobutton(dialog, text=dice, variable=dice_var, value=dice).pack(anchor="w")
    
    def roll():
        dice = dice_var.get()
        sides = int(dice[1:])
        result = random.randint(1, sides)
        self.text_area.insert(tk.END, f"[БРОСОК: {dice}] = {result}\n")
    
    tk.Button(dialog, text="Бросить!", command=roll).pack(pady=10)
```

**Технические детали:**
- Используется стандартный модуль `random` для генерации псевдослучайных чисел
- Диалоговое окно создаётся через `Toplevel`, не блокируя основное приложение
- Результат броска автоматически вставляется в позицию курсора с форматированием тега
- Поддерживаются все стандартные типы кубиков настольных ролевых игр

### Модификация 3: Переключение темы интерфейса

**Задача:** Обеспечить комфортную работу при разном освещении без внешних зависимостей.

**Реализация:**
```python
def _apply_theme(self):
    if self.is_dark_theme:
        bg_color = "#1e1e1e"
        fg_color = "#d4d4d4"
        text_bg = "#2d2d2d"
    else:
        bg_color = "#f0f0f0"
        fg_color = "#000000"
        text_bg = "#ffffff"
    
    self.root.config(bg=bg_color)
    self.text_area.config(bg=text_bg, fg=fg_color, insertbackground=fg_color)
    self.status_bar.config(bg="#2d2d2d" if self.is_dark_theme else "#f0f0f0", 
                           fg="#cccccc" if self.is_dark_theme else "#000000")
```

**Технические детали:**
- Все цвета хранятся в виде hex-кодов для точного контроля палитры
- Метод `_apply_theme()` применяется централизованно при инициализации и переключении
- Цвета тегов подсветки не изменяются при смене темы, обеспечивая консистентность семантической разметки

---

## 6. Тестирование и запуск

### Инструкция по запуску

```bash
git clone <repository-url>
cd dnd-editor
python3 src/main.py
```

### Чек-лист функционального тестирования

- [ ] Приложение запускается без ошибок в консоли
- [ ] Создание нового файла очищает текстовое поле и сбрасывает заголовок
- [ ] Открытие файла корректно обрабатывает UTF-8 кодировку (включая кириллицу)
- [ ] Сохранение через Ctrl+S записывает в существующий файл, Ctrl+Shift+S предлагает новый путь
- [ ] Подсветка тегов обновляется при вводе текста в реальном времени
- [ ] Экспорт в HTML сохраняет структуру и цветовую разметку
- [ ] Генератор бросков вставляет результат в позицию курсора
- [ ] Переключение темы изменяет цвета интерфейса, не затрагивая контент
- [ ] Горячие клавиши соответствуют заявленным в меню
- [ ] Приложение корректно закрывается через системное меню или Ctrl+Q

### Известные ограничения

- Отсутствие поддержки вкладок (multiple tabs) — выходит за рамки базового tkinter
- Подсветка синтаксиса работает только для заранее определённых тегов, не поддерживает вложенные конструкции
- При объёме текста свыше 1 МБ возможна заметная задержка при перерисовке подсветки
- Экспорт в HTML использует упрощённую конверсию без полноценного парсинга Markdown

---

## 7. Хронология работы и индивидуальные планы

### Этапы реализации (Февраль – Май 2026)

| Период | Задача | Результат |
|---|---|---|
| 03.02 – 20.02 | Исследование требований, настройка окружения, структура репозитория | Базовый шаблон проекта, первый коммит |
| 21.02 – 15.03 | Реализация ядра: текстовое поле, меню, файловые операции | Рабочий прототип с базовым функционалом |
| 16.03 – 10.04 | Внедрение подсветки тегов, шаблонов, генератора бросков | Версия с расширенным функционалом |
| 11.04 – 30.04 | Тестирование, отладка, написание технической документации | Стабильная версия, комплект отчётных файлов |
| 01.05 – 24.05 | Подготовка презентации, финальная сборка, сдача материалов | Готовый к защите пакет документации и кода |

### Индивидуальные планы участников

| Участник | Роль | Ключевые задачи |
|---|---|---|
| Русскова Валерия Андреевна | Ведущий разработчик | Проектирование архитектуры, реализация класса DnDEditor, разработка системы подсветки, экспорт в HTML, интеграция инструментов |
| Труфанова Анастасия Максимовна | Аналитик / Тестировщик | Сбор требований, разработка шаблонов сценариев, функциональное тестирование, подготовка отчётной документации, координация с организацией-партнёром |

---

## 8. Полезные ресурсы

1. [Официальная документация Tkinter](https://docs.python.org/3/library/tkinter.html)
2. [Effbot Tkinter Reference](https://effbot.org/tkinterbook/)
3. [Regular Expression HOWTO](https://docs.python.org/3/howto/regex.html)
4. [Markdown Guide](https://www.markdownguide.org/)
5. [Git Documentation](https://git-scm.com/doc)
6. [Python Encoding HOWTO](https://docs.python.org/3/howto/unicode.html)

---

## 9. Лицензия и контактная информация

Проект разработан в рамках учебной проектной практики. Исходный код предоставляется для ознакомления и внутреннего использования командой «Подземелья Политеха».

**Контактное лицо:** Семенова Валерия Валерьевна  
**Организация-партнёр:** Настольно-ролевое шоу «Подземелья Политеха»  
**Дата завершения практики:** 12 мая 2026 г.
```
