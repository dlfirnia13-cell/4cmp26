import csv
import math
import os
import sys
from statistics import median

KOLOM_WAJIB = ["Place_Name", "Category", "Price", "Rating", "Time_Minutes", "Latitude", "Longitude"]
RADIUS_BUMI_KM = 6371.0088
TITIK_AWAL_DEFAULT = "Nol Kilometer Jl.Malioboro"
GARIS = "=" * 68

def ke_angka(teks):
    try:
        nilai = float(str(teks).strip())
    except ValueError:
        return None
    return None if math.isnan(nilai) else nilai

def baca_dataset(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File dataset tidak ditemukan: {path}")
    with open(path, newline="", encoding="utf-8-sig") as f:
        pembaca = csv.DictReader(f)
        hilang = [k for k in KOLOM_WAJIB if k not in (pembaca.fieldnames or [])]
        if hilang:
            raise ValueError(f"Kolom wajib tidak ada di dataset: {hilang}")
        baris = list(pembaca)
        
    lap = {"awal": len(baris), "kosong": 0, "duplikat": 0, "tidak_valid": 0,
          "durasi_kosong": 0}
    tempat, nama_ada = [], set()
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
            tempat.append({"nama": nama, "kategori": kat, "harga": harga,
                            "rating": rating, "lat": lat, "lon": lon,
                            "durasi": ke_angka(r["Time_Minutes"])})
        nama_ada.add(nama)

    per_kat = {}
    for t in tempat:
        if t["durasi"] is not None:
            per_kat.setdefault(t["kategori"], []).append(t["durasi"])
    semua = [d for v in per_kat.values() for d in v]
    median_global = median(semua) if semua else 60
    for t in tempat:
        if t["durasi"] is None:
            lap["durasi_kosong"] += 1
            t["durasi"] = median(per_kat[t["kategori"]]) if t["kategori"] in per_kat else median_global
    lap["akhir"] = len(tempat)
    return tempat, lap
    
def haversine(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2)
         * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 2 * RADIUS_BUMI_KM * math.asin(math.sqrt(a))

def urutkan_nearest_neighbor(titik_awal, tempat):
    sisa, rute, pos = list(tempat), [], titik_awal
    while sisa:
        t = min(sisa, key=lambda x: haversine(*pos, x["lat"], x["lon"]))
        rute.append(t)
        sisa.remove(t)
        pos = (t["lat"], t["lon"])
    return rute

def evaluasi_rute(titik_awal, rute, kecepatan):
    """Kembalikan (jarak km, menit tempuh, menit kunjungan); tidak kembali ke awal."""
    pos, jarak = titik_awal, 0.0
    for t in rute:
        jarak += haversine(*pos, t["lat"], t["lon"])
        pos = (t["lat"], t["lon"])
    return jarak, jarak / kecepatan * 60, sum(t["durasi"] for t in rute)

def susun_itinerari(tempat, titik_awal, n_hari, anggaran, jam_per_hari,
                    kategori, rating_min, maks_km, kecepatan):
    kandidat = sorted((t for t in tempat
                       if t["kategori"] in kategori and t["rating"] >= rating_min),
                      key=lambda t: (-t["rating"], t["harga"]))
    hari = [[] for _ in range(n_hari)]
    sisa = anggaran
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

def rupiah(x):
    return "Rp" + f"{x:,.0f}".replace(",", ".")

def format_jam(menit):
    menit = int(round(menit))
    return f"{(menit // 60) % 24:02d}:{menit % 60:02d}"

def tampilkan_itinerari(hari, titik_awal, anggaran, sisa, n_kandidat, kec, mulai):
    """Cetak itinerari; kembalikan list baris untuk CSV (atau None)."""
    if not any(hari):
        print(f"\n[!] Tidak ada destinasi yang muat ({n_kandidat} kandidat sesuai kategori/rating). "
              "Coba naikkan anggaran, jam wisata, atau batas jarak.")
        return None

    baris_csv, tot_biaya, tot_durasi, tot_jarak = [], 0.0, 0.0, 0.0
    for no, rute in enumerate(hari, start=1):
        print(f"\n{'-' * 68}\nHARI {no}\n{'-' * 68}")
        if not rute:
            print("  (tidak ada destinasi yang dijadwalkan pada hari ini)")
            continue
        pos, waktu = titik_awal, mulai
        for i, t in enumerate(rute, start=1):
            jarak = haversine(*pos, t["lat"], t["lon"])
            tempuh = jarak / kec * 60
            datang = waktu + tempuh
            waktu = datang + t["durasi"]
            harga = "Gratis" if t["harga"] == 0 else rupiah(t["harga"])
            print(f"  {i}. {t['nama']} [{t['kategori']}]")
            print(f"     Rating {t['rating']} | Tiket {harga} | "
                  f"Durasi {int(t['durasi'])} menit | "
                  f"+{jarak:.1f} km ({int(round(tempuh))} menit perjalanan)")
            print(f"     Perkiraan {format_jam(datang)} - {format_jam(waktu)}")
            baris_csv.append({
                "Hari": no, "Urutan": i, "Destinasi": t["nama"],
                "Kategori": t["kategori"], "Rating": t["rating"],
                "Tiket": int(t["harga"]), "Durasi_Menit": int(t["durasi"]),
                "Jarak_dari_Sebelumnya_km": round(jarak, 2),
                "Datang": format_jam(datang), "Selesai": format_jam(waktu)})
            pos = (t["lat"], t["lon"])
        jarak_h, tempuh_h, kunj_h = evaluasi_rute(titik_awal, rute, kec)
        biaya_h = sum(t["harga"] for t in rute)
        print(f"  Ringkasan hari {no}: {len(rute)} destinasi | tiket {rupiah(biaya_h)} | "
              f"durasi {(kunj_h + tempuh_h) / 60:.1f} jam | jarak {jarak_h:.1f} km")
        tot_biaya += biaya_h
        tot_durasi += kunj_h + tempuh_h
        tot_jarak += jarak_h

    print(f"\n{GARIS}\nRINGKASAN TOTAL\n{GARIS}")
    print(f"Total destinasi : {sum(len(h) for h in hari)}")
    print(f"Total tiket     : {rupiah(tot_biaya)}")
    print("Sisa anggaran   : " + ("- (anggaran tidak terbatas)" if anggaran is None
                                  else rupiah(sisa)))
    print(f"Total durasi    : {tot_durasi / 60:.1f} jam")
    print(f"Total jarak     : {tot_jarak:.1f} km")
    print("Catatan: biaya hanya tiket masuk; jarak garis lurus; waktu tempuh perkiraan.")
    return baris_csv

def simpan_csv(baris, nama_file):
    with open(nama_file, "w", newline="", encoding="utf-8-sig") as f:
        penulis = csv.DictWriter(f, fieldnames=list(baris[0].keys()))
        penulis.writeheader()
        penulis.writerows(baris)

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

def tanya_anggaran():
    while True:
        isi = input("Anggaran tiket Rp (Enter = tidak terbatas): ").strip().replace(".", "")
        if isi == "":
            return None
        if isi.isdigit():
            return int(isi)
        print("  Masukkan angka, contoh 200000.")

def pilih_kategori(daftar):
    print("\nKategori tersedia:")
    for i, k in enumerate(daftar, start=1):
        print(f"  {i}. {k}")
    while True:
        isi = input("Pilih nomor kategori (pisahkan koma, Enter = semua): ").strip()
        if isi == "":
            return list(daftar)
        try:
            idx = [int(x) for x in isi.split(",")]
            if all(1 <= i <= len(daftar) for i in idx):
                return [daftar[i - 1] for i in idx]
        except ValueError:
            pass
        print("  Input tidak valid.")

