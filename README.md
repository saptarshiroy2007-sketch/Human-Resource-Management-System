# 🧑‍💼 Human Resource Management System (HRMS)

> **Every workday, perfectly aligned.**

A full-featured Human Resource Management System that digitizes and streamlines core HR operations — employee onboarding, profile management, attendance tracking, leave management, payroll visibility, and role-based approval workflows.


Sample email: employee@example.com
Password: secret123
---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [User Roles](#user-roles)
- [Tech Stack](#tech-stack)
- [Database Schema](#database-schema)
- [Getting Started](#getting-started)
- [Database Setup](#database-setup)
- [Project Structure](#project-structure)
- [Design Reference](#design-reference)
- [Team](#team)
- [License](#license)

---

## 🎯 Overview

The HRMS aims to replace manual, paper-based HR processes with a secure, centralized digital platform. It provides employees with self-service access to their profiles, attendance, and leave requests, while giving HR/Admin staff powerful tools to manage the workforce and approve requests in real time.

---

## ✨ Key Features

### 🔐 Authentication & Authorization
- Secure sign up with Employee ID, email, password, and role
- Email verification on registration
- Password security rules enforced
- Role-based access control (Admin/HR vs Employee)

### 📊 Dashboards
- **Employee Dashboard:** quick-access cards for Profile, Attendance, Leave Requests + recent activity/alerts
- **Admin/HR Dashboard:** employee list, attendance records, leave approvals, employee switching

### 👤 Employee Profile Management
- View personal details, job details, salary structure, documents & profile picture
- Employees edit limited fields (address, phone, picture); Admins edit all fields

### 🕐 Attendance Management
- Daily & weekly attendance views
- Check-in / check-out functionality
- Status types: **Present, Absent, Half-day, Leave**
- Employees view own records; Admin/HR view all

### 🌴 Leave & Time-Off Management
- Apply for Paid / Sick / Unpaid leave via calendar date range
- Add remarks; monthly calendar with Present/Absent markers
- Request statuses: **Pending, Approved, Rejected**
- Admin/HR approval workflow with comments — changes reflect instantly

### 💰 Payroll / Salary Management
- Employees: read-only payroll view
- Admin: view all payroll, update salary structures, ensure accuracy

---

## 👥 User Roles

| User Type | Description |
|---|---|
| **Admin / HR Officer** | Manages employees, approves leave & attendance, views payroll details |
| **Employee** | Views personal profile & attendance, applies for leave, views salary details |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Database | **MariaDB / MySQL** |
| Backend | *\<add your backend, e.g. Node.js / Express, Flask, PHP\>* |
| Frontend | *\<add your frontend, e.g. React, Vue, plain HTML/CSS/JS\>* |
| Auth | JWT / Session-based *\<update as used\>* |
| OS / Deployment | Void Linux (runit service management) |

---

## 🗄 Database Schema

The system uses **10 relational tables**:

| Table | Purpose |
|---|---|
| `users` | Authentication, roles, email verification |
| `employee_profiles` | Personal details & profile picture |
| `job_details` | Designation, department, joining info, reporting manager |
| `documents` | Employee document storage references |
| `attendance` | Daily attendance with check-in/out & status |
| `leave_types` | Leave categories (Paid, Sick, Unpaid) |
| `leave_requests` | Leave applications with approval workflow |
| `salary_structures` | Employee salary breakdown (admin-managed) |
| `payroll_records` | Monthly payslips |
| `activity_logs` | Audit trail & dashboard activity feed |

**Relationships:** All employee-related tables reference `users(user_id)` via foreign keys with cascading deletes. Leave requests link to both applicants and reviewers, enabling the full approval workflow.

---

## 🚀 Getting Started

### Prerequisites
- MariaDB / MySQL server
- *\<your backend runtime, e.g. Node.js 18+ / Python 3.10+ / PHP 8+\>*

### Clone the repository

```bash
git clone <your-repo-url>
cd hrms
```

---

## 🗃 Database Setup

**1. Ensure MariaDB is running** (Void Linux / runit):

```bash
sudo ln -s /etc/sv/mysqld /var/service/   # first time only
sudo sv start mysqld
sudo sv status mysqld
```

**2. Load the schema:**

```bash
sudo mariadb < hrms_schema.sql
```

**3. Create the application database user:**

```sql
CREATE USER 'hrms_app'@'localhost' IDENTIFIED BY 'your_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON hrms.* TO 'hrms_app'@'localhost';
FLUSH PRIVILEGES;
```

**4. Verify:**

```bash
sudo mariadb -e "USE hrms; SHOW TABLES;"
```

You should see all 10 tables and the seeded leave types (Paid, Sick, Unpaid).

---

## 📁 Project Structure

```
hrms/
├── hrms_schema.sql   # Database schema & seed data
├── backend/          # API / server code
├── frontend/         # UI code
├── docs/             # Documentation & ER diagram
└── README.md         # This file
```

---

## 🎨 Design Reference

Wireframes & flow diagram: [Excalidraw Board](https://link.excalidraw.com/l/65VNwvy7c4X/58RLEJ4oOwh)

---

## 👨‍💻 Team

*\<Add team member names & roles here\>*

- **Saptarshi Roy** — Backend
- **Aahir Sengupta** — Frontend+Debugging

---

## 📄 License

This project was built for Odoo + adamas university hackathon

<p align="center"><b>Built with ❤️ for a smarter workplace.</b></p>
