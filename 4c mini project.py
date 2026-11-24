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

