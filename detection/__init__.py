import os
import pickle
import threading
import unicodedata

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import tkinter as tk
from tkinter import messagebox

# Definisikan scope dan path untuk token
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
TOKEN_PATH = "token.pickle"


def log_message(widget, message):
    """Masukkan pesan ke widget log (scrolled text) dan scroll ke bawah."""
    widget.insert(tk.END, message + "\n")
    widget.see(tk.END)


def authorize(log_widget):
    """
    Authorize aplikasi dengan menggunakan OAuth 2.0.
    Token disimpan dalam file pickle agar tidak perlu otorisasi setiap kali.
    """
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token_file:
            creds = pickle.load(token_file)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            log_message(log_widget, "Merefresh token...")
            creds.refresh(Request())
        else:
            log_message(log_widget, "Memulai proses otorisasi baru. Silakan login di browser...")
            if os.path.exists("credentials.json"):
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            else:
                client_config = {
                    "installed": {
                        "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
                        "project_id": "your-project-id",
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_secret": "YOUR_CLIENT_SECRET",
                        "redirect_uris": [
                            "http://localhost:50652/"
                        ]
                    }
                }
                flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
            # Menggunakan run_local_server agar proses otorisasi melalui browser terbuka secara otomatis
            creds = flow.run_local_server(port=50652)
        with open(TOKEN_PATH, "wb") as token_file:
            pickle.dump(creds, token_file)
            log_message(log_widget, f"Token disimpan ke {TOKEN_PATH}.")
    return creds


def get_judol_comment(text):
    """
    Memeriksa apakah komentar mengandung karakter Unicode yang tidak normal.
    Jika teks yang dinormalisasi berbeda, maka dianggap sebagai spam.
    """
    normalized_text = unicodedata.normalize("NFKD", text)
    return text != normalized_text


def fetch_comments(youtube, video_id, log_widget):
    """
    Mengambil komentar dari video dengan video_id yang diberikan.
    Mengembalikan daftar ID komentar yang terdeteksi sebagai spam.
    """
    spam_comments = []
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100
        )
        response = request.execute()
        for item in response.get("items", []):
            # Ambil komentar level atas
            comment = item["snippet"]["topLevelComment"]["snippet"]
            comment_text = comment.get("textDisplay", "")
            comment_id = item.get("id", "")
            log_message(log_widget, f'Memeriksa komentar: "{comment_text}"')
            if get_judol_comment(comment_text):
                log_message(log_widget, f"🚨 Spam terdeteksi: \"{comment_text}\"")
                spam_comments.append(comment_id)
    except Exception as e:
        log_message(log_widget, "Error saat mengambil komentar: " + str(e))
    return spam_comments


def delete_comments(youtube, comment_ids, log_widget):
    """
    Menghapus komentar-komentar berdasarkan daftar comment_ids.
    """
    for comment_id in comment_ids:
        try:
            youtube.comments().delete(id=comment_id).execute()
            log_message(log_widget, f"Deleted comment: {comment_id}")
        except Exception as e:
            log_message(log_widget, f"Gagal menghapus komentar {comment_id}: {e}")


def process_comments(video_id, log_widget):
    """
    Proses lengkap: Otorisasi, ambil komentar, dan hapus komentar spam.
    Fungsi ini dijalankan dalam thread terpisah untuk menghindari freezing UI.
    """
    log_message(log_widget, "Memulai proses...")
    creds = authorize(log_widget)
    youtube = build("youtube", "v3", credentials=creds)
    spam_comments = fetch_comments(youtube, video_id, log_widget)
    if spam_comments:
        log_message(log_widget, f"Ditemukan {len(spam_comments)} komentar spam. Menghapus...")
        delete_comments(youtube, spam_comments, log_widget)
    else:
        log_message(log_widget, "Tidak ditemukan komentar spam.")
    log_message(log_widget, "Proses selesai.")


def on_start_button_click(video_entry, log_widget):
    """
    Fungsi callback saat tombol start ditekan.
    Mengambil video_id dari entry dan menjalankan proses_comments dalam thread baru.
    """
    video_id = video_entry.get().strip()
    if "=" in video_id:
        video_id = video_id.split("=")[1]
    else:
        video_id = video_id.split("/")[-1]

    if not video_id:
        messagebox.showwarning("Input Error", "Silakan masukkan YouTube Video ID terlebih dahulu.")
        return

    # Mulai proses di thread terpisah agar UI tetap responsif
    threading.Thread(target=process_comments, args=(video_id, log_widget), daemon=True).start()
