import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pypdf import PdfReader, PdfWriter
import os
import json

LANGUAGES = {
    "en": {
        "title": "PDF Merger",
        "output_filename": "Output Filename:",
        "add_pdfs": "Add PDFs",
        "sort_name": "Sort by Name",
        "sort_time": "Restore Original Order",
        "merge_pdfs": "Merge PDFs",
        "success": "Merged PDF saved to:",
        "no_files": "Please add some PDF files first.",
        "error": "Error",
        "select_file": "Select output file",
        "language": "Language"
    },
    "tr": {
        "title": "PDF Birleştirici",
        "output_filename": "Çıktı Dosya Adı:",
        "add_pdfs": "PDF Ekle",
        "sort_name": "İsme Göre Sırala",
        "sort_time": "İlk Sıralamaya Dön",
        "merge_pdfs": "PDF'leri Birleştir",
        "success": "Birleştirilen PDF kaydedildi:",
        "no_files": "Lütfen önce PDF dosyaları ekleyin.",
        "error": "Hata",
        "select_file": "Çıktı dosyasını seç",
        "language": "Dil"
    }
}

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"lang": "en"}

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f)

class PDFMergerApp:
    def __init__(self, root):
        self.root = root
        self.settings = load_settings()
        self.lang = self.settings.get("lang", "en")
        self.text = LANGUAGES[self.lang]
        self.files = []
        self.original_files = []

        self.root.title(self.text["title"])
        self.root.geometry("600x450")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=6, font=("Segoe UI", 10))
        style.configure("TLabel", font=("Segoe UI", 10))

        self.build_ui()

    def build_ui(self):
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text=self.text["output_filename"]).pack(side=tk.LEFT, padx=(0, 5))
        self.filename_var = tk.StringVar(value="merged.pdf")
        self.filename_entry = ttk.Entry(top_frame, textvariable=self.filename_var, width=40)
        self.filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        lang_menu = ttk.Menubutton(top_frame, text=self.text["language"])
        menu = tk.Menu(lang_menu, tearoff=0)
        menu.add_command(label="English", command=lambda: self.set_language("en"))
        menu.add_command(label="Türkçe", command=lambda: self.set_language("tr"))
        lang_menu["menu"] = menu
        lang_menu.pack(side=tk.RIGHT, padx=(10, 0))

        self.listbox = tk.Listbox(self.root, selectmode=tk.SINGLE, font=("Segoe UI", 10))
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 0))

        self.listbox.bind("<Button-1>", self.on_click)
        self.listbox.bind("<B1-Motion>", self.on_drag)

        button_frame = ttk.Frame(self.root, padding=10)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text=self.text["add_pdfs"], command=self.add_files).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text=self.text["sort_name"], command=self.sort_by_name).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text=self.text["sort_time"], command=self.restore_original_order).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text=self.text["merge_pdfs"], command=self.merge_pdfs).grid(row=0, column=3, padx=5)

    def set_language(self, lang):
        self.lang = lang
        self.text = LANGUAGES[lang]
        self.settings["lang"] = lang
        save_settings(self.settings)
        self.refresh_ui()

    def refresh_ui(self):
        self.root.destroy()
        new_root = tk.Tk()
        app = PDFMergerApp(new_root)
        new_root.mainloop()

    def add_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        for path in file_paths:
            filename = os.path.basename(path)
            entry = (path, filename)
            self.files.append(entry)
            self.original_files.append(entry)
            self.listbox.insert(tk.END, filename)

    def sort_by_name(self):
        self.files.sort(key=lambda x: x[1].lower())
        self.refresh_listbox()

    def restore_original_order(self):
        self.files = self.original_files.copy()
        self.refresh_listbox()

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for _, filename in self.files:
            self.listbox.insert(tk.END, filename)

    def on_click(self, event):
        self.drag_start_index = self.listbox.nearest(event.y)

    def on_drag(self, event):
        new_index = self.listbox.nearest(event.y)
        if new_index != self.drag_start_index:
            self.files[self.drag_start_index], self.files[new_index] = self.files[new_index], self.files[self.drag_start_index]
            self.refresh_listbox()
            self.listbox.selection_set(new_index)
            self.drag_start_index = new_index

    def merge_pdfs(self):
        if not self.files:
            messagebox.showwarning(self.text["error"], self.text["no_files"])
            return

        default_filename = self.filename_var.get().strip()
        if not default_filename.endswith(".pdf"):
            default_filename += ".pdf"

        output_path = filedialog.asksaveasfilename(
            title=self.text["select_file"],
            initialfile=default_filename,
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if not output_path:
            return

        try:
            writer = PdfWriter()
            for path, _ in self.files:
                reader = PdfReader(path)
                for page in reader.pages:
                    writer.add_page(page)

            with open(output_path, "wb") as f_out:
                writer.write(f_out)

            messagebox.showinfo(self.text["title"], f"{self.text['success']}\n{output_path}")
        except Exception as e:
            messagebox.showerror(self.text["error"], str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFMergerApp(root)
    root.mainloop()
