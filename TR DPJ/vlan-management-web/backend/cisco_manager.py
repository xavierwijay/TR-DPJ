"""
Cisco Device Management Module
Handles all communication with Cisco NX-OS devices
"""
import logging
from typing import Optional, Dict, List, Tuple
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

logger = logging.getLogger(__name__)


class CiscoDeviceManager:
    """Manager untuk handling koneksi dan operasi Cisco devices"""
    
    def __init__(self, device_config: Dict):
        """
        Initialize Cisco device manager
        
        Args:
            device_config: Dictionary dengan konfigurasi device
                {
                    'device_type': 'cisco_nxos',
                    'host': 'ip_address',
                    'username': 'admin',
                    'password': 'password',
                    'port': 22,
                    'timeout': 30
                }
        """
        self.device_config = device_config
        self.connection = None
    
    def connect(self) -> Tuple[bool, str]:
        """
        Establish SSH connection to device
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            logger.info(f"Connecting to {self.device_config['host']}...")
            self.connection = ConnectHandler(**self.device_config)
            logger.info("Connected successfully!")
            return True, "Connected successfully"
        except NetmikoTimeoutException as e:
            msg = f"Connection timeout to {self.device_config['host']}"
            logger.error(msg)
            return False, msg
        except NetmikoAuthenticationException as e:
            msg = "Authentication failed - check credentials"
            logger.error(msg)
            return False, msg
        except Exception as e:
            msg = f"Connection error: {str(e)}"
            logger.error(msg)
            return False, msg
    
    def disconnect(self):
        """Disconnect from device"""
        if self.connection:
            try:
                self.connection.disconnect()
                logger.info("Disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
    
    def is_connected(self) -> bool:
        """Check if device is connected"""
        return self.connection is not None
    
    def create_vlan(self, vlan_id: int, vlan_name: str) -> Tuple[bool, str]:
        """
        Create VLAN on device
        
        Args:
            vlan_id: VLAN ID (1-4094)
            vlan_name: VLAN name
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not self.connection:
            return False, "Not connected to device"
        
        # Validasi VLAN ID
        try:
            vlan_num = int(vlan_id)
            if not (1 <= vlan_num <= 4094):
                msg = f"Invalid VLAN ID: {vlan_id}. Must be between 1-4094"
                logger.error(msg)
                return False, msg
        except ValueError:
            msg = f"VLAN ID must be numeric: {vlan_id}"
            logger.error(msg)
            return False, msg
        
        try:
            commands = [
                f"vlan {vlan_id}",
                f"name {vlan_name}"
            ]
            
            logger.info(f"Creating VLAN {vlan_id} ({vlan_name})...")
            output = self.connection.send_config_set(commands)
            
            # Save configuration
            logger.info("Saving configuration...")
            save_output = self.connection.save_config()
            
            msg = f"VLAN {vlan_id} created successfully"
            logger.info(msg)
            return True, msg
            
        except Exception as e:
            msg = f"Failed to create VLAN: {str(e)}"
            logger.error(msg)
            return False, msg
    
    def verify_vlan(self, vlan_id: int) -> Tuple[bool, Optional[str]]:
        """
        Verify VLAN exists on device
        
        Args:
            vlan_id: VLAN ID to verify
            
        Returns:
            Tuple[bool, Optional[str]]: (exists, vlan_info)
        """
        if not self.connection:
            return False, None
        
        try:
            logger.info(f"Verifying VLAN {vlan_id}...")
            output = self.connection.send_command(f"show vlan id {vlan_id}")
            
            if "not found" in output.lower() or "invalid" in output.lower():
                logger.warning(f"VLAN {vlan_id} not found")
                return False, None
            
            return True, output
            
        except Exception as e:
            logger.error(f"Failed to verify VLAN: {e}")
            return False, None
    
    def get_all_vlans(self) -> Tuple[bool, Optional[str]]:
        """
        Get all VLANs from device
        
        Returns:
            Tuple[bool, Optional[str]]: (success, vlan_info)
        """
        if not self.connection:
            return False, None
        
        try:
            logger.info("Retrieving all VLANs...")
            output = self.connection.send_command("show vlan brief")
            return True, output
            
        except Exception as e:
            logger.error(f"Failed to retrieve VLANs: {e}")
            return False, None
    
    def update_vlan(self, vlan_id: int, new_vlan_name: str) -> Tuple[bool, str]:
        """
        Update VLAN name
        
        Args:
            vlan_id: VLAN ID to update
            new_vlan_name: New VLAN name
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not self.connection:
            return False, "Not connected to device"
        
        try:
            commands = [
                f"vlan {vlan_id}",
                f"name {new_vlan_name}"
            ]
            
            logger.info(f"Updating VLAN {vlan_id}...")
            output = self.connection.send_config_set(commands)
            
            # Save configuration
            logger.info("Saving configuration...")
            save_output = self.connection.save_config()
            
            msg = f"VLAN {vlan_id} updated successfully"
            logger.info(msg)
            return True, msg
            
        except Exception as e:
            msg = f"Failed to update VLAN: {str(e)}"
            logger.error(msg)
            return False, msg
    
    def delete_vlan(self, vlan_id: int) -> Tuple[bool, str]:
        """
        Delete VLAN from device
        
        Args:
            vlan_id: VLAN ID to delete
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not self.connection:
            return False, "Not connected to device"
        
        # Prevent deletion of default VLAN
        if vlan_id == 1:
            msg = "Cannot delete default VLAN 1"
            logger.error(msg)
            return False, msg
        
        try:
            command = f"no vlan {vlan_id}"
            
            logger.info(f"Deleting VLAN {vlan_id}...")
            output = self.connection.send_config_set(command)
            
            # Save configuration
            logger.info("Saving configuration...")
            save_output = self.connection.save_config()
            
            msg = f"VLAN {vlan_id} deleted successfully"
            logger.info(msg)
            return True, msg
            
        except Exception as e:
            msg = f"Failed to delete VLAN: {str(e)}"
            logger.error(msg)
            return False, msg
    
    def get_device_info(self) -> Tuple[bool, Optional[Dict]]:
        """
        Get device information
        
        Returns:
            Tuple[bool, Optional[Dict]]: (success, device_info)
        """
        if not self.connection:
            return False, None
        
        try:
            logger.info("Getting device information...")
            output = self.connection.send_command("show version")
            
            # Parse device info
            info = {
                'version_output': output,
                'connected': True,
                'device_type': self.device_config.get('device_type'),
                'host': self.device_config.get('host')
            }
            
            return True, info
            
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            return False, None


def get_cisco_manager(config: Dict) -> CiscoDeviceManager:
    """
    Factory function to create CiscoDeviceManager instance
    
    Args:
        config: Device configuration dictionary
        
    Returns:
        CiscoDeviceManager instance
    """
    return CiscoDeviceManager(config)
