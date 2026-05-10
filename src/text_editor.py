import tkinter as tk
from tkinter import filedialog, messagebox
import os

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Python Text Editor")
        self.root.geometry("800x600")
        self.current_file = None
        self.is_dark_theme = False

        # Текстовое поле
        self.text_area = tk.Text(self.root, wrap="word", undo=True, font=("Consolas", 12))
        self.text_area.pack(expand=True, fill="both")

        # Строка состояния (Модификация 1)
        self.status_bar = tk.Label(self.root, text="Ln: 1 | Col: 1 | Words: 0", 
                                   anchor="w", relief="sunken", bd=1)
        self.status_bar.pack(side="bottom", fill="x")

        self._create_menu()
        self._bind_shortcuts()
        self._bind_status_update()

    def _create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")

        edit_menu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Toggle Theme (Dark/Light)", command=self.toggle_theme, accelerator="Ctrl+T")

    def _bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-Shift-S>", lambda e: self.save_as())
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        self.root.bind("<Control-t>", lambda e: self.toggle_theme())

    def _bind_status_update(self):
        self.text_area.bind("<KeyRelease>", self.update_status)
        self.text_area.bind("<ButtonRelease>", self.update_status)

    def update_status(self, event=None):
        row, col = self.text_area.index(tk.INSERT).split('.')
        content = self.text_area.get("1.0", tk.END)
        words = len(content.split())
        self.status_bar.config(text=f"Ln: {row} | Col: {col} | Words: {words}")

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.root.title("Simple Python Text Editor")
        self.update_status()

    def open_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, f.read())
                self.current_file = file_path
                self.root.title(f"Simple Python Text Editor - {os.path.basename(file_path)}")
                self.update_status()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(self.text_area.get(1.0, tk.END))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")
        else:
            self.save_as()

    def save_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.text_area.get(1.0, tk.END))
                self.root.title(f"Simple Python Text Editor - {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def toggle_theme(self):
        """Модификация 2: Переключение светлой/тёмной темы"""
        self.is_dark_theme = not self.is_dark_theme
        if self.is_dark_theme:
            self.text_area.config(bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4")
            self.status_bar.config(bg="#2d2d2d", fg="#cccccc")
            self.root.config(bg="#1e1e1e")
        else:
            self.text_area.config(bg="#ffffff", fg="#000000", insertbackground="#000000")
            self.status_bar.config(bg="#f0f0f0", fg="#000000")
            self.root.config(bg="#ffffff")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditor(root)
    root.mainloop()
