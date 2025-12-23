-- Create the siakad database
CREATE DATABASE siakad;

-- Use the siakad database
USE siakad;

-- Example table creation (adjust as needed)
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nim VARCHAR(20) NOT NULL UNIQUE,
    nama VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(60) NOT NULL,
    program_studi VARCHAR(50) NOT NULL,
    role VARCHAR(20) DEFAULT 'mahasiswa',
    advisor_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (advisor_id) REFERENCES user(id)
);

CREATE TABLE course (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode VARCHAR(20) NOT NULL UNIQUE,
    nama VARCHAR(100) NOT NULL,
    sks INT NOT NULL,
    semester INT NOT NULL,
    dosen_id INT NOT NULL,
    FOREIGN KEY (dosen_id) REFERENCES user(id)
);

CREATE TABLE grade (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    nilai FLOAT NOT NULL,
    bobot FLOAT NOT NULL,
    grade VARCHAR(2) NOT NULL,
    semester INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES user(id),
    FOREIGN KEY (course_id) REFERENCES course(id)
);

CREATE TABLE krs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    semester INT NOT NULL,
    tahun_ajaran VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    approved_by INT,
    approved_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES user(id),
    FOREIGN KEY (course_id) REFERENCES course(id),
    FOREIGN KEY (approved_by) REFERENCES user(id)
);

CREATE TABLE material (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    judul VARCHAR(200) NOT NULL,
    deskripsi TEXT,
    file_path VARCHAR(500),
    tipe VARCHAR(20),
    minggu INT,
    uploaded_by INT NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES course(id),
    FOREIGN KEY (uploaded_by) REFERENCES user(id)
);

CREATE TABLE video (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    judul VARCHAR(200) NOT NULL,
    deskripsi TEXT,
    video_path VARCHAR(500),
    durasi INT,
    minggu INT,
    uploaded_by INT NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES course(id),
    FOREIGN KEY (uploaded_by) REFERENCES user(id)
);

CREATE TABLE video_watch (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    video_id INT NOT NULL,
    watch_time INT DEFAULT 0,
    total_duration INT DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    last_watched DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES user(id),
    FOREIGN KEY (video_id) REFERENCES video(id)
);

CREATE TABLE forum_post (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    student_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    tags VARCHAR(500),
    replies_count INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES course(id),
    FOREIGN KEY (student_id) REFERENCES user(id)
);

CREATE TABLE forum_reply (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    student_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES forum_post(id),
    FOREIGN KEY (student_id) REFERENCES user(id)
);

CREATE TABLE letter_submission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    letter_type VARCHAR(50) NOT NULL,  -- 'certificate', 'transcript', 'leave', 'recommendation', etc.
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_by INT,
    approved_at DATETIME,
    file_path VARCHAR(500),
    notes TEXT,
    FOREIGN KEY (student_id) REFERENCES user(id),
    FOREIGN KEY (approved_by) REFERENCES user(id)
);

CREATE TABLE submission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    judul VARCHAR(200) NOT NULL,
    deskripsi TEXT,
    file_path VARCHAR(500),
    nilai FLOAT,
    komentar TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    deadline DATETIME,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES user(id),
    FOREIGN KEY (course_id) REFERENCES course(id)
);

CREATE TABLE schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    hari VARCHAR(10) NOT NULL,
    waktu_mulai VARCHAR(5) NOT NULL,
    waktu_selesai VARCHAR(5) NOT NULL,
    ruangan VARCHAR(50) NOT NULL,
    semester INT NOT NULL,
    tahun_ajaran VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES course(id)
);

-- Insert sample data for testing
INSERT INTO user (nim, nama, email, password, program_studi, role, advisor_id) VALUES
('admin', 'Administrator', 'admin@amikom.ac.id', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8lLxQcK6m', 'Sistem Informasi', 'admin', NULL),
('dosen1', 'Dr. Budi Santoso', 'budi@amikom.ac.id', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8lLxQcK6m', 'Teknik Informatika', 'dosen', NULL),
('mahasiswa1', 'Ahmad Fauzi', 'ahmad@student.amikom.ac.id', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8lLxQcK6m', 'Teknik Informatika', 'mahasiswa', 2);

INSERT INTO course (kode, nama, sks, semester, dosen_id) VALUES
('IF101', 'Pemrograman Dasar', 3, 1, 2),
('IF102', 'Basis Data', 4, 2, 2),
('IF201', 'Pemrograman Web', 3, 3, 2),
('IF202', 'Jaringan Komputer', 3, 4, 2);

INSERT INTO grade (student_id, course_id, nilai, bobot, grade, semester) VALUES
(3, 1, 85, 3, 'A', 1),
(3, 2, 78, 4, 'B+', 2),
(3, 3, 92, 3, 'A-', 3);

INSERT INTO schedule (course_id, hari, waktu_mulai, waktu_selesai, ruangan, semester, tahun_ajaran) VALUES
(3, 'Senin', '08:00', '10:00', 'Lab Komputer 1', 1, '2023/2024'),
(2, 'Senin', '10:00', '12:00', 'Kelas 201', 1, '2023/2024'),
(4, 'Selasa', '08:00', '10:00', 'Lab Jaringan', 1, '2023/2024'),
(1, 'Rabu', '13:00', '15:00', 'Kelas 301', 1, '2023/2024'),
(1, 'Kamis', '08:00', '10:00', 'Lab Komputer 2', 1, '2023/2024'),
(2, 'Jumat', '10:00', '12:00', 'Kelas 101', 1, '2023/2024');

INSERT INTO material (course_id, judul, deskripsi, file_path, tipe, minggu, uploaded_by) VALUES
(1, 'Materi Pengenalan Pemrograman', 'Materi dasar tentang konsep pemrograman', 'uploads/pemrograman_dasar_week1.pdf', 'pdf', 1, 2),
(1, 'Algoritma dan Flowchart', 'Panduan membuat algoritma dan flowchart', 'uploads/algoritma_flowchart.pptx', 'pptx', 2, 2),
(2, 'Konsep Database Relasional', 'Penjelasan tentang database relasional', 'uploads/database_relasional.pdf', 'pdf', 1, 2),
(2, 'SQL Dasar', 'Tutorial bahasa SQL untuk pemula', 'uploads/sql_dasar.docx', 'docx', 2, 2),
(3, 'HTML dan CSS Dasar', 'Materi pengenalan HTML dan CSS', 'uploads/html_css_basics.pdf', 'pdf', 1, 2),
(3, 'JavaScript Fundamentals', 'Dasar-dasar pemrograman JavaScript', 'uploads/javascript_fundamentals.pptx', 'pptx', 2, 2);

INSERT INTO video (course_id, judul, deskripsi, video_path, durasi, minggu, uploaded_by) VALUES
(1, 'Instalasi Python', 'Tutorial instalasi Python dan IDE', 'videos/python_installation.mp4', 15, 1, 2),
(1, 'Hello World Program', 'Membuat program pertama dengan Python', 'videos/hello_world.mp4', 20, 1, 2),
(2, 'Desain Database dengan ERD', 'Cara membuat Entity Relationship Diagram', 'videos/erd_design.mp4', 25, 1, 2),
(2, 'Query SQL Lengkap', 'Tutorial lengkap query SQL', 'videos/sql_queries.mp4', 30, 2, 2),
(3, 'Membuat Website Pertama', 'Tutorial membuat website sederhana', 'videos/first_website.mp4', 35, 1, 2),
(3, 'Responsive Design', 'Teknik membuat website responsive', 'videos/responsive_design.mp4', 28, 2, 2);

INSERT INTO video_watch (student_id, video_id, watch_time, total_duration, completed) VALUES
(3, 1, 15, 15, TRUE),
(3, 2, 18, 20, FALSE),
(3, 3, 25, 25, TRUE),
(3, 4, 20, 30, FALSE);

INSERT INTO forum_post (course_id, author_id, title, content, tags, replies_count) VALUES
(1, 3, 'Pertanyaan tentang variabel di Python', 'Saya bingung dengan konsep variabel di Python. Apa perbedaannya dengan Java?', 'python,variabel', 2),
(2, 3, 'Normalisasi database - bentuk 3NF', 'Apakah ada yang bisa jelaskan konsep normalisasi bentuk 3?', 'database,normalisasi', 1),
(3, 3, 'Routing di React', 'Bagaimana cara implementasi routing di React Router?', 'react,routing', 0);

INSERT INTO forum_reply (post_id, author_id, content) VALUES
(1, 2, 'Variabel di Python lebih fleksibel dibanding Java karena tidak perlu deklarasi tipe data eksplisit.'),
(1, 3, 'Terima kasih atas penjelasannya! Sekarang saya lebih paham.'),
(2, 2, '3NF adalah bentuk normalisasi yang menghilangkan transitive dependency dalam tabel.');

INSERT INTO letter_submission (student_id, letter_type, title, description, status, approved_by, notes) VALUES
(3, 'certificate', 'Pengajuan Surat Keterangan Mahasiswa Aktif', 'Diperlukan untuk keperluan administrasi bank', 'approved', 1, 'Surat telah disiapkan dan dapat diambil di bagian akademik'),
(3, 'transcript', 'Pengajuan Transkrip Nilai', 'Untuk keperluan melamar kerja', 'pending', NULL, NULL),
(3, 'leave', 'Pengajuan Izin Tidak Masuk Kuliah', 'Sakit demam tinggi selama 3 hari', 'approved', 2, 'Izin diterima, tugas dapat dikumpulkan setelah sembuh');

INSERT INTO submission (student_id, course_id, judul, deskripsi, file_path, status, nilai, komentar, deadline) VALUES
(3, 1, 'Tugas Algoritma Pemrograman', 'Implementasi algoritma sorting bubble sort', 'uploads/tugas1_ahmad.pdf', 'graded', 85, 'Bagus, namun perlu diperbaiki struktur kode', '2024-01-15 23:59:59'),
(3, 2, 'Tugas Desain Database', 'Desain ERD untuk sistem perpustakaan', 'uploads/tugas2_ahmad.docx', 'submitted', NULL, NULL, '2024-01-20 23:59:59'),
(3, 3, 'Tugas Website Sederhana', 'Membuat halaman login dengan HTML, CSS, dan JavaScript', 'uploads/tugas3_ahmad.zip', 'pending', NULL, NULL, '2024-01-25 23:59:59');

CREATE TABLE internship_application (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    perusahaan VARCHAR(200) NOT NULL,
    posisi VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT NOT NULL,
    file_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'pending',
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES user(id)
);

CREATE TABLE thesis_application (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    judul_skripsi VARCHAR(500) NOT NULL,
    peminatan VARCHAR(100) NOT NULL,
    abstrak TEXT NOT NULL,
    dosen_pref VARCHAR(200),
    file_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'pending',
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES user(id)
);

CREATE TABLE system_setting (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `setting_key` VARCHAR(50) NOT NULL UNIQUE,
    setting_value VARCHAR(255) NOT NULL,
    description VARCHAR(255)
);

INSERT INTO system_setting (setting_key, setting_value, description) VALUES
('system_name', 'SIAKAD', 'Full name of the academic system'),
('max_file_size', '10', 'Maximum file upload size in MB'),
('backup_frequency', 'daily', 'Database backup frequency'),
('active_semester', 'Ganjil 2023/2024', 'Current active academic semester');
