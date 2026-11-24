"""
UAS Praktek Pemrograman Dasar
Proyek : Aplikasi Pencatat Keuangan Pribadi Mahasiswa (GUI Tkinter)
Nama   : Al Hafizh Nidhom Samudra
NIM    : 266152026

Materi yang diterapkan:
1. Struktur data  -> list, dictionary, tuple
2. Fungsi         -> tambah, ubah, hapus, hitung, simpan, muat
3. Pengkondisian  -> validasi input (if / elif / else)
4. Perulangan     -> for untuk menghitung dan menampilkan data
5. Penanganan error -> try / except (input tidak valid, file rusak)
6. File           -> penyimpanan data ke JSON
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox

FILE_DATA = "data_keuangan.json"

# Tuple: data tetap yang tidak akan berubah
JENIS = ("Pemasukan", "Pengeluaran")
KATEGORI = ("Uang Saku", "Gaji", "Makan", "Transportasi", "Belanja",
            "Pendidikan", "Hiburan", "Lainnya")


# ============================================================
# BAGIAN 1: FUNGSI LOGIKA (tanpa GUI)
# ============================================================

def format_rupiah(angka):
    """Mengubah angka menjadi format Rp 1.000.000."""
    return "Rp " + f"{angka:,.0f}".replace(",", ".")


def validasi_input(nama, jumlah_teks, jenis, kategori):
    """
    Memeriksa input pengguna.
    Mengembalikan (valid, pesan, jumlah).
    """
    nama = nama.strip()

    if nama == "":
        return False, "Nama transaksi tidak boleh kosong.", 0
    if jenis not in JENIS:
        return False, "Pilih jenis transaksi terlebih dahulu.", 0
    if kategori not in KATEGORI:
        return False, "Pilih kategori terlebih dahulu.", 0

    try:
        jumlah = float(jumlah_teks.replace(".", "").replace(",", "."))
    except ValueError:
        return False, "Jumlah harus berupa angka (contoh: 25000).", 0

    if jumlah <= 0:
        return False, "Jumlah harus lebih besar dari 0.", 0

    return True, "", jumlah


def tambah_transaksi(daftar, nama, jumlah, jenis, kategori):
    """Menambahkan satu transaksi (dictionary) ke dalam list."""
    transaksi = {
        "nama": nama.strip(),
        "jumlah": jumlah,
        "jenis": jenis,
        "kategori": kategori,
    }
    daftar.append(transaksi)


def ubah_transaksi(daftar, index, nama, jumlah, jenis, kategori):
    """Mengubah transaksi pada posisi index. Mengembalikan True jika berhasil."""
    if 0 <= index < len(daftar):
        daftar[index] = {
            "nama": nama.strip(),
            "jumlah": jumlah,
            "jenis": jenis,
            "kategori": kategori,
        }
        return True
    return False


def hapus_transaksi(daftar, index):
    """Menghapus transaksi pada posisi index. Mengembalikan True jika berhasil."""
    if 0 <= index < len(daftar):
        daftar.pop(index)
        return True
    return False


def hitung_ringkasan(daftar):
    """Menghitung total pemasukan, total pengeluaran, dan saldo."""
    total_masuk = 0
    total_keluar = 0
    for item in daftar:
        if item["jenis"] == "Pemasukan":
            total_masuk += item["jumlah"]
        else:
            total_keluar += item["jumlah"]
    return total_masuk, total_keluar, total_masuk - total_keluar


def hitung_per_kategori(daftar):
    """Menghitung total pengeluaran untuk tiap kategori (dictionary)."""
    hasil = {}
    for item in daftar:
        if item["jenis"] == "Pengeluaran":
            kat = item["kategori"]
            hasil[kat] = hasil.get(kat, 0) + item["jumlah"]
    return hasil


def analisis_keuangan(total_masuk, total_keluar):
    """Memberi saran sederhana berdasarkan perbandingan pemasukan dan pengeluaran."""
    if total_masuk == 0 and total_keluar == 0:
        return "Belum ada data transaksi."
    if total_masuk == 0:
        return "Ada pengeluaran tetapi belum ada pemasukan."

    rasio = total_keluar / total_masuk * 100
    if rasio > 100:
        return f"Boros! Pengeluaran {rasio:.0f}% dari pemasukan (defisit)."
    elif rasio > 80:
        return f"Hati-hati, pengeluaran sudah {rasio:.0f}% dari pemasukan."
    else:
        return f"Keuangan sehat. Pengeluaran {rasio:.0f}% dari pemasukan."


def simpan_data(daftar):
    """Menyimpan list transaksi ke file JSON."""
    try:
        with open(FILE_DATA, "w", encoding="utf-8") as f:
            json.dump(daftar, f, indent=2, ensure_ascii=False)
        return True
    except OSError:
        return False


def muat_data():
    """Memuat data dari file JSON. Jika tidak ada/rusak, mengembalikan list kosong."""
    try:
        with open(FILE_DATA, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# ============================================================
# BAGIAN 2: GUI (Tkinter)
# ============================================================

def buat_gui():
    """Membangun jendela aplikasi dan menghubungkannya dengan fungsi logika."""
    daftar = muat_data()

    root = tk.Tk()
    root.title("Pencatat Keuangan Pribadi")
    root.geometry("820x640")
    root.minsize(820, 640)

    var_nama = tk.StringVar()
    var_jumlah = tk.StringVar()
    var_jenis = tk.StringVar(value=JENIS[1])
    var_kategori = tk.StringVar(value=KATEGORI[2])
    var_masuk = tk.StringVar()
    var_keluar = tk.StringVar()
    var_saldo = tk.StringVar()
    var_analisis = tk.StringVar()

    # ---------- Fungsi-fungsi pembantu GUI ----------
    def refresh():
        """Memperbarui tabel, ringkasan, dan analisis."""
        for baris in tree.get_children():
            tree.delete(baris)
        for i, item in enumerate(daftar):
            tree.insert("", "end", iid=str(i), values=(
                i + 1, item["nama"], item["jenis"],
                item["kategori"], format_rupiah(item["jumlah"])))

        masuk, keluar, saldo = hitung_ringkasan(daftar)
        var_masuk.set(format_rupiah(masuk))
        var_keluar.set(format_rupiah(keluar))
        var_saldo.set(format_rupiah(saldo))
        var_analisis.set(analisis_keuangan(masuk, keluar))

    def bersihkan_form():
        var_nama.set("")
        var_jumlah.set("")
        var_jenis.set(JENIS[1])
        var_kategori.set(KATEGORI[2])
        if tree.selection():
            tree.selection_remove(tree.selection())

    def ambil_index_terpilih():
        pilihan = tree.selection()
        if not pilihan:
            return None
        return int(pilihan[0])

    def baca_form():
        """Membaca & memvalidasi form. Mengembalikan data atau None jika tidak valid."""
        valid, pesan, jumlah = validasi_input(
            var_nama.get(), var_jumlah.get(), var_jenis.get(), var_kategori.get())
        if not valid:
            messagebox.showwarning("Input Tidak Valid", pesan)
            return None
        return var_nama.get(), jumlah, var_jenis.get(), var_kategori.get()

    # ---------- Aksi tombol ----------
    def aksi_tambah():
        data = baca_form()
        if data is None:
            return
        tambah_transaksi(daftar, *data)
        simpan_data(daftar)
        bersihkan_form()
        refresh()

    def aksi_ubah():
        index = ambil_index_terpilih()
        if index is None:
            messagebox.showinfo("Info", "Pilih transaksi di tabel yang ingin diubah.")
            return
        data = baca_form()
        if data is None:
            return
        if ubah_transaksi(daftar, index, *data):
            simpan_data(daftar)
            bersihkan_form()
            refresh()

    def aksi_hapus():
        index = ambil_index_terpilih()
        if index is None:
            messagebox.showinfo("Info", "Pilih transaksi di tabel yang ingin dihapus.")
            return
        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus transaksi ini?"):
            hapus_transaksi(daftar, index)
            simpan_data(daftar)
            bersihkan_form()
            refresh()

    def aksi_rincian():
        """Menampilkan total pengeluaran per kategori."""
        per_kategori = hitung_per_kategori(daftar)
        if not per_kategori:
            messagebox.showinfo("Rincian", "Belum ada data pengeluaran.")
            return
        teks = ""
        for kat, total in per_kategori.items():
            teks += f"{kat:<14}: {format_rupiah(total)}\n"
        messagebox.showinfo("Pengeluaran per Kategori", teks)

    def saat_dipilih(_event):
        """Mengisi form dengan data baris yang diklik (untuk diubah)."""
        index = ambil_index_terpilih()
        if index is not None and index < len(daftar):
            item = daftar[index]
            var_nama.set(item["nama"])
            var_jumlah.set(str(int(item["jumlah"])) if item["jumlah"] == int(item["jumlah"])
                           else str(item["jumlah"]))
            var_jenis.set(item["jenis"])
            var_kategori.set(item["kategori"])

    # ---------- Tampilan ----------
    ttk.Label(root, text="Pencatat Keuangan Pribadi",
              font=("Segoe UI", 16, "bold")).pack(pady=(12, 4))

    # Form input
    form = ttk.LabelFrame(root, text="Data Transaksi")
    form.pack(fill="x", padx=14, pady=6)

    ttk.Label(form, text="Nama").grid(row=0, column=0, padx=8, pady=6, sticky="w")
    ttk.Entry(form, textvariable=var_nama, width=28).grid(row=0, column=1, padx=8)
    ttk.Label(form, text="Jumlah (Rp)").grid(row=0, column=2, padx=8, sticky="w")
    ttk.Entry(form, textvariable=var_jumlah, width=18).grid(row=0, column=3, padx=8)

    ttk.Label(form, text="Jenis").grid(row=1, column=0, padx=8, pady=6, sticky="w")
    ttk.Combobox(form, textvariable=var_jenis, values=JENIS,
                 state="readonly", width=25).grid(row=1, column=1, padx=8)
    ttk.Label(form, text="Kategori").grid(row=1, column=2, padx=8, sticky="w")
    ttk.Combobox(form, textvariable=var_kategori, values=KATEGORI,
                 state="readonly", width=15).grid(row=1, column=3, padx=8)

    # Tombol
    tombol = ttk.Frame(root)
    tombol.pack(pady=4)
    ttk.Button(tombol, text="Tambah", command=aksi_tambah).grid(row=0, column=0, padx=4)
    ttk.Button(tombol, text="Ubah", command=aksi_ubah).grid(row=0, column=1, padx=4)
    ttk.Button(tombol, text="Hapus", command=aksi_hapus).grid(row=0, column=2, padx=4)
    ttk.Button(tombol, text="Bersihkan Form", command=bersihkan_form).grid(row=0, column=3, padx=4)
    ttk.Button(tombol, text="Rincian Kategori", command=aksi_rincian).grid(row=0, column=4, padx=4)

    # Tabel
    kolom = ("no", "nama", "jenis", "kategori", "jumlah")
    tree = ttk.Treeview(root, columns=kolom, show="headings", height=10)
    judul = ("No", "Nama", "Jenis", "Kategori", "Jumlah")
    lebar = (40, 260, 110, 120, 140)
    for k, j, w in zip(kolom, judul, lebar):
        tree.heading(k, text=j)
        tree.column(k, width=w, anchor="center" if k in ("no", "jenis") else "w")
    tree.pack(fill="both", expand=True, padx=14, pady=6)
    tree.bind("<<TreeviewSelect>>", saat_dipilih)

    # Ringkasan
    ringkas = ttk.LabelFrame(root, text="Ringkasan")
    ringkas.pack(fill="x", padx=14, pady=6)
    ttk.Label(ringkas, text="Total Pemasukan  :").grid(row=0, column=0, sticky="w", padx=8, pady=2)
    ttk.Label(ringkas, textvariable=var_masuk).grid(row=0, column=1, sticky="w")
    ttk.Label(ringkas, text="Total Pengeluaran:").grid(row=1, column=0, sticky="w", padx=8, pady=2)
    ttk.Label(ringkas, textvariable=var_keluar).grid(row=1, column=1, sticky="w")
    ttk.Label(ringkas, text="Saldo            :",
              font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", padx=8, pady=2)
    ttk.Label(ringkas, textvariable=var_saldo,
              font=("Segoe UI", 10, "bold")).grid(row=2, column=1, sticky="w")
    ttk.Label(ringkas, textvariable=var_analisis,
              foreground="#1a5fb4").grid(row=3, column=0, columnspan=2, sticky="w", padx=8, pady=4)

    refresh()
    root.mainloop()


if __name__ == "__main__":
    buat_gui()