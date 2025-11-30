# Quick Start Guide - VLAN Management System

## ⚡ Quick Setup (5 minutes)

### Option 1: Automated Setup (Recommended)
```bash
# Double-click setup.bat (Windows)
# atau jalankan di terminal:
setup.bat
```

### Option 2: Manual Setup

#### 1. Navigate to project folder
```bash
cd c:\xampp\htdocs\TR DPJ\vlan-management-web
```

#### 2. Create Virtual Environment
```bash
python -m venv venv
```

#### 3. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 5. Setup Environment Variables
```bash
# Copy template
copy .env.example .env

# Edit .env (optional - defaults are for Cisco Sandbox)
```

#### 6. Initialize Database
```bash
python -c "from backend.app import create_app, db; app = create_app(); db.create_all()"
```

#### 7. Run Application
```bash
python run.py
```

---

## 🌐 Access Application

Open browser dan buka: **http://localhost:5000**

### Login Demo
- Name: `Student Name`
- NIM: `12345678`
- Email: `student@university.edu`

Click "Login / Register" - account akan dibuat otomatis

---

## 📝 First Steps

### 1. Dashboard Overview
- Overview tab menampilkan stats dan charts
- Check device status (Online/Offline)
- Lihat recent activities

### 2. Create VLAN
1. Click "Create New VLAN" button
2. Fill form:
   - VLAN ID: 100 (atau number lain 2-4094)
   - VLAN Name: TEST_VLAN
   - Subnet Mask: 255.255.255.0 (default)
   - Auto-delete: optional
3. Click "Create VLAN"
4. VLAN akan ditampilkan di table

### 3. Manage VLANs
- **View**: Click pada VLAN ID di table
- **Edit**: Click "Edit" button
- **Delete**: Click "Delete" button + confirm

### 4. Check Device
1. Go to "Device" tab
2. Click "Check Status" untuk verifikasi koneksi
3. Click "View Device VLANs" untuk lihat VLANs di Cisco

### 5. View Activities
- Go to "Activities" tab
- Lihat semua operasi yang dilakukan
- Filter by user atau action

---

## 🎨 UI Customization

### Theme Colors
Edit `frontend/static/css/style.css`:
```css
:root {
    --primary-color: #6366f1;        /* Blue */
    --secondary-color: #8b5cf6;      /* Purple */
    --success-color: #10b981;        /* Green */
    --danger-color: #ef4444;         /* Red */
    --warning-color: #f59e0b;        /* Orange */
    /* ... lebih banyak variables */
}
```

### Font
Default menggunakan "Poppins" dari Google Fonts. Bisa di-change di `style.css`:
```css
font-family: 'Poppins', sans-serif;  /* Change here */
```

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# Flask
FLASK_ENV=development              # development, testing, production
SECRET_KEY=your-secret-key         # Change in production!

# Database
DATABASE_URL=sqlite:///vlan_management.db

# Cisco Device
CISCO_HOST=sbx-nxos-mgmt.cisco.com  # Cisco sandbox host
CISCO_USERNAME=admin                # Cisco username
CISCO_PASSWORD=Admin_1234!          # Cisco password
CISCO_PORT=22
CISCO_TIMEOUT=30

# Session
SESSION_TIMEOUT_MINUTES=30          # Auto-logout after 30 mins

# CORS
CORS_ORIGINS=http://localhost:5000,http://localhost:3000
```

---

## 🐛 Common Issues

### Issue: Port 5000 Already in Use
```bash
# Solution: Change port in run.py
app.run(debug=True, host='0.0.0.0', port=5001)  # Use 5001 instead
```

### Issue: Cannot Connect to Database
```bash
# Solution: Delete database and recreate
del backend\database\vlan_management.db
python run.py  # Will recreate automatically
```

### Issue: Cisco Device Connection Failed
```bash
# Solution: Check credentials in .env
# Default for Cisco Sandbox:
CISCO_USERNAME=admin
CISCO_PASSWORD=Admin_1234!
CISCO_HOST=sbx-nxos-mgmt.cisco.com
```

### Issue: Static Files Not Loading
```bash
# Make sure you're accessing through Flask server
# NOT by opening HTML file directly
# Always use: http://localhost:5000
```

---

## 📊 Database

### Location
```
backend/vlan_management.db  (SQLite database)
```

### Tables
- `users` - User accounts
- `vlan_configs` - VLAN configurations
- `user_sessions` - Active sessions
- `activity_logs` - Audit trail

### Reset Database
```bash
# Delete database file
del backend\vlan_management.db

# App will recreate on next run
python run.py
```

---

## 🚀 Deployment

### Development
```bash
FLASK_ENV=development python run.py
```

### Production
1. Edit `backend/config.py`:
   ```python
   DEBUG = False
   SESSION_COOKIE_SECURE = True
   ```

2. Update `.env`:
   ```env
   FLASK_ENV=production
   SECRET_KEY=your-production-secret-key
   ```

3. Use production server (not Flask development):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
   ```

---

## 📚 Project Structure

```
vlan-management-web/
├── backend/
│   ├── app.py              ← Main Flask app
│   ├── models.py           ← Database models
│   ├── config.py           ← Configuration
│   ├── cisco_manager.py    ← Device communication
│   ├── utils.py            ← Helper functions
│   └── database/           ← Database files
│
├── frontend/
│   ├── templates/          ← HTML files
│   └── static/             ← CSS & JavaScript
│
├── run.py                  ← Entry point
├── requirements.txt        ← Dependencies
├── .env                    ← Configuration
└── README.md               ← Full documentation
```

---

## 🎓 Learning Objectives

Dengan mengerjakan proyek ini, Anda belajar:

✅ **Backend (Python)**
- Flask web framework
- SQLAlchemy ORM & database design
- RESTful API design
- Network device integration (Netmiko)
- Authentication & session management
- Error handling & logging

✅ **Frontend (HTML/CSS/JavaScript)**
- Modern responsive design
- ES6+ JavaScript
- Async/await & fetch API
- DOM manipulation
- UI/UX best practices

✅ **Network**
- Cisco NX-OS device management
- SSH protocol
- VLAN configuration
- Network automation

---

## 📞 Support

### Getting Help
1. Check README.md for full documentation
2. Look at error messages in browser console (F12)
3. Check terminal output for Python errors
4. Review code comments for implementation details

### Common Endpoints
- Home: http://localhost:5000/
- Login: http://localhost:5000/login
- Dashboard: http://localhost:5000/dashboard
- API: http://localhost:5000/api/*

---

## ✨ Features Checklist

- [x] CRUD Operations (Create, Read, Update, Delete)
- [x] User Management (Name + NIM)
- [x] Dashboard with Statistics
- [x] Activity Logging
- [x] Real-time Device Integration
- [x] Auto-Delete VLAN (Bonus)
- [x] Subnet Management (Bonus)
- [x] Responsive UI
- [x] Dark Theme
- [x] RESTful API
- [x] Session Management
- [x] Error Handling

---

## 🎉 Ready to Go!

Aplikasi Anda sudah siap. Mulai dari:
1. **Run**: `python run.py`
2. **Open**: http://localhost:5000
3. **Login**: Gunakan nama dan NIM Anda
4. **Create**: VLAN pertama Anda
5. **Monitor**: Lihat activities dan statistics

---

**Happy Learning! 🚀**

*Last Updated: November 26, 2025*
