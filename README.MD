# Simple LMS Extended Backend

Backend REST API untuk **Simple Learning Management System (LMS)** yang dikembangkan sebagai Final Project Mata Kuliah **Pemrograman Sisi Server**.

## Deskripsi

Project ini merupakan pengembangan dari Simple LMS dengan menggunakan:

- Django
- Django Ninja
- PostgreSQL
- JWT Authentication
- Docker & Docker Compose

Project ini menerapkan Role-Based Access Control (RBAC) dengan tiga peran utama:

- **Admin**
- **Instructor**
- **Student**

Selain fitur dasar LMS, project ini mengimplementasikan **Paket 1 – LMS Experience**, meliputi:

- Search, Filter, dan Sorting Course
- Rating, Review, dan Wishlist
- Curriculum & Detail Progress
- Student Dashboard

---

# Tech Stack

- Python 3.x
- Django
- Django Ninja
- PostgreSQL
- Docker
- Docker Compose
- JWT Authentication

---

# Project Structure

```
.
├── code/
│   ├── manage.py
│   ├── requirements.txt
│   ├── lms/
│   ├── users/
│   ├── courses/
│   ├── enrollments/
│   └── progress/
│
├── docker-compose.yml
├── Dockerfile
├── README.md
├── .env.example
└── FINAL_PROJECT_REPORT.md
```

---

# Installation

Clone repository

```bash
git clone <repository-url>
```

Masuk ke folder project

```bash
cd <project-folder>
```

Jalankan Docker

```bash
docker compose up -d
```

---

# Database Migration

```bash
docker exec -it lms-app python manage.py migrate
```

---

# Create Superuser

```bash
docker exec -it lms-app python manage.py createsuperuser
```

---

# Run Project

Apabila menggunakan Docker Compose, project akan berjalan secara otomatis.

Akses aplikasi pada:

```
http://localhost:8000
```

Swagger API:

```
http://localhost:8000/api/docs
```

Admin Panel:

```
http://localhost:8000/admin
```

---

# Authentication

Project menggunakan **JWT Authentication**.

Endpoint Login:

```
POST /api/v1/auth/login
```

Gunakan access token pada setiap request yang membutuhkan autentikasi.

---

# 👥 Roles

## Admin

- Mengelola seluruh data
- Mengelola User
- Mengelola Course
- Approval Course

## Instructor

- Membuat Course
- Membuat Lesson
- Mengelola Curriculum
- Melihat Student Progress

## Student

- Melihat Course
- Enroll Course
- Belajar
- Memberikan Review
- Menambahkan Wishlist

---

# Implemented Features

## Core Features

- JWT Authentication
- Role Based Access Control
- Course Management
- Lesson Management
- Enrollment
- Learning Progress
- Swagger Documentation

## Additional Features (Package 1)

- Search, Filter & Sorting Course
- Rating & Review
- Wishlist
- Curriculum
- Student Dashboard

---

# 📌 Main API Endpoints

## Authentication

```
POST /api/v1/auth/login
POST /api/v1/auth/register
POST /api/v1/auth/refresh
```

## Course

```
GET /api/v1/courses
GET /api/v1/courses/{id}
POST /api/v1/courses
PUT /api/v1/courses/{id}
DELETE /api/v1/courses/{id}
```

## Enrollment

```
POST /api/v1/enrollments
GET /api/v1/enrollments
```

## Progress

```
GET /api/v1/progress
POST /api/v1/progress
```

## Review

```
POST /api/v1/reviews
GET /api/v1/reviews
```

## Wishlist

```
POST /api/v1/wishlist
GET /api/v1/wishlist
DELETE /api/v1/wishlist/{id}
```

## Dashboard

```
GET /api/v1/dashboard
```

---

# Demo Accounts

| Role       | Username   | Password      |
| ---------- | ---------- | ------------- |
| Admin      | admin      | admin123      |
| Instructor | instructor | instructor123 |
| Student    | student    | student123    |

> **Catatan:** Akun demo dapat dibuat menggunakan seed data.

---

# Docker Commands

Start container

```bash
docker compose up -d
```

Stop container

```bash
docker compose down
```

Melihat log

```bash
docker compose logs -f
```

Masuk ke container

```bash
docker exec -it lms-app bash
```

---

# Environment

Salin file environment

```bash
cp .env.example .env
```

Kemudian sesuaikan konfigurasi database apabila diperlukan.

---

# API Documentation

Swagger tersedia pada:

```
http://localhost:8000/api/docs
```

---

# License

Project ini dibuat untuk keperluan akademik sebagai Final Project Mata Kuliah Pemrograman Sisi Server Program Studi Teknik Informatika Universitas Dian Nuswantoro.
