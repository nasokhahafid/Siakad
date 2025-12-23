# SIAKAD - Integrated SIPA & E-Learning System

SIAKAD HUB Modern adalah platform sistem informasi akademik terintegrasi yang menggabungkan fungsi administrasi akademik (KRS, KHS, Penjadwalan) dengan platform pembelajaran digital (E-Learning) yang responsif dan modern.

## 🌟 Fitur Utama

- **Portal Mahasiswa**: Manajemen KRS, Kartu Hasil Studi (KHS), Transkrip Nilai, Jadwal Kuliah Real-time, dan Profil Akademik.
- **E-Learning**: Akses materi (PDF/PPT), video pembelajaran, progres belajar, dan forum diskusi per mata kuliah.
- **Portal Dosen**: Manajemen konten mata kuliah, penilaian tugas mahasiswa, dan pemantauan aktivitas akademik.
- **Portal Admin**: Manajemen user (Mahasiswa/Dosen), pengelolaan mata kuliah global, dan konfigurasi sistem.
- **Layanan Mandiri**: Pengajuan surat keterangan akademik, pendaftaran magang (MBKM), dan pengajuan judul skripsi secara online.

## 🚀 Teknologi yang Digunakan

- **Backend**: Python Flask
- **Database**: MySQL (MariaDB)
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login & Bcrypt
- **Frontend**: Tailwind CSS / Vanilla CSS (Modern Interface)
- **PDF Engine**: ReportLab (Export KHS/Transkrip)

## 🛠️ Cara Penggunaan

1. **Instalasi Dependensi**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Database**:

   - Buat database bernama `siakad` di MySQL.
   - Import file `instance/create_siakad_database.sql` ke dalam database tersebut.

3. **Menjalankan Aplikasi**:
   ```bash
   python run.py
   ```
   Akses di: `http://localhost:5000`

## 🔑 Akun Pengujian (Demo)

Gunakan akun berikut untuk menguji fitur berdasarkan level akses user:

| Role              | Username (NIM) | Password   | Nama             |
| :---------------- | :------------- | :--------- | :--------------- |
| **Administrator** | `admin`        | `password` | Administrator    |
| **Dosen**         | `dosen1`       | `password` | Dr. Budi Santoso |
| **Mahasiswa**     | `mahasiswa1`   | `password` | Ahmad Fauzi      |

---

Developed with ❤️ for Academic Excellence.
