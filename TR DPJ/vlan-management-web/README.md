# VLAN Management System - Web Application

## 📋 Deskripsi Proyek

Sistem manajemen VLAN berbasis web yang mengintegrasikan frontend modern dengan backend Python Flask dan koneksi langsung ke Cisco Sandbox. Aplikasi ini memungkinkan pengguna untuk membuat, membaca, mengubah, dan menghapus (CRUD) VLAN dengan antarmuka web yang intuitif dan responsif.

### Fitur Utama
- ✅ **CRUD Operations** - Create, Read, Update, Delete VLANs
- ✅ **User Management** - Registrasi user dengan NIM dan nama
- ✅ **Real-time Dashboard** - Monitoring VLAN dan device status
- ✅ **Activity Logging** - Track semua operasi dengan timestamp
- ✅ **Auto-Delete Feature** - VLAN otomatis dihapus setelah periode tertentu (BONUS)
- ✅ **Subnet Management** - Validasi dan kalkulasi subnet mask (BONUS)
- ✅ **Device Integration** - Koneksi real-time ke Cisco NX-OS
- ✅ **Responsive UI** - Modern, dark-themed interface
- ✅ **Session Management** - Auto-cleanup expired sessions

---

## 🎯 Fitur Bonus

### 1. **Auto-Delete VLAN**
VLANs dapat dikonfigurasi untuk otomatis dihapus setelah periode waktu tertentu:
- User bisa set waktu expiry (dalam jam)
- Background job akan menandai VLAN sebagai "expired"
- Admin bisa membersihkan expired VLANs

**Implementasi:**
```python
# Di database model
auto_delete = db.Column(db.Boolean, default=False)
expires_at = db.Column(db.DateTime, nullable=True)
status = db.Column(db.String(20), default='active')  # active, inactive, expired

# Fungsi cleanup
def cleanup_expired_vlans(app):
    expired_vlans = VlanConfig.query.filter(
        VlanConfig.auto_delete == True,
        VlanConfig.expires_at < datetime.utcnow(),
        VlanConfig.status == 'active'
    ).all()
```

### 2. **Subnet Mask Validation & Host Limit**
- Validasi format subnet mask (255.x.x.x)
- Auto-kalkulasi max hosts dari subnet mask
- Pembatasan jumlah host yang bisa ditambahkan per VLAN

**Implementasi:**
```python
def validate_subnet_mask(subnet_mask: str) -> Tuple[bool, str]
def calculate_max_hosts(subnet_mask: str) -> int

# Di model VLAN
max_hosts = db.Column(db.Integer, nullable=True)
host_count = db.Column(db.Integer, default=0)

def can_add_hosts(self, count=1):
    if self.max_hosts is None:
        return True
    return (self.host_count + count) <= self.max_hosts
```

### 3. **Session Timeout Auto-Cleanup**
- Sessions otomatis cleanup ketika expired
- Configurable timeout period (default 30 menit)
- User activities dicatat di database

### 4. **Activity Logging**
- Semua operasi CRUD dicatat
- Include: user, IP address, action, status, timestamp
- Dapat di-query untuk audit trail

---

## 📁 Struktur Proyek

```
vlan-management-web/
├── backend/
│   ├── app.py                 # Flask main application
│   ├── config.py              # Configuration settings
│   ├── models.py              # SQLAlchemy database models
│   ├── cisco_manager.py       # Cisco device management
│   ├── utils.py               # Utility functions
│   └── database/              # Database files
│
├── frontend/
│   ├── templates/
│   │   ├── index.html         # Home page
│   │   ├── login.html         # Login page
│   │   ├── dashboard.html     # Main dashboard
│   │   └── profile.html       # User profile
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # Main stylesheet
│   │   └── js/
│   │       ├── main.js        # Main page JavaScript
│   │       └── dashboard.js   # Dashboard JavaScript
│
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7+
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone/Download Project
```bash
cd c:\xampp\htdocs\TR DPJ\vlan-management-web
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Setup Environment Variables
```bash
# Copy template
copy .env.example .env

# Edit .env dengan credentials Cisco Anda
```

### Step 6: Initialize Database
```bash
python -c "from backend.app import create_app, db; app = create_app(); db.create_all()"
```

### Step 7: Run Application
```bash
python backend/app.py
```

Aplikasi akan berjalan di: **http://localhost:5000**

---

## 📝 API Documentation

### Authentication Routes

#### **Login / Register**
```
POST /login
Content-Type: application/json

{
    "name": "John Doe",
    "nim": "12345678",
    "email": "john@example.com"
}

Response:
{
    "success": true,
    "data": {
        "id": "uuid",
        "name": "John Doe",
        "nim": "12345678",
        "email": "john@example.com",
        "total_vlans": 0,
        "created_at": "2025-11-26T10:30:00"
    },
    "message": "Login successful"
}
```

### User Routes

#### **Get All Users**
```
GET /api/users

Response:
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "name": "John Doe",
            "nim": "12345678",
            "email": "john@example.com",
            "total_vlans": 5,
            "created_at": "2025-11-26T10:30:00"
        }
    ]
}
```

#### **Get Current User Profile**
```
GET /api/users/profile

Response:
{
    "success": true,
    "data": {
        "id": "uuid",
        "name": "John Doe",
        "nim": "12345678",
        "email": "john@example.com",
        "total_vlans": 5,
        "vlans": [...]
    }
}
```

### VLAN Routes

#### **Get All VLANs**
```
GET /api/vlans

Response:
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "vlan_id": 100,
            "vlan_name": "LAB_VLAN",
            "status": "active",
            "subnet_mask": "255.255.255.0",
            "max_hosts": 254,
            "user_name": "John Doe",
            "created_at": "2025-11-26T10:30:00",
            "expires_at": null,
            "auto_delete": false
        }
    ]
}
```

#### **Create VLAN**
```
POST /api/vlans
Content-Type: application/json

{
    "vlan_id": 100,
    "vlan_name": "LAB_VLAN",
    "description": "Lab network VLAN",
    "subnet_mask": "255.255.255.0",
    "auto_delete": true,
    "expiry_hours": 24
}

Response:
{
    "success": true,
    "data": {
        "id": "uuid",
        "vlan_id": 100,
        "vlan_name": "LAB_VLAN",
        "status": "active",
        ...
    },
    "message": "VLAN created successfully"
}
```

#### **Update VLAN**
```
PUT /api/vlans/{vlan_id}
Content-Type: application/json

{
    "vlan_name": "NEW_NAME",
    "description": "Updated description",
    "subnet_mask": "255.255.0.0"
}

Response:
{
    "success": true,
    "data": { ... },
    "message": "VLAN updated successfully"
}
```

#### **Delete VLAN**
```
DELETE /api/vlans/{vlan_id}

Response:
{
    "success": true,
    "message": "VLAN 100 deleted successfully"
}
```

#### **Get VLANs by User**
```
GET /api/vlans/user/{user_id}

Response:
{
    "success": true,
    "data": [...]
}
```

### Device Routes

#### **Get Device Status**
```
GET /api/device/status

Response:
{
    "success": true,
    "data": {
        "connected": true,
        "host": "sbx-nxos-mgmt.cisco.com",
        "device_type": "cisco_nxos",
        "message": "Connected successfully"
    }
}
```

#### **Get Device VLANs**
```
GET /api/device/vlans

Response:
{
    "success": true,
    "data": {
        "device_vlans": [
            {
                "vlan_id": 1,
                "vlan_name": "default",
                "status": "active"
            }
        ]
    }
}
```

### Activity Routes

#### **Get All Activities**
```
GET /api/activities?limit=50

Response:
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "user_id": "uuid",
            "action": "CREATE",
            "details": "Created VLAN 100",
            "status": "SUCCESS",
            "ip_address": "192.168.1.1",
            "created_at": "2025-11-26T10:30:00"
        }
    ]
}
```

#### **Get User Activities**
```
GET /api/activities/user/{user_id}?limit=50

Response:
{
    "success": true,
    "data": [...]
}
```

---

## 🔐 Security Features

### 1. **Session Management**
- Sessions stored in database
- Auto-cleanup expired sessions
- Session timeout: 30 minutes (configurable)

### 2. **Input Validation**
- VLAN ID validation (1-4094)
- VLAN name validation (max 32 chars)
- Subnet mask format validation
- Email validation

### 3. **Error Handling**
- Comprehensive error messages
- Logging all errors
- API error responses

### 4. **Database Protection**
- Protected VLAN 1 (default VLAN)
- Ownership verification on VLAN operations
- Transaction rollback on errors

---

## 🎨 Frontend Features

### Pages
1. **Home Page** - Landing page dengan hero section dan features
2. **Login Page** - User registration/login form
3. **Dashboard** - Main application interface
   - Overview section dengan stats dan charts
   - VLANs management table
   - Users directory
   - Activity logs
   - Device status
   - Settings

### UI/UX Features
- Dark theme dengan gradient primary colors
- Responsive design (desktop, tablet, mobile)
- Smooth animations dan transitions
- Modal dialogs untuk forms
- Toast notifications untuk feedback
- Real-time data updates
- Interactive charts (Pie chart untuk VLAN distribution)

---

## 📊 Database Models

### User Model
```python
- id (UUID, primary key)
- name (String)
- nim (String, unique)
- email (String, unique)
- created_at (DateTime)
- updated_at (DateTime)
- relationships: vlans, sessions
```

### VlanConfig Model
```python
- id (UUID, primary key)
- vlan_id (Integer)
- vlan_name (String)
- description (String)
- user_id (Foreign Key)
- subnet_mask (String)
- max_hosts (Integer)
- host_count (Integer)
- status (String) # active, inactive, expired
- created_at (DateTime)
- updated_at (DateTime)
- expires_at (DateTime, nullable)
- auto_delete (Boolean)
- device_synced (Boolean)
- sync_timestamp (DateTime)
```

### UserSession Model
```python
- id (UUID, primary key)
- user_id (Foreign Key)
- session_token (String)
- ip_address (String)
- user_agent (String)
- created_at (DateTime)
- last_activity (DateTime)
- expires_at (DateTime)
```

### ActivityLog Model
```python
- id (UUID, primary key)
- user_id (Foreign Key)
- vlan_id (Foreign Key)
- action (String) # CREATE, READ, UPDATE, DELETE, LOGIN, LOGOUT
- details (Text)
- status (String) # SUCCESS, FAILED
- ip_address (String)
- created_at (DateTime)
```

---

## 🔄 Workflow

### User Registration Flow
1. User masuk ke `/login`
2. Input name, NIM, email
3. System check apakah user sudah ada
4. Jika tidak, create new user
5. Create session dan redirect ke dashboard
6. Log activity: LOGIN

### Create VLAN Flow
1. User click "Create New VLAN" di dashboard
2. Form modal terbuka
3. User input VLAN details
4. System validate input
5. Connect ke Cisco device
6. Kirim create commands
7. Save ke database
8. Log activity: CREATE
9. Reload VLAN list di dashboard

### Auto-Delete Flow
1. User enable "Auto-delete VLAN"
2. Set expiry time (e.g., 24 hours)
3. System calculate expires_at timestamp
4. Save ke database dengan auto_delete=true
5. Background job check setiap jam
6. Jika expired, mark status as "expired"
7. User bisa melihat expired VLANs di dashboard

---

## 🧪 Testing

### Test Create VLAN
```bash
# 1. Open browser, go to http://localhost:5000
# 2. Login dengan nama dan NIM Anda
# 3. Click "Create New VLAN"
# 4. Fill form:
#    - VLAN ID: 100
#    - VLAN Name: TEST_VLAN
#    - Subnet: 255.255.255.0
#    - Auto-delete: checked
#    - Expiry: 24 hours
# 5. Click Create
# 6. Check device: show vlan brief
```

### Test Activity Logging
```bash
# 1. Di dashboard, pergi ke Activities tab
# 2. Lakukan beberapa operasi (create, update, delete)
# 3. Activities harus tercatat dengan benar
# 4. Setiap activity harus punya:
#    - Timestamp
#    - User name
#    - Action (CREATE/UPDATE/DELETE)
#    - Status (SUCCESS/FAILED)
```

---

## 🚨 Troubleshooting

### Error: Connection Timeout
```
Error: Connection timeout to sbx-nxos-mgmt.cisco.com

Solution:
1. Check internet connection
2. Verify Cisco sandbox is accessible
3. Check credentials di .env
4. Try ping sbx-nxos-mgmt.cisco.com
```

### Error: Authentication Failed
```
Error: Authentication failed - check credentials

Solution:
1. Verify username dan password di .env
2. Cisco sandbox default: admin / Admin_1234!
3. Check apakah user punya privilege yang cukup
```

### Error: Database Locked
```
Error: database is locked

Solution:
1. Close semua Flask instances
2. Delete vlan_management.db
3. Restart aplikasi (akan recreate database)
```

### Port Already in Use
```
Error: Address already in use

Solution:
# Change port di app.py
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)  # Change to 5001
```

---

## 📚 Development Guide

### Adding New Feature

#### 1. Create API Endpoint
```python
# backend/app.py
@app.route('/api/new-feature', methods=['GET', 'POST'])
def new_feature():
    # Implementation
    pass
```

#### 2. Add Database Model (jika perlu)
```python
# backend/models.py
class NewModel(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    # fields
```

#### 3. Add Frontend Component
```html
<!-- frontend/templates/dashboard.html -->
<section id="new-feature" class="content-section">
    <!-- UI -->
</section>
```

#### 4. Add Frontend Logic
```javascript
// frontend/static/js/dashboard.js
async function loadNewFeature() {
    // Fetch data
}
```

---

## 🔗 Integration Points

### Cisco NX-OS Commands Used
```
vlan <id>                  # Create VLAN
name <name>                # Set VLAN name
no vlan <id>               # Delete VLAN
show vlan id <id>          # Show specific VLAN
show vlan brief            # Show all VLANs
write memory               # Save config
```

### Python Libraries
- **Flask**: Web framework
- **Flask-CORS**: CORS support
- **Flask-SQLAlchemy**: ORM
- **Netmiko**: SSH to network devices
- **python-dotenv**: Environment variables

---

## 📞 Support & Documentation

- **Flask Docs**: https://flask.palletsprojects.com/
- **Netmiko Docs**: https://github.com/ktbyers/netmiko
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Cisco NX-OS Docs**: https://www.cisco.com/c/en/us/support/switches/nexus-9000-series-switches/

---

## 📄 License

Proyek ini dibuat untuk keperluan edukasi.

---

## ✨ Conclusion

VLAN Management System adalah aplikasi web modern yang mendemonstrasikan:
- Full-stack web development (Python + HTML/CSS/JS)
- Network automation dengan Netmiko
- Database management dengan SQLAlchemy
- RESTful API design
- User authentication & session management
- Real-time device integration

Aplikasi ini siap untuk diproduksi dengan beberapa improvement minor.

---

**Last Updated**: November 26, 2025  
**Version**: 1.0.0
