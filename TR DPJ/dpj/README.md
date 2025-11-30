# Automasi Jaringan - Manajemen VLAN Cisco NX-OS

## 📖 Deskripsi

Proyek ini adalah script Python untuk otomasi jaringan yang digunakan untuk mengelola VLAN pada perangkat Cisco NX-OS menggunakan library Netmiko. Script ini memungkinkan Anda untuk membuat VLAN, memverifikasi VLAN yang dibuat, dan menampilkan semua VLAN yang ada pada perangkat.

## 🎯 Tujuan Pembelajaran

Setelah mempelajari code ini, mahasiswa diharapkan dapat:
- Memahami konsep automasi jaringan menggunakan Python
- Menggunakan library Netmiko untuk koneksi SSH ke perangkat jaringan
- Menerapkan Object-Oriented Programming (OOP) dalam Python
- Mengelola VLAN pada perangkat Cisco secara otomatis
- Menerapkan error handling dan logging yang baik

## 📋 Prerequisites

### Software yang Dibutuhkan:
- Python 3.7 atau lebih tinggi
- pip (Python package manager)

### Library Python:
```bash
pip install netmiko
```

## 🚀 Cara Instalasi

1. **Clone atau download project ini**
   ```bash
   cd d:\ast\dpj
   ```

2. **Install dependencies**
   ```bash
   pip install netmiko
   ```

3. **Jalankan script**
   ```bash
   python index.py
   ```

## 📁 Struktur Project

```
dpj/
│
├── index.py          # File utama script
├── README.md         # Dokumentasi (file ini)
└── session.log       # Log sesi (dibuat otomatis saat script berjalan)
```

## 💻 Cara Menggunakan

### Menjalankan Script

1. Jalankan command berikut di terminal:
   ```bash
   python index.py
   ```

2. Program akan menampilkan **CRUD Menu** dengan 6 pilihan:
   ```
   ============================================================
              VLAN MANAGEMENT SYSTEM - CRUD MENU
   ============================================================
   1. Create VLAN       - Buat VLAN baru
   2. Read VLAN         - Lihat VLAN tertentu
   3. Update VLAN       - Update nama VLAN
   4. Delete VLAN       - Hapus VLAN
   5. Show All VLANs    - Tampilkan semua VLAN
   6. Exit              - Keluar dari program
   ============================================================
   ```

3. Pilih menu dengan mengetik angka (1-6) dan tekan Enter

### Contoh Penggunaan Setiap Menu:

#### 1️⃣ CREATE VLAN (Menu 1)
```
Pilih menu (1-6): 1

--- CREATE VLAN ---
Masukkan VLAN ID (1-4094): 100
Masukkan VLAN Name: LAB_VLAN

SUCCESS: VLAN 100 berhasil dibuat!
```

#### 2️⃣ READ VLAN (Menu 2)
```
Pilih menu (1-6): 2

--- READ VLAN ---
Masukkan VLAN ID yang ingin dilihat: 100

============================================================
VLAN Name                             Status    Ports
---- -------------------------------- --------- -----------
100  LAB_VLAN                         active
============================================================
```

#### 3️⃣ UPDATE VLAN (Menu 3)
```
Pilih menu (1-6): 3

--- UPDATE VLAN ---
Masukkan VLAN ID yang ingin diupdate: 100
VLAN 100 ditemukan.
Masukkan nama VLAN baru: NETWORK_LAB

SUCCESS: VLAN 100 berhasil diupdate dengan nama 'NETWORK_LAB'
```

#### 4️⃣ DELETE VLAN (Menu 4)
```
Pilih menu (1-6): 4

--- DELETE VLAN ---
Masukkan VLAN ID yang ingin dihapus: 100
Apakah Anda yakin ingin menghapus VLAN 100? (yes/no): yes

SUCCESS: VLAN 100 berhasil dihapus!
```

#### 5️⃣ SHOW ALL VLANs (Menu 5)
```
Pilih menu (1-6): 5

--- SHOW ALL VLANs ---
============================================================
VLAN Name                             Status    Ports
---- -------------------------------- --------- -----------
1    default                          active    Eth1/1
100  NETWORK_LAB                      active
200  GUEST_VLAN                       active
============================================================
```

#### 6️⃣ EXIT (Menu 6)
```
Pilih menu (1-6): 6

Terima kasih telah menggunakan VLAN Management System!
```

## 🔍 Penjelasan Kode Detail

### 1. Import Libraries

```python
import logging
from typing import Optional
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
```

**Penjelasan:**
- `logging`: Library untuk mencatat aktivitas program (log file)
- `typing`: Untuk type hints - memberi tahu tipe data yang diharapkan
- `netmiko`: Library utama untuk koneksi SSH ke perangkat jaringan Cisco
- `NetmikoTimeoutException`: Exception yang dilempar ketika koneksi timeout
- `NetmikoAuthenticationException`: Exception untuk error autentikasi (username/password salah)

---

### 2. Konfigurasi Logging

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

**Penjelasan:**
- `level=logging.INFO`: Menampilkan log level INFO ke atas (INFO, WARNING, ERROR)
- `format`: Format pesan log dengan timestamp, level, dan message
- `logger`: Object untuk menulis log

---

### 3. Class NetworkDevice

Class ini adalah inti dari program yang mengelola semua operasi jaringan menggunakan konsep **Object-Oriented Programming (OOP)**.

#### A. Method `__init__` (Constructor)
```python
def __init__(self, device_config: dict):
    self.device_config = device_config
    self.connection: Optional[ConnectHandler] = None
```

**Penjelasan:**
- Constructor dipanggil saat object dibuat
- `self.device_config`: Menyimpan konfigurasi perangkat (host, username, password, dll)
- `self.connection`: Variabel untuk menyimpan koneksi, awalnya None
- `Optional[ConnectHandler]`: Type hint yang artinya bisa ConnectHandler atau None

---

#### B. Method `__enter__` dan `__exit__` (Context Manager)
```python
def __enter__(self):
    """Membuka koneksi saat masuk context"""
    try:
        logger.info(f"Connecting to {self.device_config['host']}...")
        self.connection = ConnectHandler(**self.device_config)
        logger.info("Connected successfully!")
        return self
    except NetmikoTimeoutException:
        logger.error(f"Connection timeout to {self.device_config['host']}")
        raise
    except NetmikoAuthenticationException:
        logger.error("Authentication failed - check credentials")
        raise

def __exit__(self, exc_type, exc_val, exc_tb):
    """Menutup koneksi otomatis saat keluar context"""
    if self.connection:
        self.connection.disconnect()
        logger.info("Disconnected")
```

**Penjelasan:**
- Implementasi **Context Manager** (syntax `with`)
- `__enter__`: Dipanggil saat masuk blok `with`, membuka koneksi
- `__exit__`: Dipanggil saat keluar blok `with`, menutup koneksi otomatis
- **Keuntungan**: Koneksi pasti ditutup meskipun ada error
- `**self.device_config`: Unpacking dictionary menjadi parameter keyword

**Contoh Penggunaan:**
```python
with NetworkDevice(config) as device:
    device.create_vlan("10", "TEST")  # Koneksi terbuka
# Koneksi otomatis tertutup di sini
```

---

#### C. Method `create_vlan` (CREATE - CRUD)
```python
def create_vlan(self, vlan_id: str, vlan_name: str) -> bool:
    """Membuat VLAN baru"""
    if not self.connection:
        logger.error("No active connection")
        return False
    
    # Validasi VLAN ID
    try:
        vlan_num = int(vlan_id)
        if not (1 <= vlan_num <= 4094):
            logger.error(f"Invalid VLAN ID: {vlan_id}")
            return False
    except ValueError:
        logger.error(f"VLAN ID must be numeric: {vlan_id}")
        return False
    
    # Kirim command ke perangkat
    commands = [
        f"vlan {vlan_id}",
        f"name {vlan_name}"
    ]
    output = self.connection.send_config_set(commands)
    self.connection.save_config()  # Simpan konfigurasi
    return True
```

**Penjelasan:**
- **Input**: vlan_id (string), vlan_name (string)
- **Output**: True jika berhasil, False jika gagal
- **Validasi**: Cek VLAN ID antara 1-4094 dan harus numeric
- `send_config_set()`: Kirim multiple commands sekaligus
- `save_config()`: Simpan konfigurasi ke perangkat (wr mem)
- **f-string**: Format string dengan variabel, contoh: `f"vlan {vlan_id}"`

**Cisco Commands yang Dikirim:**
```
vlan 100
name LAB_VLAN
```

---

#### D. Method `verify_vlan` (READ - CRUD)
```python
def verify_vlan(self, vlan_id: str) -> Optional[str]:
    """Verifikasi VLAN tertentu"""
    output = self.connection.send_command(f"show vlan id {vlan_id}")
    
    if "not found" in output.lower() or "invalid" in output.lower():
        logger.warning(f"VLAN {vlan_id} not found")
        return None
    
    return output
```

**Penjelasan:**
- **Input**: vlan_id (string)
- **Output**: String berisi info VLAN, atau None jika tidak ditemukan
- `send_command()`: Kirim single command (non-configuration)
- Cek apakah VLAN exists dengan mencari kata "not found" atau "invalid"
- `.lower()`: Ubah ke lowercase untuk case-insensitive matching

**Cisco Command:**
```
show vlan id 100
```

---

#### E. Method `show_all_vlans` (READ ALL - CRUD)
```python
def show_all_vlans(self) -> Optional[str]:
    """Menampilkan semua VLAN"""
    output = self.connection.send_command("show vlan brief")
    return output
```

**Penjelasan:**
- **Output**: String berisi semua VLAN
- `show vlan brief`: Command untuk menampilkan VLAN dalam format ringkas

**Cisco Command:**
```
show vlan brief
```

---

#### F. Method `update_vlan` (UPDATE - CRUD)
```python
def update_vlan(self, vlan_id: str, new_vlan_name: str) -> bool:
    """Update nama VLAN"""
    commands = [
        f"vlan {vlan_id}",
        f"name {new_vlan_name}"
    ]
    output = self.connection.send_config_set(commands)
    self.connection.save_config()
    return True
```

**Penjelasan:**
- **Input**: vlan_id (string), new_vlan_name (string)
- **Output**: True jika berhasil, False jika gagal
- Masuk ke VLAN config mode, lalu set nama baru
- Sama seperti create, tapi untuk VLAN yang sudah ada

**Cisco Commands:**
```
vlan 100
name NEW_NAME
```

---

#### G. Method `delete_vlan` (DELETE - CRUD)
```python
def delete_vlan(self, vlan_id: str) -> bool:
    """Hapus VLAN"""
    if vlan_id == "1":
        logger.error("Cannot delete default VLAN 1")
        return False
    
    command = f"no vlan {vlan_id}"
    output = self.connection.send_config_set(command)
    self.connection.save_config()
    return True
```

**Penjelasan:**
- **Input**: vlan_id (string)
- **Output**: True jika berhasil, False jika gagal
- **Proteksi**: Tidak bisa hapus VLAN 1 (default VLAN)
- `no vlan X`: Command Cisco untuk menghapus VLAN

**Cisco Command:**
```
no vlan 100
```

---

### 4. Menu Functions

#### A. Function `display_menu()`
```python
def display_menu():
    """Menampilkan menu CRUD"""
    print("\n" + "="*60)
    print("           VLAN MANAGEMENT SYSTEM - CRUD MENU")
    print("="*60)
    print("1. Create VLAN       - Buat VLAN baru")
    # ... dst
```

**Penjelasan:**
- Fungsi untuk menampilkan menu
- `"="*60`: Membuat garis separator dengan 60 karakter `=`
- `\n`: New line (baris baru)

---

#### B. Function `get_user_input()`
```python
def get_user_input(prompt: str) -> str:
    """Validasi input user"""
    while True:
        user_input = input(prompt).strip()
        if user_input:
            return user_input
        print("Input tidak boleh kosong. Silakan coba lagi.")
```

**Penjelasan:**
- **Loop forever** sampai user input valid
- `input()`: Terima input dari user
- `.strip()`: Hapus whitespace di awal dan akhir
- Validasi: Input tidak boleh kosong

---

#### C. Function `menu_create_vlan()`
```python
def menu_create_vlan(device: NetworkDevice):
    """Handler untuk menu Create"""
    print("\n--- CREATE VLAN ---")
    vlan_id = get_user_input("Masukkan VLAN ID (1-4094): ")
    vlan_name = get_user_input("Masukkan VLAN Name: ")
    
    if device.create_vlan(vlan_id, vlan_name):
        print(f"\nSUCCESS: VLAN {vlan_id} berhasil dibuat!")
    else:
        print("\nERROR: Gagal membuat VLAN")
```

**Penjelasan:**
- **Parameter**: Object NetworkDevice
- Terima input VLAN ID dan name dari user
- Panggil method `create_vlan()` dari object device
- Tampilkan pesan sukses atau error

---

#### D. Function `menu_delete_vlan()`
```python
def menu_delete_vlan(device: NetworkDevice):
    """Handler untuk menu Delete"""
    vlan_id = get_user_input("Masukkan VLAN ID yang ingin dihapus: ")
    
    # Verifikasi VLAN exists
    vlan_info = device.verify_vlan(vlan_id)
    if not vlan_info:
        print(f"\nERROR: VLAN {vlan_id} tidak ditemukan")
        return
    
    # Konfirmasi
    confirm = input(f"\nApakah Anda yakin? (yes/no): ").strip().lower()
    if confirm in ['yes', 'y']:
        if device.delete_vlan(vlan_id):
            print(f"\nSUCCESS: VLAN {vlan_id} berhasil dihapus!")
```

**Penjelasan:**
- Cek dulu apakah VLAN exists sebelum delete
- **Konfirmasi**: Minta user confirm sebelum delete
- `confirm in ['yes', 'y']`: Cek apakah input adalah 'yes' atau 'y'
- **Safety**: Hindari accidental deletion

---

### 5. Function `main()`

```python
def main():
    """Main function dengan CRUD menu loop"""
    device_config = {
        "device_type": "cisco_nxos",
        "host": "sbx-nxos-mgmt.cisco.com",
        "username": "admin",
        "password": "Admin_1234!",
        "port": 22,
        "timeout": 30,
        "session_log": "session.log",
    }
    
    try:
        with NetworkDevice(device_config) as device:
            while True:  # Loop menu sampai user exit
                display_menu()
                choice = input("\nPilih menu (1-6): ").strip()
                
                if choice == "1":
                    menu_create_vlan(device)
                elif choice == "2":
                    menu_read_vlan(device)
                elif choice == "3":
                    menu_update_vlan(device)
                elif choice == "4":
                    menu_delete_vlan(device)
                elif choice == "5":
                    menu_show_all_vlans(device)
                elif choice == "6":
                    print("\nTerima kasih!")
                    break  # Keluar dari loop
                else:
                    print("\nPilihan tidak valid!")
                
                input("\nTekan Enter untuk melanjutkan...")
    
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan oleh user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
```

**Penjelasan:**
- **device_config**: Dictionary berisi konfigurasi koneksi
- `while True`: Loop infinite sampai ada `break`
- **if-elif-else**: Branching untuk handle pilihan user
- `break`: Keluar dari loop while
- **try-except**: Error handling
  - `KeyboardInterrupt`: User tekan Ctrl+C
  - `Exception`: Error lainnya
- `input("\nTekan Enter...")`: Pause sebelum kembali ke menu

---

### 6. Entry Point

```python
if __name__ == "__main__":
    main()
```

**Penjelasan:**
- `__name__`: Variable special Python
- Ketika file dijalankan langsung: `__name__ == "__main__"`
- Ketika file di-import: `__name__ == "nama_module"`
- **Best Practice**: Memastikan `main()` hanya jalan saat file dieksekusi langsung
- Memungkinkan file ini di-import tanpa auto-run main()

---

### 7. Konsep-Konsep Penting

#### A. **Object-Oriented Programming (OOP)**
- **Class**: Blueprint untuk membuat object
- **Object**: Instance dari class
- **Method**: Function di dalam class
- **self**: Referensi ke object itu sendiri

#### B. **Context Manager**
- Pattern untuk manage resources (koneksi, file, dll)
- Syntax: `with ... as ...:`
- Benefit: Auto cleanup meskipun ada error

#### C. **Type Hints**
```python
def create_vlan(self, vlan_id: str, vlan_name: str) -> bool:
```
- `: str`: Parameter bertipe string
- `-> bool`: Return value bertipe boolean
- Benefit: Code lebih readable, IDE bisa kasih autocomplete

#### D. **Exception Handling**
```python
try:
    # Code yang mungkin error
except SpecificError:
    # Handle error spesifik
except Exception as e:
    # Handle semua error lain
```

#### E. **f-strings (Formatted String Literals)**
```python
name = "Python"
print(f"Hello {name}")  # Output: Hello Python
```
- Lebih mudah dibaca dari `.format()` atau `%`
- Evaluasi expression di dalam `{}`

#### F. **List Comprehension & Loops**
```python
while True:     # Loop sampai ada break
for item in items:  # Loop through collection
```

#### G. **Dictionary**
```python
config = {
    "host": "192.168.1.1",
    "username": "admin"
}
```
- Key-value pairs
- Seperti JSON di JavaScript
- Access: `config["host"]` atau `config.get("host")`

## 🛠️ Fitur-Fitur

### ✅ Yang Sudah Ada:
- **CRUD Menu System** - Interactive menu untuk operasi VLAN
- **CREATE** - Membuat VLAN baru dengan validasi ID (1-4094)
- **READ** - Melihat detail VLAN tertentu
- **UPDATE** - Mengubah nama VLAN yang sudah ada
- **DELETE** - Menghapus VLAN dengan konfirmasi
- **SHOW ALL** - Menampilkan semua VLAN dalam format tabel
- **Koneksi SSH Otomatis** - Auto connect/disconnect ke perangkat
- **Error Handling Lengkap** - Handle berbagai jenis error
- **Input Validation** - Validasi semua input user
- **Logging System** - Track semua aktivitas dengan timestamp
- **Auto-Save Configuration** - Konfigurasi otomatis tersimpan ke device
- **Context Manager** - Pengelolaan koneksi yang aman
- **Confirmation Dialog** - Konfirmasi sebelum delete untuk safety
- **Protection** - Tidak bisa hapus VLAN 1 (default VLAN)
- **Bilingual Interface** - Menu dalam Bahasa Indonesia

### 🔄 Yang Bisa Dikembangkan:
- Assign VLAN ke interface spesifik
- Baca konfigurasi dari file (JSON/YAML)
- Bulk operations (create/delete multiple VLANs sekaligus)
- Support multiple devices (switch lain)
- Export VLAN list ke CSV/Excel
- GUI interface dengan Tkinter atau PyQt
- Web interface dengan Flask/Django
- Backup & restore VLAN configuration
- VLAN statistics dan monitoring
- Integration dengan database

## 📊 Contoh Output Lengkap

### Saat Program Dimulai:
```
2025-11-02 10:30:15 - INFO - Connecting to sbx-nxos-mgmt.cisco.com...
2025-11-02 10:30:18 - INFO - Connected successfully!

============================================================
           VLAN MANAGEMENT SYSTEM - CRUD MENU
============================================================
1. Create VLAN       - Buat VLAN baru
2. Read VLAN         - Lihat VLAN tertentu
3. Update VLAN       - Update nama VLAN
4. Delete VLAN       - Hapus VLAN
5. Show All VLANs    - Tampilkan semua VLAN
6. Exit              - Keluar dari program
============================================================

Pilih menu (1-6): _
```

### Contoh Operasi CREATE (Menu 1):
```
Pilih menu (1-6): 1

--- CREATE VLAN ---
Masukkan VLAN ID (1-4094): 100
Masukkan VLAN Name: LAB_NETWORK

2025-11-02 10:31:15 - INFO - Creating VLAN 100 (LAB_NETWORK)...
2025-11-02 10:31:16 - INFO - Saving configuration...
2025-11-02 10:31:17 - INFO - VLAN 100 (LAB_NETWORK) berhasil dibuat!

SUCCESS: VLAN 100 berhasil dibuat!

Tekan Enter untuk melanjutkan...
```

### Contoh Operasi READ (Menu 2):
```
Pilih menu (1-6): 2

--- READ VLAN ---
Masukkan VLAN ID yang ingin dilihat: 100

2025-11-02 10:32:10 - INFO - Verifying VLAN 100...

============================================================
VLAN Name                             Status    Ports
---- -------------------------------- --------- -----------
100  LAB_NETWORK                      active
============================================================

Tekan Enter untuk melanjutkan...
```

### Contoh Operasi UPDATE (Menu 3):
```
Pilih menu (1-6): 3

--- UPDATE VLAN ---
Masukkan VLAN ID yang ingin diupdate: 100

2025-11-02 10:33:05 - INFO - Verifying VLAN 100...

VLAN 100 ditemukan.
Masukkan nama VLAN baru: PRODUCTION_NETWORK

2025-11-02 10:33:20 - INFO - Updating VLAN 100 with new name: PRODUCTION_NETWORK...
2025-11-02 10:33:21 - INFO - Saving configuration...
2025-11-02 10:33:22 - INFO - VLAN 100 berhasil diupdate!

SUCCESS: VLAN 100 berhasil diupdate dengan nama 'PRODUCTION_NETWORK'

Tekan Enter untuk melanjutkan...
```

### Contoh Operasi DELETE (Menu 4):
```
Pilih menu (1-6): 4

--- DELETE VLAN ---
Masukkan VLAN ID yang ingin dihapus: 100

2025-11-02 10:34:05 - INFO - Verifying VLAN 100...

Apakah Anda yakin ingin menghapus VLAN 100? (yes/no): yes

2025-11-02 10:34:15 - INFO - Deleting VLAN 100...
2025-11-02 10:34:16 - INFO - Saving configuration...
2025-11-02 10:34:17 - INFO - VLAN 100 berhasil dihapus!

SUCCESS: VLAN 100 berhasil dihapus!

Tekan Enter untuk melanjutkan...
```

### Contoh Operasi SHOW ALL (Menu 5):
```
Pilih menu (1-6): 5

--- SHOW ALL VLANs ---
2025-11-02 10:35:10 - INFO - Retrieving all VLANs...

============================================================
VLAN Name                             Status    Ports
---- -------------------------------- --------- -----------
1    default                          active    Eth1/1, Eth1/2
10   MANAGEMENT                       active
20   GUEST_NETWORK                    active    Eth1/3
100  PRODUCTION_NETWORK               active
200  DEVELOPMENT                      active
============================================================

2025-11-02 10:35:11 - INFO - Berhasil menampilkan semua VLAN

Tekan Enter untuk melanjutkan...
```

### Contoh EXIT (Menu 6):
```
Pilih menu (1-6): 6

Terima kasih telah menggunakan VLAN Management System!
2025-11-02 10:36:00 - INFO - Program dihentikan oleh user
2025-11-02 10:36:00 - INFO - Disconnected
```

## ⚠️ Troubleshooting

### Problem: Connection Timeout
**Error:** `Connection timeout to sbx-nxos-mgmt.cisco.com`

**Solusi:**
- Periksa koneksi internet
- Pastikan IP/hostname benar
- Periksa firewall

### Problem: Authentication Failed
**Error:** `Authentication failed - check credentials`

**Solusi:**
- Periksa username dan password
- Pastikan user memiliki privilege yang cukup

### Problem: Invalid VLAN ID
**Error:** `Invalid VLAN ID: 5000. Must be between 1-4094`

**Solusi:**
- Gunakan VLAN ID yang valid (1-4094)
- VLAN 1 adalah default VLAN

## 🔐 Catatan Keamanan

⚠️ **PENTING:** Jangan simpan password langsung di code untuk production!

**Best Practices:**
1. Gunakan environment variables:
   ```python
   import os
   password = os.getenv('DEVICE_PASSWORD')
   ```

2. Gunakan file konfigurasi terpisah (jangan commit ke git):
   ```python
   import json
   with open('config.json') as f:
       config = json.load(f)
   ```

3. Gunakan vault seperti HashiCorp Vault atau AWS Secrets Manager

## 📚 Referensi & Sumber Belajar

- [Netmiko Documentation](https://github.com/ktbyers/netmiko)
- [Cisco NX-OS Command Reference](https://www.cisco.com/c/en/us/support/switches/nexus-9000-series-switches/products-command-reference-list.html)
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [Python Context Managers](https://docs.python.org/3/reference/datamodel.html#context-managers)

## 👨‍🏫 Tugas untuk Mahasiswa

### Level 1 - Pemula (Praktik Dasar):
1. **Jalankan Program**
   - Jalankan script dan coba semua menu (1-6)
   - Buat minimal 3 VLAN berbeda
   - Screenshot hasil output

2. **Eksperimen Error Handling**
   - Coba buat VLAN dengan ID invalid (misalnya: 5000, -1, atau "abc")
   - Coba delete VLAN 1 (default VLAN)
   - Coba read VLAN yang tidak ada
   - Dokumentasikan error message yang muncul

3. **Modifikasi Sederhana**
   - Ubah device_config untuk menambah timeout menjadi 60 detik
   - Tambahkan VLAN ID favorit Anda di komentar code
   - Ganti bahasa pesan sukses dari Indonesia ke Inggris

4. **Pemahaman Code**
   - Jelaskan dengan kata-kata sendiri apa itu Context Manager
   - Tuliskan perbedaan antara `send_command()` dan `send_config_set()`
   - Identifikasi 5 error yang mungkin terjadi dan cara handle-nya

---

### Level 2 - Menengah (Pengembangan Fitur):
1. **Tambah Validasi**
   - Tambahkan validasi bahwa VLAN name tidak boleh lebih dari 32 karakter
   - Tambahkan validasi bahwa VLAN name tidak boleh mengandung spasi
   - Tambahkan pengecekan VLAN sudah exist sebelum create

2. **Export Data**
   - Tambahkan menu untuk export semua VLAN ke file CSV
   - Format: VLAN_ID, VLAN_Name, Status
   - Contoh: `100,LAB_NETWORK,active`

3. **Bulk Operations**
   - Buat fungsi untuk import VLAN dari file CSV
   - Format file: setiap baris berisi `vlan_id,vlan_name`
   - Create semua VLAN dari file sekaligus

4. **Statistics**
   - Tambahkan menu untuk menampilkan:
     - Total jumlah VLAN yang ada
     - List VLAN IDs yang sudah terpakai
     - Range VLAN ID yang masih kosong

5. **Logging ke File**
   - Modifikasi logging agar output juga ke file `vlan_operations.log`
   - Format: timestamp, operation, vlan_id, status

---

### Level 3 - Advanced (Project Besar):
1. **Multiple Device Support**
   - Buat file `devices.json` berisi list devices
   - Tambahkan menu untuk pilih device mana yang akan dikelola
   - Implementasi koneksi ke multiple switches

2. **Assign VLAN ke Interface**
   - Tambahkan menu baru: "Assign VLAN to Interface"
   - Input: Interface name (misalnya: Ethernet1/1) dan VLAN ID
   - Command yang dikirim:
     ```
     interface Ethernet1/1
     switchport mode access
     switchport access vlan 100
     ```

3. **Backup & Restore**
   - **Backup**: Save semua VLAN config ke file JSON
   - **Restore**: Baca file JSON dan create semua VLAN
   - Tambahkan timestamp pada nama file backup

4. **Web Interface**
   - Gunakan Flask untuk membuat web interface
   - Halaman web dengan form untuk CRUD operations
   - Tampilkan tabel VLANs dengan Bootstrap

5. **Database Integration**
   - Simpan history semua operasi VLAN ke SQLite database
   - Tabel: operations (id, timestamp, operation_type, vlan_id, vlan_name, user, status)
   - Buat query untuk:
     - History 10 operasi terakhir
     - Total CREATE, UPDATE, DELETE per hari
     - VLANs yang paling sering dimodifikasi

6. **Error Recovery**
   - Implementasi retry mechanism untuk koneksi timeout
   - Maksimal 3x retry dengan delay 5 detik
   - Log setiap retry attempt

---

### Bonus Challenge 🏆:
1. **Real-time Monitoring**
   - Gunakan threading untuk monitoring VLAN changes setiap 30 detik
   - Alert jika ada VLAN baru atau dihapus
   - Simpan changes ke log file

2. **Security Enhancement**
   - Pindahkan credentials ke environment variables
   - Gunakan `python-dotenv` untuk load dari file `.env`
   - File `.env`:
     ```
     DEVICE_HOST=sbx-nxos-mgmt.cisco.com
     DEVICE_USERNAME=admin
     DEVICE_PASSWORD=Admin_1234!
     ```

3. **Unit Testing**
   - Buat file `test_vlan_management.py`
   - Test setiap function di NetworkDevice class
   - Gunakan `unittest` atau `pytest`
   - Mock koneksi ke device untuk testing

4. **GUI Application**
   - Buat GUI dengan Tkinter atau PyQt5
   - Window dengan:
     - Tabel untuk display VLANs
     - Form untuk Create/Update
     - Buttons untuk setiap operasi
     - Status bar untuk messages

5. **API Development**
   - Buat REST API dengan FastAPI
   - Endpoints:
     - `GET /vlans` - List all VLANs
     - `GET /vlans/{id}` - Get specific VLAN
     - `POST /vlans` - Create VLAN
     - `PUT /vlans/{id}` - Update VLAN
     - `DELETE /vlans/{id}` - Delete VLAN
   - Deploy ke Heroku atau AWS

---

### Kriteria Penilaian:
- **Level 1**: Nilai C - Understanding basic concepts
- **Level 2**: Nilai B - Can develop features
- **Level 3**: Nilai A - Mastery of advanced concepts
- **Bonus Challenge**: Nilai A+ - Exceptional work

### Submission Guidelines:
1. Upload code ke GitHub repository
2. Include README.md dengan:
   - Deskripsi perubahan yang dibuat
   - Screenshot hasil
   - Cara menjalankan code
3. Create demo video (5-10 menit)
4. Document challenges dan solutions

## 📞 Kontak & Support

Jika ada pertanyaan mengenai code ini, silakan hubungi dosen pengampu atau diskusikan di forum kelas.

## 📝 License

Script ini dibuat untuk keperluan edukasi.

---

**Selamat Belajar! 🎓**

*"Automation is not about replacing humans, it's about empowering them."*
