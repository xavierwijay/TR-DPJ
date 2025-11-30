"""
Network Automation Script - VLAN Management
Manages VLAN creation on Cisco NX-OS devices using Netmiko
"""
import logging
from typing import Optional
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NetworkDevice:
    """Handles network device connections and operations"""
    
    def __init__(self, device_config: dict):
        """Initialize with device configuration"""
        self.device_config = device_config
        self.connection: Optional[ConnectHandler] = None
    
    def __enter__(self):
        """Context manager entry - establish connection"""
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
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection"""
        if self.connection:
            self.connection.disconnect()
            logger.info("Disconnected")
    
    def create_vlan(self, vlan_id: str, vlan_name: str) -> bool:
        """
        Create a VLAN on the device
        
        Args:
            vlan_id: VLAN ID (1-4094)
            vlan_name: VLAN name
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connection:
            logger.error("No active connection")
            return False
        
        # Validate VLAN ID
        try:
            vlan_num = int(vlan_id)
            if not (1 <= vlan_num <= 4094):
                logger.error(f"Invalid VLAN ID: {vlan_id}. Must be between 1-4094")
                return False
        except ValueError:
            logger.error(f"VLAN ID must be numeric: {vlan_id}")
            return False
        
        try:
            commands = [
                f"vlan {vlan_id}",
                f"name {vlan_name}"
            ]
            
            logger.info(f"Creating VLAN {vlan_id} ({vlan_name})...")
            output = self.connection.send_config_set(commands)
            logger.debug(f"Configuration output:\n{output}")
            
            # Save configuration
            logger.info("Saving configuration...")
            self.connection.save_config()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create VLAN: {e}")
            return False
    
    def verify_vlan(self, vlan_id: str) -> Optional[str]:
        """
        Verify VLAN exists on device
        
        Args:
            vlan_id: VLAN ID to verify
            
        Returns:
            str: VLAN information or None if not found
        """
        if not self.connection:
            logger.error("No active connection")
            return None
        
        try:
            logger.info(f"Verifying VLAN {vlan_id}...")
            output = self.connection.send_command(f"show vlan id {vlan_id}")
            
            if "not found" in output.lower() or "invalid" in output.lower():
                logger.warning(f"VLAN {vlan_id} not found")
                return None
            
            return output
            
        except Exception as e:
            logger.error(f"Failed to verify VLAN: {e}")
            return None
    
    def show_all_vlans(self) -> Optional[str]:
        """
        Display all VLANs configured on the device
        
        Returns:
            str: All VLAN information or None if failed
        """
        if not self.connection:
            logger.error("No active connection")
            return None
        
        try:
            logger.info("Retrieving all VLANs...")
            output = self.connection.send_command("show vlan brief")
            return output
            
        except Exception as e:
            logger.error(f"Failed to retrieve VLANs: {e}")
            return None
    
    def update_vlan(self, vlan_id: str, new_vlan_name: str) -> bool:
        """
        Update VLAN name
        
        Args:
            vlan_id: VLAN ID to update
            new_vlan_name: New VLAN name
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connection:
            logger.error("No active connection")
            return False
        
        try:
            commands = [
                f"vlan {vlan_id}",
                f"name {new_vlan_name}"
            ]
            
            logger.info(f"Updating VLAN {vlan_id} with new name: {new_vlan_name}...")
            output = self.connection.send_config_set(commands)
            logger.debug(f"Configuration output:\n{output}")
            
            # Save configuration
            logger.info("Saving configuration...")
            self.connection.save_config()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update VLAN: {e}")
            return False
    
    def delete_vlan(self, vlan_id: str) -> bool:
        """
        Delete a VLAN from the device
        
        Args:
            vlan_id: VLAN ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connection:
            logger.error("No active connection")
            return False
        
        # Prevent deletion of default VLAN
        if vlan_id == "1":
            logger.error("Cannot delete default VLAN 1")
            return False
        
        try:
            command = f"no vlan {vlan_id}"
            
            logger.info(f"Deleting VLAN {vlan_id}...")
            output = self.connection.send_config_set(command)
            logger.debug(f"Configuration output:\n{output}")
            
            # Save configuration
            logger.info("Saving configuration...")
            self.connection.save_config()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete VLAN: {e}")
            return False


def display_menu():
    """Display CRUD menu options"""
    print("\n" + "="*60)
    print("           VLAN MANAGEMENT SYSTEM - CRUD MENU")
    print("="*60)
    print("1. Create VLAN       - Buat VLAN baru")
    print("2. Read VLAN         - Lihat VLAN tertentu")
    print("3. Update VLAN       - Update nama VLAN")
    print("4. Delete VLAN       - Hapus VLAN")
    print("5. Show All VLANs    - Tampilkan semua VLAN")
    print("6. Exit              - Keluar dari program")
    print("="*60)


def get_user_input(prompt: str) -> str:
    """Get and validate user input"""
    while True:
        user_input = input(prompt).strip()
        if user_input:
            return user_input
        print("Input tidak boleh kosong. Silakan coba lagi.")


def menu_create_vlan(device: NetworkDevice):
    """Menu option 1: Create VLAN"""
    print("\n--- CREATE VLAN ---")
    vlan_id = get_user_input("Masukkan VLAN ID (1-4094): ")
    vlan_name = get_user_input("Masukkan VLAN Name: ")
    
    if device.create_vlan(vlan_id, vlan_name):
        logger.info(f"VLAN {vlan_id} ({vlan_name}) berhasil dibuat!")
        print(f"\nSUCCESS: VLAN {vlan_id} berhasil dibuat!")
    else:
        print("\nERROR: Gagal membuat VLAN")


def menu_read_vlan(device: NetworkDevice):
    """Menu option 2: Read/View specific VLAN"""
    print("\n--- READ VLAN ---")
    vlan_id = get_user_input("Masukkan VLAN ID yang ingin dilihat: ")
    
    vlan_info = device.verify_vlan(vlan_id)
    if vlan_info:
        print("\n" + "="*60)
        print(vlan_info)
        print("="*60)
    else:
        print(f"\nERROR: VLAN {vlan_id} tidak ditemukan")


def menu_update_vlan(device: NetworkDevice):
    """Menu option 3: Update VLAN name"""
    print("\n--- UPDATE VLAN ---")
    vlan_id = get_user_input("Masukkan VLAN ID yang ingin diupdate: ")
    
    # Check if VLAN exists first
    vlan_info = device.verify_vlan(vlan_id)
    if not vlan_info:
        print(f"\nERROR: VLAN {vlan_id} tidak ditemukan")
        return
    
    print(f"\nVLAN {vlan_id} ditemukan.")
    new_vlan_name = get_user_input("Masukkan nama VLAN baru: ")
    
    if device.update_vlan(vlan_id, new_vlan_name):
        logger.info(f"VLAN {vlan_id} berhasil diupdate!")
        print(f"\nSUCCESS: VLAN {vlan_id} berhasil diupdate dengan nama '{new_vlan_name}'")
    else:
        print("\nERROR: Gagal mengupdate VLAN")


def menu_delete_vlan(device: NetworkDevice):
    """Menu option 4: Delete VLAN"""
    print("\n--- DELETE VLAN ---")
    vlan_id = get_user_input("Masukkan VLAN ID yang ingin dihapus: ")
    
    # Check if VLAN exists first
    vlan_info = device.verify_vlan(vlan_id)
    if not vlan_info:
        print(f"\nERROR: VLAN {vlan_id} tidak ditemukan")
        return
    
    # Confirmation
    confirm = input(f"\nApakah Anda yakin ingin menghapus VLAN {vlan_id}? (yes/no): ").strip().lower()
    if confirm in ['yes', 'y']:
        if device.delete_vlan(vlan_id):
            logger.info(f"VLAN {vlan_id} berhasil dihapus!")
            print(f"\nSUCCESS: VLAN {vlan_id} berhasil dihapus!")
        else:
            print("\nERROR: Gagal menghapus VLAN")
    else:
        print("\nPenghapusan VLAN dibatalkan.")


def menu_show_all_vlans(device: NetworkDevice):
    """Menu option 5: Show all VLANs"""
    print("\n--- SHOW ALL VLANs ---")
    all_vlans = device.show_all_vlans()
    if all_vlans:
        print("\n" + "="*60)
        print(all_vlans)
        print("="*60)
        logger.info("Berhasil menampilkan semua VLAN")
    else:
        print("\nERROR: Gagal mengambil data VLAN")


def main():
    """Main execution function with CRUD menu"""
    
    # Device configuration
    # TODO: Move credentials to environment variables or secure vault
    device_config = {
        "device_type": "cisco_nxos",
        "host": "sbx-nxos-mgmt.cisco.com",
        "username": "admin",
        "password": "Admin_1234!",
        "port": 22,
        "timeout": 30,
        "session_log": "session.log",  # Optional: log all session output
    }
    
    try:
        # Use context manager for automatic connection handling
        with NetworkDevice(device_config) as device:
            while True:
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
                    print("\nTerima kasih telah menggunakan VLAN Management System!")
                    logger.info("Program dihentikan oleh user")
                    break
                else:
                    print("\nPilihan tidak valid! Silakan pilih 1-6.")
                
                # Pause before showing menu again
                input("\nTekan Enter untuk melanjutkan...")
                
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        print("\n\nProgram dihentikan oleh user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\nERROR: {e}")
        raise


if __name__ == "__main__":
    main()
