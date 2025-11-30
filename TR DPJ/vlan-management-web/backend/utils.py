"""
Utility functions for VLAN Management System
"""
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from typing import Callable, Dict, Tuple

logger = logging.getLogger(__name__)


def validate_vlan_id(vlan_id) -> Tuple[bool, str]:
    """
    Validate VLAN ID
    
    Args:
        vlan_id: VLAN ID to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    try:
        vlan_num = int(vlan_id)
        if not (1 <= vlan_num <= 4094):
            return False, f"VLAN ID must be between 1-4094, got {vlan_num}"
        if vlan_num == 1:
            return False, "VLAN 1 is reserved (default VLAN)"
        return True, "Valid"
    except ValueError:
        return False, f"VLAN ID must be numeric"


def validate_vlan_name(vlan_name: str) -> Tuple[bool, str]:
    """
    Validate VLAN name
    
    Args:
        vlan_name: VLAN name to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    if not vlan_name or len(vlan_name) == 0:
        return False, "VLAN name cannot be empty"
    
    if len(vlan_name) > 32:
        return False, "VLAN name cannot exceed 32 characters"
    
    # Check for invalid characters (spaces are allowed in newer IOS versions)
    invalid_chars = ['?', '"', "'"]
    for char in invalid_chars:
        if char in vlan_name:
            return False, f"VLAN name contains invalid character: {char}"
    
    return True, "Valid"


def validate_subnet_mask(subnet_mask: str) -> Tuple[bool, str]:
    """
    Validate subnet mask format
    
    Args:
        subnet_mask: Subnet mask to validate (e.g., 255.255.255.0)
        
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    try:
        octets = subnet_mask.split('.')
        if len(octets) != 4:
            return False, "Invalid subnet mask format"
        
        for octet in octets:
            num = int(octet)
            if not (0 <= num <= 255):
                return False, "Octet must be between 0-255"
        
        return True, "Valid"
    except:
        return False, "Invalid subnet mask format"


def calculate_max_hosts(subnet_mask: str) -> int:
    """
    Calculate maximum hosts from subnet mask
    
    Args:
        subnet_mask: Subnet mask (e.g., 255.255.255.0)
        
    Returns:
        int: Maximum number of usable hosts
    """
    octets = [int(x) for x in subnet_mask.split('.')]
    binary = ''.join([f'{oct:08b}' for oct in octets])
    ones = binary.count('1')
    zeros = 32 - ones
    
    # Formula: 2^zeros - 2 (minus network and broadcast addresses)
    if zeros >= 2:
        return (2 ** zeros) - 2
    return 0


def require_api_key(f: Callable) -> Callable:
    """
    Decorator to require API key for API endpoints
    
    Usage:
        @app.route('/api/vlans')
        @require_api_key
        def get_vlans():
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Validate API key (implement your own logic)
        if not validate_api_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key
    
    Args:
        api_key: API key to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Implement your API key validation logic
    # For now, just check if it's not empty
    return len(api_key) > 0


def get_client_ip() -> str:
    """
    Get client IP address from request
    
    Returns:
        str: Client IP address
    """
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ.get('HTTP_X_FORWARDED_FOR').split(',')[0]
    return request.remote_addr


def format_error_response(error: str, details: str = None) -> Dict:
    """
    Format error response
    
    Args:
        error: Error message
        details: Detailed error information
        
    Returns:
        Dict: Formatted error response
    """
    response = {
        'success': False,
        'error': error,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if details:
        response['details'] = details
    
    return response


def format_success_response(data: Dict = None, message: str = None) -> Dict:
    """
    Format success response
    
    Args:
        data: Response data
        message: Success message
        
    Returns:
        Dict: Formatted success response
    """
    response = {
        'success': True,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if data:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    return response


def parse_vlan_output(output: str) -> Dict:
    """
    Parse VLAN output from Cisco device
    
    Args:
        output: Raw VLAN output from device
        
    Returns:
        Dict: Parsed VLAN information
    """
    lines = output.strip().split('\n')
    vlans = {}
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('VLAN') or line.startswith('----'):
            continue
        
        parts = line.split()
        if len(parts) >= 2:
            try:
                vlan_id = int(parts[0])
                vlan_name = parts[1] if len(parts) > 1 else 'unknown'
                status = parts[2] if len(parts) > 2 else 'unknown'
                
                vlans[vlan_id] = {
                    'vlan_id': vlan_id,
                    'vlan_name': vlan_name,
                    'status': status
                }
            except ValueError:
                continue
    
    return vlans


def is_session_expired(last_activity: datetime, timeout_minutes: int) -> bool:
    """
    Check if session has expired
    
    Args:
        last_activity: Last activity timestamp
        timeout_minutes: Session timeout in minutes
        
    Returns:
        bool: True if expired, False otherwise
    """
    expiry_time = last_activity + timedelta(minutes=timeout_minutes)
    return datetime.utcnow() > expiry_time


def cleanup_expired_sessions(app, timeout_minutes: int = 30):
    """
    Cleanup expired sessions (background task)
    
    Args:
        app: Flask app instance
        timeout_minutes: Session timeout in minutes
    """
    from models import db, UserSession
    
    with app.app_context():
        expired_sessions = UserSession.query.filter(
            UserSession.expires_at < datetime.utcnow()
        ).all()
        
        for session in expired_sessions:
            logger.info(f"Removing expired session: {session.id}")
            db.session.delete(session)
        
        db.session.commit()
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")


def cleanup_expired_vlans(app):
    """
    Cleanup expired VLANs (background task - bonus feature)
    
    Args:
        app: Flask app instance
    """
    from models import db, VlanConfig
    
    with app.app_context():
        expired_vlans = VlanConfig.query.filter(
            VlanConfig.auto_delete == True,
            VlanConfig.expires_at < datetime.utcnow(),
            VlanConfig.status == 'active'
        ).all()
        
        for vlan in expired_vlans:
            logger.info(f"Marking VLAN {vlan.vlan_id} as expired")
            vlan.status = 'expired'
            db.session.commit()
        
        logger.info(f"Marked {len(expired_vlans)} VLANs as expired")
