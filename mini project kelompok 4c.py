import csv, getpass, hashlib, math, os, sys, time
from statistics import median

KOLOM_WAJIB = ["Place_Name", "Category", "Price", "Rating", "Time_Minutes", "Latitude", "Longitude"]
ATURAN = {"Price": (0, 1e12), "Rating": (0, 5), "Time_Minutes": (1, 1440),
          "Latitude": (-90, 90), "Longitude": (-180, 180)}
RADIUS_BUMI_KM = 6371.0088
TITIK_AWAL_DEFAULT = "Nol Kilometer Jl.Malioboro"
GARIS = "=" * 68
FOLDER = os.path.dirname(os.path.abspath(__file__))
FILE_USER = os.path.join(FOLDER, "users.txt")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def judul(teks):
    lebar = max(len(GARIS), len(teks) + 6)
    print(f"\n{'=' * lebar}\n||{teks.center(lebar - 4)}||\n{'=' * lebar}")

def at(teks, delay=0.03):  # at = animasi tampil (efek mengetik)
    for char in teks:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def cetak_tabel(teks, kop, isi, delay=0.003, semua=None):
    """Tabel gaya TB_5C: bingkai '=', judul '||...||', sel rata tengah, tampil dengan animasi."""
    contoh = (semua if semua is not None else isi) + ([kop] if kop else [])
    lebar = [max(len(str(x[k])) for x in contoh) + 2 for k in range(len(contoh[0]))]
    total = sum(lebar) + len(lebar) + 1
    baris = lambda s: "|" + "|".join(str(c).center(w) for c, w in zip(s, lebar)) + "|"
    at("=" * total, delay)
    if teks:
        at("||" + teks.center(total - 4) + "||", delay)
        at("=" * total, delay)
    if kop:
        at(baris(kop), delay)
        at("|" + "|".join("-" * w for w in lebar) + "|", delay)
    for x in isi:
        at(baris(x), delay)
    at("=" * total, delay)

# ------------------------------ COVER & ANIMASI ------------------------------
class cover:
    def coveran(self):
        def b(teks=""):
            print(("||" + teks.center(100) + "||").center(150))
        print(("||" + "=" * 100 + "||").center(150))
        b("MINI PROJECT")
        b("PEMROGRAMAN KOMPUTER")
        b("Pengembangan Program Perencanaan Itinerari Wisata Harian di Daerah Istimewa Yogyakarta")
        b("Berdasarkan Anggaran, Waktu, dan Rute Terdekat Menggunakan Python")
        b(); b()
        b("Oleh:")
        b("Kelompok 4C")
        b(); b()
        b("Anggota:")
        b("Dela Firnia                (2610932026)")
        b("Haikal Yandri              (2610932022)")
        b("Khairina Ardelia Tarigan   (2610933004)")
        b("Zahwa Aqila Ramadhani      (2610933024)")
        b(); b()
        b("Asisten Pengampu:")
        b("Kurnia Rahmat Illahi")
        b()
        b("Dosen Pengampu:")
        b("Asmuliardi Muluk, S.T., M.T.")
        b(); b()
        b("LABORATORIUM SISTEM INFORMASI DAN KEPUTUSAN")
        b("DEPARTEMEN TEKNIK INDUSTRI")
        b("UNIVERSITAS ANDALAS")
        b("PADANG")
        b("2026")
        print(("||" + "=" * 100 + "||").center(150))

def animasi_pembuka():
    for i in range(30):
        clear_screen()
        print(" " * i + "Selamat Datang di Wisata Yogyakarta!!!!")
        print(" " * i + "Halooo para traveler!!!!!")
        print(" " * i + "Yukkk mulai perjalanan favorit kamuuuu")
        print(" " * i + "Let's gooo!!!")
        time.sleep(0.15)

def ke_angka(teks):
    try:
        nilai = float(str(teks).strip())
        return None if math.isnan(nilai) else nilai
    except ValueError:
        return None

def rupiah(x): return "Rp" + f"{x:,.0f}".replace(",", ".")
def format_jam(menit): return f"{(int(round(menit)) // 60) % 24:02d}:{int(round(menit)) % 60:02d}"
def potong(teks, n): return teks if len(teks) <= n else teks[:n - 1] + "…"

def harga_teks(nilai):
    v = ke_angka(nilai if nilai is not None else "")
    return "-" if v is None and not nilai else str(nilai) if v is None else "Gratis" if v == 0 else rupiah(v)

# ------------------------------ LOGIN ------------------------------
def minta_password(pesan):
    """Minta password dengan getpass; fallback ke input pada terminal tanpa dukungan getpass."""
    if not sys.stdin or not sys.stdin.isatty():
        return input(pesan)
    try:
        return getpass.getpass(pesan)
    except (EOFError, KeyboardInterrupt):
        raise
    except Exception:
        print("  Tampilan password disembunyikan tidak didukung; teks password akan terlihat.")
        return input(pesan)

def login():
    """Kembalikan nama pengguna bila berhasil; None bila gagal/dibatalkan."""
    clear_screen()
    judul("LOGIN - PERENCANA WISATA YOGYAKARTA")
    users = {}
    if os.path.exists(FILE_USER):
        with open(FILE_USER, encoding="utf-8") as f:
            users = dict(l.rstrip("\n").split("\t") for l in f if l.count("\t") == 1)
    nama = ""
    while not nama:
        nama = input("Nama: ").strip().replace("\t", " ")
    enkripsi = lambda s: hashlib.sha256((nama + s).encode()).hexdigest()
    if nama not in users:
        if input(f"'{nama}' belum terdaftar. Daftar akun baru? (y/n) [y]: ").strip().lower() == "n":
            return None
        while True:
            sandi = minta_password("Buat password (min 4 karakter): ")
            if len(sandi) >= 4 and sandi == minta_password("Ulangi password: "):
                break
            print("  Password minimal 4 karakter dan kedua isian harus sama.")
        with open(FILE_USER, "a", encoding="utf-8") as f:
            f.write(f"{nama}\t{enkripsi(sandi)}\n")
        print(f"Akun dibuat. Selamat datang, {nama}!")
        return nama
    for sisa in (2, 1, 0):
        if enkripsi(minta_password("Password: ")) == users[nama]:
            print(f"Login berhasil. Selamat datang kembali, {nama}!")
            return nama
        print(f"  Password salah. Sisa percobaan: {sisa}")
    return None

# ------------------------------ DATASET ------------------------------
def baca_csv(path):
    """Baca CSV mentah: kembalikan (daftar kolom, list baris dict)."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File dataset tidak ditemukan: {path}")
    with open(path, newline="", encoding="utf-8-sig") as f:
        pembaca = csv.DictReader(f)
        kolom = list(pembaca.fieldnames or [])
        hilang = [k for k in KOLOM_WAJIB if k not in kolom]
        if hilang:
            raise ValueError(f"Kolom wajib tidak ada di dataset: {hilang}")
        return kolom, list(pembaca)

def simpan_dataset(path, kolom, baris):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        penulis = csv.DictWriter(f, fieldnames=kolom, extrasaction="ignore", restval="")
        penulis.writeheader()
        penulis.writerows(baris)

def bersihkan(baris):
    """Validasi & bersihkan. Durasi kosong diisi median per kategori."""
    lap = {"awal": len(baris), "kosong": 0, "duplikat": 0, "tidak_valid": 0, "durasi_kosong": 0}
    tempat, nama_ada, per_kat = [], set(), {}
    for r in baris:
        nama, kat = (r["Place_Name"] or "").strip(), (r["Category"] or "").strip()
        harga, rating = ke_angka(r["Price"]), ke_angka(r["Rating"])
        lat, lon = ke_angka(r["Latitude"]), ke_angka(r["Longitude"])
        if not nama or not kat or None in (harga, rating, lat, lon):
            lap["kosong"] += 1
        elif nama in nama_ada:
            lap["duplikat"] += 1
        elif not (harga >= 0 and 0 <= rating <= 5 and -90 <= lat <= 90 and -180 <= lon <= 180):
            lap["tidak_valid"] += 1
        else:
            durasi = ke_angka(r["Time_Minutes"])
            tempat.append({"nama": nama, "kategori": kat, "harga": harga, "rating": rating,
                           "lat": lat, "lon": lon, "durasi": durasi})
            if durasi is not None:
                per_kat.setdefault(kat, []).append(durasi)
        nama_ada.add(nama)
    median_global = median([d for v in per_kat.values() for d in v] or [60])
    for t in tempat:
        if t["durasi"] is None:
            lap["durasi_kosong"] += 1
            t["durasi"] = median(per_kat[t["kategori"]]) if t["kategori"] in per_kat else median_global
    lap["akhir"] = len(tempat)
    return tempat, lap

# ------------------- MENU 1: TABEL SELURUH DATASET -------------------
def tampilkan_dataset(baris, per_hal=15):
    if not baris:
        print("\nDataset kosong.")
        return
    kop = ["No", "Nama Tempat", "Kategori", "Harga", "Rating", "Menit", "Latitude", "Longitude"]
    isi = [[str(i), potong((r["Place_Name"] or "-").strip(), 32), potong((r["Category"] or "-").strip(), 18),
            harga_teks(r["Price"]), r["Rating"] or "-", r["Time_Minutes"] or "-",
            r["Latitude"] or "-", r["Longitude"] or "-"] for i, r in enumerate(baris, 1)]
    hal, total = 0, math.ceil(len(isi) / per_hal)
    while True:
        clear_screen()
        cetak_tabel("DATASET WISATA YOGYAKARTA", kop, isi[hal * per_hal:(hal + 1) * per_hal], 0.002, semua=isi)
        print(f"Halaman {hal + 1}/{total} | total {len(isi)} data")
        p = input("[n] berikut  [p] sebelumnya  [no. halaman]  [Enter] kembali: ").strip().lower() if total > 1 else ""
        if not p:
            return
        if p == "n" and hal < total - 1:
            hal += 1
        elif p == "p" and hal > 0:
            hal -= 1
        elif p.isdigit() and 1 <= int(p) <= total:
            hal = int(p) - 1

# ----------------- MENU 2: TAMBAH / UBAH DATA -----------------
def tanya_kolom(kol, lama=""):
    while True:
        isi = input(kol + (f" [{lama}]" if lama else "") + ": ").strip() or lama
        if kol in ("Place_Name", "Category"):
            if isi:
                return isi
            print("  Tidak boleh kosong.")
        else:
            lo, hi = ATURAN[kol]
            v = ke_angka(isi)
            if v is not None and lo <= v <= hi:
                return isi
            print(f"  Masukkan angka {lo:g} sampai {hi:g} (tanpa titik ribuan).")

def isi_data(baris, data, asli=None):
    """Minta semua kolom wajib (default = nilai lama); False bila nama sudah dipakai data lain."""
    for k in KOLOM_WAJIB:
        data[k] = tanya_kolom(k, data[k] or "")
        if k == "Place_Name" and any(r is not asli and (r["Place_Name"] or "").strip().lower()
                                     == data[k].lower() for r in baris):
            print("  [!] Nama sudah dipakai data lain. Dibatalkan.")
            return False
    return True

def menu_data(path, kolom, baris, sesi):
    while True:
        judul("KELOLA DATA")
        p = input("  1. Tambah data baru\n  2. Ubah data (berdasarkan nomor tabel)\n  0. Kembali\nPilih: ").strip()
        if p == "0":
            return
        if p == "1":
            asli, data, kunci = None, dict.fromkeys(kolom, ""), "tambah"
        elif p == "2":
            tampilkan_dataset(baris)
            no = input("Nomor data yang diubah (Enter = batal): ").strip()
            if not (no.isdigit() and 1 <= int(no) <= len(baris)):
                continue
            asli = baris[int(no) - 1]
            data, kunci = dict(asli), "ubah"
        else:
            print("  Pilihan tidak valid.")
            continue
        if isi_data(baris, data, asli):
            baris.append(data) if asli is None else asli.update(data)
            sesi[kunci] += 1
            simpan_dataset(path, kolom, baris)
            print("Perubahan disimpan ke CSV.")

# ------------------------ LOGIKA ITINERARI ------------------------
def haversine(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2)
         * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 2 * RADIUS_BUMI_KM * math.asin(math.sqrt(a))

def urutkan_nearest_neighbor(titik_awal, tempat):
    """Dari titik awal, selalu pilih destinasi terdekat berikutnya.
    Tanpa titik awal (warga lokal): mulai dari destinasi berating tertinggi."""
    sisa, rute = list(tempat), []
    if titik_awal is None and sisa:
        b = max(sisa, key=lambda x: x["rating"])
        titik_awal = (b["lat"], b["lon"])
    pos = titik_awal
    while sisa:
        t = min(sisa, key=lambda x: haversine(*pos, x["lat"], x["lon"]))
        rute.append(t)
        sisa.remove(t)
        pos = (t["lat"], t["lon"])
    return rute

def evaluasi_rute(titik_awal, rute, kecepatan):
    """Kembalikan (jarak km, menit tempuh, menit kunjungan); tidak kembali ke awal."""
    if not rute:
        return 0.0, 0.0, 0
    pos, jarak = titik_awal or (rute[0]["lat"], rute[0]["lon"]), 0.0
    for t in rute:
        jarak += haversine(*pos, t["lat"], t["lon"])
        pos = (t["lat"], t["lon"])
    return jarak, jarak / kecepatan * 60, sum(t["durasi"] for t in rute)

def susun_itinerari(tempat, titik_awal, n_hari, anggaran, jam_per_hari,
                    kategori, rating_min, maks_km, kecepatan):
    """Kandidat dari rating tertinggi, dimasukkan ke hari yang masih muat (jam & jarak)
    dengan tambahan jarak terkecil. anggaran None = tidak terbatas."""
    kandidat = sorted((t for t in tempat if t["kategori"] in kategori and t["rating"] >= rating_min),
                      key=lambda t: (-t["rating"], t["harga"]))
    hari, sisa = [[] for _ in range(n_hari)], anggaran
    for t in kandidat:
        if anggaran is not None and t["harga"] > sisa:
            continue
        pilihan = None  # (tambahan_jarak, indeks_hari, rute_baru)
        for h in range(n_hari):
            baru = urutkan_nearest_neighbor(titik_awal, hari[h] + [t])
            jarak, tempuh, kunjungan = evaluasi_rute(titik_awal, baru, kecepatan)
            if kunjungan + tempuh > jam_per_hari * 60 or jarak > maks_km:
                continue
            tambahan = jarak - evaluasi_rute(titik_awal, hari[h], kecepatan)[0]
            if pilihan is None or tambahan < pilihan[0]:
                pilihan = (tambahan, h, baru)
        if pilihan:
            hari[pilihan[1]] = pilihan[2]
            if anggaran is not None:
                sisa -= t["harga"]
    return hari, sisa, len(kandidat)

def tampilkan_itinerari(hari, titik_awal, anggaran, sisa, n_kandidat, kec, mulai):
    """Cetak itinerari; kembalikan list baris untuk CSV (atau None)."""
    if not any(hari):
        print(f"\n[!] Tidak ada destinasi yang muat ({n_kandidat} kandidat sesuai kategori/rating). "
              "Coba turunkan rating minimum atau longgarkan anggaran, jam wisata, dan batas jarak.")
        return None
    baris_csv, tot = [], [0.0, 0.0, 0.0]  # biaya, durasi (menit), jarak
    kop = ["No", "Destinasi", "Kategori", "Rating", "Tiket", "Durasi", "Perjalanan", "Perkiraan"]
    for no, rute in enumerate(hari, start=1):
        print()
        if not rute:
            cetak_tabel(f"HARI {no}", None, [["(tidak ada destinasi yang dijadwalkan pada hari ini)"]], 0.005)
            continue
        pos, waktu, isi = titik_awal or (rute[0]["lat"], rute[0]["lon"]), mulai, []
        for i, t in enumerate(rute, start=1):
            jarak = haversine(*pos, t["lat"], t["lon"])
            tempuh = jarak / kec * 60
            datang, waktu = waktu + tempuh, waktu + tempuh + t["durasi"]
            jalan = ("titik mulai" if titik_awal is None and i == 1
                     else f"+{jarak:.1f} km ({int(round(tempuh))} menit)")
            isi.append([str(i), t["nama"], t["kategori"], str(t["rating"]), harga_teks(t["harga"]),
                        f"{int(t['durasi'])} menit", jalan, f"{format_jam(datang)} - {format_jam(waktu)}"])
            baris_csv.append({"Hari": no, "Urutan": i, "Destinasi": t["nama"], "Kategori": t["kategori"],
                              "Rating": t["rating"], "Tiket": int(t["harga"]),
                              "Durasi_Menit": int(t["durasi"]), "Jarak_dari_Sebelumnya_km": round(jarak, 2),
                              "Datang": format_jam(datang), "Selesai": format_jam(waktu)})
            pos = (t["lat"], t["lon"])
        cetak_tabel(f"HARI {no}", kop, isi, 0.003)
        jarak_h, tempuh_h, kunj_h = evaluasi_rute(titik_awal, rute, kec)
        biaya_h = sum(t["harga"] for t in rute)
        print(f"  Ringkasan hari {no}: {len(rute)} destinasi | tiket {rupiah(biaya_h)} | "
              f"durasi {(kunj_h + tempuh_h) / 60:.1f} jam | jarak {jarak_h:.1f} km")
        tot = [tot[0] + biaya_h, tot[1] + kunj_h + tempuh_h, tot[2] + jarak_h]
    judul("RINGKASAN TOTAL")
    print(f"Total destinasi : {sum(len(h) for h in hari)}\nTotal tiket     : {rupiah(tot[0])}")
    print("Sisa anggaran   : " + ("- (anggaran tidak diperhitungkan)" if anggaran is None else rupiah(sisa)))
    print(f"Total durasi    : {tot[1] / 60:.1f} jam\nTotal jarak     : {tot[2]:.1f} km")
    print("Catatan: biaya hanya tiket masuk; jarak garis lurus; waktu tempuh perkiraan.")
    return baris_csv

# ------------------------- INPUT PARAMETER -------------------------
def tanya_angka(pesan, default, tipe=float, minimum=None):
    while True:
        isi = input(f"{pesan} [{default}]: ").strip()
        if isi == "":
            return default
        try:
            nilai = tipe(isi.replace(".", "") if tipe is int else isi)
        except ValueError:
            print("  Masukkan angka yang valid.")
            continue
        if minimum is not None and nilai < minimum:
            print(f"  Nilai minimal {minimum}.")
            continue
        return nilai

def pilih_kategori(daftar):
    print("\nKategori tersedia:")
    for i, k in enumerate(daftar, start=1):
        print(f"  {i}. {k}")
    while True:
        isi = input("Pilih nomor kategori (pisahkan koma, Enter = semua): ").strip()
        try:
            idx = [int(x) for x in isi.split(",")] if isi else list(range(1, len(daftar) + 1))
            if all(1 <= i <= len(daftar) for i in idx):
                return [daftar[i - 1] for i in idx]
        except ValueError:
            pass
        print("  Input tidak valid.")

def cetak_tabel_destinasi(tempat, kolom=3, lebar=24):
    """Daftar destinasi dalam tabel beberapa kolom (nomor mengalir ke bawah)."""
    n = len(tempat)
    baris, ln = math.ceil(n / kolom), len(str(n))
    isi = [[f"{i + 1:>{ln}}. {potong(tempat[i]['nama'], lebar):<{lebar}}" if i < n
            else " " * (ln + lebar + 2) for i in (r + k * baris for k in range(kolom))]
           for r in range(baris)]
    cetak_tabel("DAFTAR SELURUH DESTINASI", None, isi, 0.002)

def pilih_titik_awal(tempat):
    """Kembalikan ((lat, lon), nama) dari nomor, pencarian nama, atau koordinat."""
    print("\nDaftar seluruh destinasi (Place_Name):")
    cetak_tabel_destinasi(tempat)
    print(f"\nTitik awal perjalanan:\n  Enter = {TITIK_AWAL_DEFAULT}")
    print("  Ketik nomor destinasi, sebagian nama untuk mencari,")
    print("  atau koordinat 'lat,lon' (contoh: -7.7829,110.3671)")
    hasil = lambda t: ((t["lat"], t["lon"]), t["nama"])
    while True:
        isi = input("Titik awal: ").strip() or TITIK_AWAL_DEFAULT
        if isi.isdigit():
            if 1 <= int(isi) <= len(tempat):
                return hasil(tempat[int(isi) - 1])
            print(f"  Nomor harus antara 1 dan {len(tempat)}.")
        elif "," in isi:
            try:
                lat, lon = [float(x) for x in isi.split(",")]
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return (lat, lon), f"Koordinat ({lat}, {lon})"
            except ValueError:
                pass
            print("  Format koordinat salah.")
        else:
            cocok = [t for t in tempat if isi.lower() in t["nama"].lower()]
            if len(cocok) == 1:
                return hasil(cocok[0])
            print("  Tidak ditemukan." if not cocok else
                  "  Ada beberapa: " + "; ".join(t["nama"] for t in cocok[:8]))

# ------------- MENU 3 & 4: ITINERARI LOKAL / WISATAWAN -------------
def buat_itinerari(tempat, lokal):
    """lokal=True : warga Jogja (tanpa titik awal & anggaran, fokus rating).
    lokal=False: wisatawan luar Jogja (titik awal + anggaran + rating)."""
    clear_screen()
    judul("ITINERARI WARGA LOKAL JOGJA (fokus rating, tanpa titik awal & anggaran)" if lokal
          else "ITINERARI WISATAWAN LUAR JOGJA (titik awal, anggaran & rating)")
    print("--- Parameter perjalanan (Enter = nilai default) ---")
    n_hari = tanya_angka("Jumlah hari", 2, int, 1)
    if lokal:
        titik_awal, nama_awal, anggaran = None, "otomatis (dari destinasi berating tertinggi)", None
    else:
        titik_awal, nama_awal = pilih_titik_awal(tempat)
        anggaran = tanya_angka("Anggaran tiket Rp", 200000, int, 0)
    jam_per_hari = tanya_angka("Jam wisata per hari", 8, float, 1)
    jam_mulai = tanya_angka("Jam mulai (0-23, contoh 8 atau 8.5)", 8, float, 0) * 60
    kategori = pilih_kategori(sorted({t["kategori"] for t in tempat}))
    rating_min = tanya_angka("Rating minimum (0-5)", 4.0 if lokal else 4.3, float, 0)
    maks_km = tanya_angka("Batas jarak tempuh per hari (km)", 60, float, 1)
    kecepatan = tanya_angka("Kecepatan rata-rata kendaraan (km/jam)", 30, float, 1)
    hari, sisa, n_kandidat = susun_itinerari(
        tempat, titik_awal, n_hari, anggaran, jam_per_hari, kategori, rating_min, maks_km, kecepatan)
    judul("ITINERARI WISATA YOGYAKARTA")
    print(f"Titik awal : {nama_awal} | {n_hari} hari | mulai {format_jam(jam_mulai)}, "
          f"{jam_per_hari} jam/hari | maks {maks_km} km/hari @ {kecepatan} km/jam")
    print("Anggaran   : " + ("tidak diperhitungkan (rating tertinggi)" if anggaran is None else
                             f"{rupiah(anggaran)} | rating min {rating_min}"))
    print(f"Kategori   : {', '.join(kategori)}")
    hasil = tampilkan_itinerari(hari, titik_awal, anggaran, sisa, n_kandidat, kecepatan, jam_mulai)
    if hasil and input("\nSimpan itinerari ke CSV? (y/n) [n]: ").strip().lower() == "y":
        nama_file = os.path.join(FOLDER, "itinerari_hasil.csv")
        simpan_dataset(nama_file, list(hasil[0].keys()), hasil)
        print(f"Tersimpan: {nama_file}")
    input("\nTekan ENTER untuk kembali ke menu utama...")
    return bool(hasil)

# ------------------------------- MAIN -------------------------------
def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(FOLDER, "tour.csv")
    cvr = cover()
    cvr.coveran()
    time.sleep(3)
    animasi_pembuka()
    nama = login()
    if not nama:
        print("Login gagal. Program ditutup.")
        return
    time.sleep(2)
    try:
        kolom, baris = baca_csv(path)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}")
        return
    tempat, lap = bersihkan(baris)
    at(f"\nDataset: {lap['awal']} baris -> {lap['akhir']} dipakai (dibuang {lap['kosong']} kosong, "
          f"{lap['duplikat']} duplikat, {lap['tidak_valid']} tidak valid; "
          f"{lap['durasi_kosong']} durasi diisi median)", 0.01)
    time.sleep(2)
    sesi, mulai = {"itinerari": 0, "tambah": 0, "ubah": 0}, time.time()
    while True:
        clear_screen()
        judul("MENU UTAMA - PERENCANA WISATA YOGYAKARTA")
        print("  1. Tampilkan seluruh dataset (tabel)\n  2. Tambah / ubah data\n"
              "  3. Itinerari warga lokal Jogja (fokus rating)\n"
              "  4. Itinerari wisatawan luar Jogja (titik awal, anggaran, rating)\n  5. Keluar")
        pilih = input("Pilih menu (1-5): ").strip()
        if pilih == "1":
            tampilkan_dataset(baris)
        elif pilih == "2":
            menu_data(path, kolom, baris, sesi)
            tempat, lap = bersihkan(baris)
        elif pilih in ("3", "4"):
            if not tempat:
                print("  Tidak ada data valid untuk dijadikan itinerari.")
                time.sleep(1.5)
            elif buat_itinerari(tempat, lokal=(pilih == "3")):
                sesi["itinerari"] += 1
        elif pilih == "5":
            judul("RINGKASAN AKTIVITAS SESI")
            print(f"Pengguna          : {nama}\nLama sesi         : {(time.time() - mulai) / 60:.1f} menit\n"
                  f"Itinerari dibuat  : {sesi['itinerari']}\nData ditambahkan  : {sesi['tambah']}\n"
                  f"Data diubah       : {sesi['ubah']}")
            judul("Terima kasih telah menggunakan Perencana Wisata Yogyakarta. Sampai jumpa!")
            return
        else:
            print("  Pilihan tidak valid, masukkan 1-5.")
            time.sleep(1.2)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram dihentikan pengguna.")