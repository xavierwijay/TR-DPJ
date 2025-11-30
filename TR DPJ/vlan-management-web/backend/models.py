"""
Database models for VLAN Management System
"""
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()


class User(db.Model):
    """User model for tracking who creates/manages VLANs"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    nim = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vlans = db.relationship('VlanConfig', backref='user', lazy=True, cascade='all, delete-orphan')
    sessions = db.relationship('UserSession', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'nim': self.nim,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'total_vlans': len(self.vlans)
        }
    
    def __repr__(self):
        return f'<User {self.name} ({self.nim})>'


class VlanConfig(db.Model):
    """VLAN configuration model"""
    __tablename__ = 'vlan_configs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vlan_id = db.Column(db.Integer, nullable=False)
    vlan_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    
    # User who created this VLAN
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Subnet configuration (for bonus feature)
    subnet_mask = db.Column(db.String(18), default='255.255.255.0')
    max_hosts = db.Column(db.Integer, nullable=True)  # Max number of hosts allowed in this VLAN
    host_count = db.Column(db.Integer, default=0)  # Current host count
    
    # Status and timestamps
    status = db.Column(db.String(20), default='active')  # active, inactive, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Auto-delete feature (bonus)
    expires_at = db.Column(db.DateTime, nullable=True)  # When VLAN will auto-delete
    auto_delete = db.Column(db.Boolean, default=False)
    
    # Cisco device info
    device_synced = db.Column(db.Boolean, default=False)
    sync_timestamp = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'vlan_id': self.vlan_id,
            'vlan_name': self.vlan_name,
            'description': self.description,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'user_nim': self.user.nim if self.user else None,
            'subnet_mask': self.subnet_mask,
            'max_hosts': self.max_hosts,
            'host_count': self.host_count,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'auto_delete': self.auto_delete,
            'device_synced': self.device_synced,
            'sync_timestamp': self.sync_timestamp.isoformat() if self.sync_timestamp else None
        }
    
    def is_expired(self):
        """Check if VLAN has expired"""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True
        return False
    
    def can_add_hosts(self, count=1):
        """Check if can add more hosts (bonus feature)"""
        if self.max_hosts is None:
            return True
        return (self.host_count + count) <= self.max_hosts
    
    def __repr__(self):
        return f'<VLAN {self.vlan_id} - {self.vlan_name}>'


class UserSession(db.Model):
    """Track user sessions for auto-cleanup"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def is_active(self):
        """Check if session is still active"""
        return datetime.utcnow() < self.expires_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_active': self.is_active()
        }
    
    def __repr__(self):
        return f'<Session {self.id[:8]}...>'


class ActivityLog(db.Model):
    """Log all VLAN management activities"""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    vlan_id = db.Column(db.String(36), db.ForeignKey('vlan_configs.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)  # CREATE, READ, UPDATE, DELETE, LOGIN, LOGOUT
    details = db.Column(db.Text)
    status = db.Column(db.String(20))  # SUCCESS, FAILED
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'vlan_id': self.vlan_id,
            'action': self.action,
            'details': self.details,
            'status': self.status,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<ActivityLog {self.action} at {self.created_at}>'
