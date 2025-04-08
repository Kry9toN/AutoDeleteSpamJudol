import tkinter as tk
from tkinter import scrolledtext

from detection import on_start_button_click


class UISpam:
    def __init__(self):
        self.root = tk.Tk()

    def init_ui(self):
        self.root.title("YouTube Spam Comment Manager")

        # Frame untuk input video ID
        input_frame = tk.Frame(self.root, padx=10, pady=10)
        input_frame.pack(fill="x")

        tk.Label(input_frame, text="Link YouTube Video :").pack(side="left")
        video_entry = tk.Entry(input_frame, width=50)
        video_entry.pack(side="left", padx=(5, 10))

        start_button = tk.Button(input_frame, text="Scan & Hapus Komentar Spam",
                                 command=lambda: on_start_button_click(video_entry, log_text))
        start_button.pack(side="left")

        # Widget untuk log output
        log_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=80, height=20)
        log_text.pack(padx=10, pady=10, fill="both", expand=True)

        log_text.insert(tk.END, "Aplikasi ini butuh login akun google anda agar bisa mengakses dan menghapus komentar yang terdeteksi" + "\n")
        log_text.insert(tk.END, "Penasaran/curiga apps nya, cari codenya di sini https://github.com/Kry9toN/AutoDeleteSpamJudol" + "\n")
        log_text.insert(tk.END, "Created by: @Github Kry9toN" + "\n")
        log_text.insert(tk.END, "=" * 64 + "\n")
        log_text.see(tk.END)

        # Mulai loop utama UI
        self.root.mainloop()
