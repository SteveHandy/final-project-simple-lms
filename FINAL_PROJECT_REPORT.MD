# Simple LMS Extended Backend

Backend REST API untuk **Simple Learning Management System (LMS)** yang dikembangkan sebagai Final Project Mata Kuliah **Pemrograman Sisi Server**.

Project ini merupakan pengembangan dari Simple LMS berbasis Django dengan tambahan autentikasi JWT, Role-Based Access Control, REST API, serta fitur LMS Experience.

---

## Deskripsi Project

Simple LMS Extended Backend adalah sistem backend LMS yang memiliki fitur utama:

- Authentication menggunakan JWT
- Role-Based Access Control
- Manajemen Course
- Manajemen Lesson / Course Content
- Enrollment Student
- Learning Progress
- Rating dan Review Course
- Wishlist Course
- Curriculum dan Progress Detail
- Student Dashboard
- Swagger API Documentation

Role yang digunakan:

- **Admin**
- **Instructor**
- **Student**

---

## Tech Stack

- Python 3.12
- Django
- Django Ninja
- PostgreSQL
- Docker
- Docker Compose
- JWT Authentication
- Pillow
- Psycopg2

---

## Project Structure

```text
.
├── code/
│   ├── manage.py
│   ├── requirements.txt
│   ├── api.py
│   ├── lms/
│   ├── users/
│   ├── courses/
│   ├── progress/
│   └── dashboard/
│
├── docker-compose.yml
├── Dockerfile
├── README.md
└── FINAL_PROJECT_REPORT.md
```

---

## Cara Menjalankan Project

### 1. Clone Repository

```bash
git clone https://github.com/SteveHandy/final-project-simple-lms.git
cd final-project-simple-lms
```

---

### 2. Build dan Jalankan Docker

```bash
docker compose up --build -d
```

Cek container:

```bash
docker ps
```

Pastikan container berikut berjalan:

```text
lms-app
lms-db
```

---

### 3. Jalankan Migration

```bash
docker exec -it lms-app python manage.py migrate
```

---

### 4. Buat Superuser

```bash
docker exec -it lms-app python manage.py createsuperuser
```

---

### 5. Generate JWT Key

Project ini menggunakan JWT berbasis key. Jika file berikut belum ada di folder `code/`:

```text
jwt-signing.pem
jwt-signing.pub
```

generate dengan perintah berikut:

```bash
docker exec -it lms-app bash
openssl genrsa -out jwt-signing.pem 2048
openssl rsa -in jwt-signing.pem -pubout -out jwt-signing.pub
exit
```

---

### 6. Akses Aplikasi

Django App:

```text
http://localhost:8000
```

Swagger API Documentation:

```text
http://localhost:8000/api/docs
```

Django Admin:

```text
http://localhost:8000/admin/
```

Student Dashboard Page:

```text
http://localhost:8000/dashboard/student/
```

Login page untuk dashboard:

```text
http://localhost:8000/accounts/login/
```

---

## Akun Demo

Akun demo berikut digunakan untuk pengujian role.

| Role       | Username   | Password      |
| ---------- | ---------- | ------------- |
| Admin      | admin      | admin123      |
| Instructor | instructor | instruktur123 |
| Student    | student    | murid123      |

Jika akun belum tersedia, buat melalui Django Admin atau Django shell.

Contoh membuat akun demo melalui shell:

```bash
docker exec -it lms-app python manage.py shell
```

Lalu jalankan:

```python
from django.contrib.auth.models import User
from users.models import UserProfile

accounts = [
    ("admin", "admin123", UserProfile.Role.ADMIN, True, True),
    ("instructor", "instruktur123", UserProfile.Role.INSTRUCTOR, True, False),
    ("student", "murid123", UserProfile.Role.STUDENT, False, False),
]

for username, password, role, is_staff, is_superuser in accounts:
    user, created = User.objects.get_or_create(username=username)
    user.set_password(password)
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.save()

    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.role = role
    profile.save()

print("Akun demo berhasil dibuat.")
```

---

## Authentication

Project menggunakan JWT Authentication.

Login dilakukan melalui endpoint:

```text
POST /api/auth/sign-in
```

Setelah login berhasil, gunakan `access token` pada request yang membutuhkan autentikasi.

Format header:

```text
Authorization: Bearer <access_token>
```

---

## Role dan Hak Akses

### Admin

- Mengelola seluruh data
- Mengelola user
- Mengelola course
- Mengelola enrollment
- Mengakses seluruh data progress

### Instructor

- Membuat course
- Mengubah course miliknya
- Membuat lesson
- Mengelola curriculum
- Melihat student progress pada course yang diajar

### Student

- Melihat daftar course
- Enroll course
- Mengakses lesson
- Menandai lesson selesai
- Memberikan rating dan review
- Menambahkan course ke wishlist
- Melihat student dashboard

---

## Main API Endpoints

Base URL API:

```text
http://localhost:8000/api
```

Swagger:

```text
http://localhost:8000/api/docs
```

---

## Authentication Endpoints

```text
POST /api/auth/sign-in
POST /api/auth/refresh
POST /api/auth/verify
```

---

## User Endpoints

```text
GET /api/users/me
PUT /api/users/me
```

---

## Course Endpoints

```text
GET    /api/courses/
GET    /api/courses/{course_id}
POST   /api/courses/
PUT    /api/courses/{course_id}
DELETE /api/courses/{course_id}
```

---

## Search, Filter, dan Sorting Course

Endpoint:

```text
GET /api/courses/
```

Contoh query:

```text
GET /api/courses/?search=python
GET /api/courses/?category=1
GET /api/courses/?instructor=1
GET /api/courses/?level=beginner
GET /api/courses/?status=published
GET /api/courses/?min_price=50000&max_price=200000
GET /api/courses/?sort=price_low
GET /api/courses/?search=django&level=beginner&sort=newest
```

Sorting yang tersedia:

```text
newest
oldest
price_low
price_high
name_asc
name_desc
updated
```

---

## Lesson / Course Content Endpoints

```text
GET    /api/courses/{course_id}/lessons
GET    /api/courses/lesson/{lesson_id}
POST   /api/courses/lesson
PUT    /api/courses/lesson/{lesson_id}
DELETE /api/courses/lesson/{lesson_id}
```

---

## Curriculum Endpoint

```text
GET /api/courses/{course_id}/curriculum
```

Endpoint ini menampilkan daftar lesson atau course content lengkap dengan status progress student.

---

## Enrollment Endpoints

```text
GET    /api/courses/{course_id}/members
POST   /api/courses/{course_id}/enroll
DELETE /api/courses/{course_id}/members/{user_id}
```

Contoh body enroll:

```json
{
  "user_id": 3,
  "roles": "std"
}
```

Role enrollment:

```text
std = Student
ast = Assistant
```

---

## Progress Endpoints

```text
GET    /api/progress/
GET    /api/progress/course/{course_id}/summary
GET    /api/progress/course/{course_id}/detail
POST   /api/progress/lesson/{lesson_id}/complete
DELETE /api/progress/lesson/{lesson_id}
```

Keterangan:

- `summary` menampilkan ringkasan progress course.
- `detail` menampilkan daftar lesson beserta status selesai atau belum.
- `complete` digunakan untuk menandai lesson sebagai selesai.
- `DELETE` digunakan untuk reset progress lesson.

---

## Rating dan Review Endpoints

```text
GET    /api/courses/{course_id}/reviews
POST   /api/courses/{course_id}/reviews
PUT    /api/courses/{course_id}/reviews/me
DELETE /api/courses/{course_id}/reviews/me
GET    /api/courses/{course_id}/rating
```

Contoh body review:

```json
{
  "rating": 5,
  "review": "Materinya jelas dan mudah dipahami."
}
```

Rating memiliki nilai minimal `1` dan maksimal `5`.

---

## Wishlist Endpoints

```text
GET    /api/courses/wishlist/me
POST   /api/courses/{course_id}/wishlist
DELETE /api/courses/{course_id}/wishlist
```

---

## Student Dashboard

Halaman dashboard student:

```text
GET /dashboard/student/
```

Halaman ini menampilkan:

- jumlah course yang diikuti
- total lesson
- lesson yang sudah selesai
- rata-rata progress
- daftar course student
- recent completed lesson
- wishlist
- jumlah review yang dibuat

Login dashboard menggunakan session Django melalui:

```text
GET /accounts/login/
```

---

## Student Dashboard API

Jika menggunakan API dashboard:

```text
GET /api/dashboard/student
GET /api/dashboard/student/courses
GET /api/dashboard/student/wishlist
```

---

## Admin Panel

Admin panel dapat diakses melalui:

```text
http://localhost:8000/admin/
```

Admin dapat digunakan untuk mengelola:

- User
- User Profile
- Category
- Course
- Course Member
- Course Content
- Course Review
- Course Wishlist
- Progress

---

## Docker Commands

Menjalankan container:

```bash
docker compose up -d
```

Build ulang container:

```bash
docker compose up --build -d
```

Menghentikan container:

```bash
docker compose down
```

Melihat log:

```bash
docker compose logs -f
```

Masuk ke container Django:

```bash
docker exec -it lms-app bash
```

Menjalankan migration:

```bash
docker exec -it lms-app python manage.py migrate
```

Membuat superuser:

```bash
docker exec -it lms-app python manage.py createsuperuser
```

---

## Testing API

Testing dapat dilakukan melalui Swagger:

```text
http://localhost:8000/api/docs
```

Urutan pengujian yang disarankan:

1. Login melalui `/api/auth/sign-in`
2. Copy access token
3. Klik tombol Authorize di Swagger
4. Jalankan endpoint Course
5. Enroll student ke course
6. Tambahkan lesson pada course
7. Tandai lesson selesai melalui endpoint Progress
8. Tambahkan review dan wishlist
9. Cek Student Dashboard

---

## Implemented Features

### Core Features

- Docker Compose
- PostgreSQL Database
- Django Migration
- JWT Authentication
- Role-Based Access Control
- Course API
- Lesson API
- Enrollment API
- Progress API
- Swagger Documentation

### Additional Features - LMS Experience

- Search, Filter, dan Sorting Course
- Rating, Review, dan Wishlist Course
- Curriculum dan Progress Belajar Detail
- Student Dashboard

---

## License

Project ini dibuat untuk keperluan akademik sebagai Final Project Mata Kuliah Pemrograman Sisi Server Program Studi Teknik Informatika Universitas Dian Nuswantoro.
