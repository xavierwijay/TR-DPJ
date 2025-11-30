"""
Flask Application for VLAN Management System
Main application entry point
"""
import logging
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

from config import config
from models import db, User, VlanConfig, UserSession, ActivityLog
from cisco_manager import get_cisco_manager
from utils import (
    validate_vlan_id, validate_vlan_name, validate_subnet_mask,
    calculate_max_hosts, get_client_ip, format_error_response,
    format_success_response, is_session_expired, cleanup_expired_sessions,
    cleanup_expired_vlans
)

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name: str = None) -> Flask:
    """
    Application factory function
    
    Args:
        config_name: Configuration name (development, testing, production)
        
    Returns:
        Flask app instance
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize database
    db.init_app(app)
    
    # Enable CORS
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['*']))
    
    # Register blueprints and routes
    register_routes(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created/verified")
    
    return app


def register_routes(app: Flask):
    """Register all routes and blueprints"""
    
    # ==================== WEB ROUTES ====================
    
    @app.route('/')
    def index():
        """Home page"""
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard page"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return render_template('dashboard.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page"""
        if request.method == 'POST':
            data = request.get_json()
            nim = data.get('nim')
            name = data.get('name')
            email = data.get('email')
            
            if not nim or not name or not email:
                return jsonify(format_error_response('Missing required fields')), 400
            
            # Find or create user
            user = User.query.filter_by(nim=nim).first()
            if not user:
                user = User(name=name, nim=nim, email=email)
                db.session.add(user)
                db.session.commit()
                logger.info(f"New user registered: {name} ({nim})")
            
            # Create session
            session_token = os.urandom(32).hex()
            expires_at = datetime.utcnow() + timedelta(hours=2)
            
            user_session = UserSession(
                user_id=user.id,
                session_token=session_token,
                ip_address=get_client_ip(),
                user_agent=request.headers.get('User-Agent'),
                expires_at=expires_at
            )
            db.session.add(user_session)
            db.session.commit()
            
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_nim'] = user.nim
            session['session_token'] = session_token
            
            # Log activity
            log_activity(user.id, 'LOGIN', 'User logged in', 'SUCCESS')
            
            return jsonify(format_success_response(
                data=user.to_dict(),
                message='Login successful'
            )), 200
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        """Logout"""
        if 'user_id' in session:
            log_activity(session['user_id'], 'LOGOUT', 'User logged out', 'SUCCESS')
        session.clear()
        return redirect(url_for('index'))
    
    @app.route('/profile')
    def profile():
        """User profile page"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return render_template('profile.html')
    
    # ==================== API ROUTES - USERS ====================
    
    @app.route('/api/users', methods=['GET'])
    def get_users():
        """Get all users"""
        try:
            users = User.query.all()
            return jsonify(format_success_response(
                data=[user.to_dict() for user in users]
            )), 200
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return jsonify(format_error_response('Failed to get users', str(e))), 500
    
    @app.route('/api/users/<user_id>', methods=['GET'])
    def get_user(user_id):
        """Get specific user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify(format_error_response('User not found')), 404
            
            return jsonify(format_success_response(data=user.to_dict())), 200
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return jsonify(format_error_response('Failed to get user', str(e))), 500
    
    @app.route('/api/users/profile', methods=['GET'])
    def get_current_user_profile():
        """Get current user profile"""
        if 'user_id' not in session:
            return jsonify(format_error_response('Not authenticated')), 401
        
        try:
            user = User.query.get(session['user_id'])
            if not user:
                return jsonify(format_error_response('User not found')), 404
            
            user_data = user.to_dict()
            user_data['vlans'] = [vlan.to_dict() for vlan in user.vlans]
            
            return jsonify(format_success_response(data=user_data)), 200
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return jsonify(format_error_response('Failed to get profile', str(e))), 500
    
    # ==================== API ROUTES - VLANs ====================
    
    @app.route('/api/vlans', methods=['GET'])
    def get_all_vlans():
        """Get all VLANs"""
        try:
            vlans = VlanConfig.query.all()
            return jsonify(format_success_response(
                data=[vlan.to_dict() for vlan in vlans]
            )), 200
        except Exception as e:
            logger.error(f"Error getting VLANs: {e}")
            return jsonify(format_error_response('Failed to get VLANs', str(e))), 500
    
    @app.route('/api/vlans/user/<user_id>', methods=['GET'])
    def get_user_vlans(user_id):
        """Get VLANs for specific user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify(format_error_response('User not found')), 404
            
            vlans = VlanConfig.query.filter_by(user_id=user_id).all()
            return jsonify(format_success_response(
                data=[vlan.to_dict() for vlan in vlans]
            )), 200
        except Exception as e:
            logger.error(f"Error getting user VLANs: {e}")
            return jsonify(format_error_response('Failed to get VLANs', str(e))), 500
    
    @app.route('/api/vlans', methods=['POST'])
    def create_vlan():
        """Create new VLAN"""
        if 'user_id' not in session:
            return jsonify(format_error_response('Not authenticated')), 401
        
        try:
            data = request.get_json()
            
            # Validate input
            vlan_id = data.get('vlan_id')
            vlan_name = data.get('vlan_name')
            description = data.get('description', '')
            subnet_mask = data.get('subnet_mask', '255.255.255.0')
            auto_delete = data.get('auto_delete', False)
            expiry_hours = data.get('expiry_hours', 24)  # Default 24 hours
            
            # Validate VLAN ID
            is_valid, msg = validate_vlan_id(vlan_id)
            if not is_valid:
                return jsonify(format_error_response('Invalid VLAN ID', msg)), 400
            
            # Check if VLAN already exists
            if VlanConfig.query.filter_by(vlan_id=vlan_id).first():
                return jsonify(format_error_response('VLAN already exists', f'VLAN {vlan_id} is already registered')), 409
            
            # Validate VLAN name
            is_valid, msg = validate_vlan_name(vlan_name)
            if not is_valid:
                return jsonify(format_error_response('Invalid VLAN name', msg)), 400
            
            # Validate subnet mask
            is_valid, msg = validate_subnet_mask(subnet_mask)
            if not is_valid:
                return jsonify(format_error_response('Invalid subnet mask', msg)), 400
            
            # Connect to Cisco device and create VLAN
            cisco_manager = get_cisco_manager(app.config['CISCO_CONFIG'])
            success, conn_msg = cisco_manager.connect()
            
            if not success:
                log_activity(session['user_id'], 'CREATE', f'Failed to connect to device', 'FAILED')
                return jsonify(format_error_response('Device connection failed', conn_msg)), 503
            
            success, vlan_msg = cisco_manager.create_vlan(vlan_id, vlan_name)
            cisco_manager.disconnect()
            
            if not success:
                log_activity(session['user_id'], 'CREATE', f'Failed to create VLAN {vlan_id}', 'FAILED')
                return jsonify(format_error_response('Failed to create VLAN on device', vlan_msg)), 500
            
            # Save to database
            max_hosts = calculate_max_hosts(subnet_mask)
            expires_at = None
            if auto_delete:
                expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
            
            vlan_config = VlanConfig(
                vlan_id=vlan_id,
                vlan_name=vlan_name,
                description=description,
                user_id=session['user_id'],
                subnet_mask=subnet_mask,
                max_hosts=max_hosts,
                status='active',
                device_synced=True,
                sync_timestamp=datetime.utcnow(),
                auto_delete=auto_delete,
                expires_at=expires_at
            )
            
            db.session.add(vlan_config)
            db.session.commit()
            
            log_activity(
                session['user_id'],
                'CREATE',
                f'Created VLAN {vlan_id} ({vlan_name})',
                'SUCCESS',
                vlan_config.id
            )
            
            logger.info(f"VLAN {vlan_id} created successfully by user {session['user_id']}")
            
            return jsonify(format_success_response(
                data=vlan_config.to_dict(),
                message='VLAN created successfully'
            )), 201
            
        except Exception as e:
            logger.error(f"Error creating VLAN: {e}")
            log_activity(session['user_id'], 'CREATE', f'Error: {str(e)}', 'FAILED')
            return jsonify(format_error_response('Failed to create VLAN', str(e))), 500
    
    @app.route('/api/vlans/<vlan_id>', methods=['GET'])
    def get_vlan_details(vlan_id):
        """Get specific VLAN details"""
        try:
            vlan = VlanConfig.query.get(vlan_id)
            if not vlan:
                return jsonify(format_error_response('VLAN not found')), 404
            
            return jsonify(format_success_response(data=vlan.to_dict())), 200
        except Exception as e:
            logger.error(f"Error getting VLAN: {e}")
            return jsonify(format_error_response('Failed to get VLAN', str(e))), 500
    
    @app.route('/api/vlans/<vlan_id>', methods=['PUT'])
    def update_vlan(vlan_id):
        """Update VLAN"""
        if 'user_id' not in session:
            return jsonify(format_error_response('Not authenticated')), 401
        
        try:
            vlan = VlanConfig.query.get(vlan_id)
            if not vlan:
                return jsonify(format_error_response('VLAN not found')), 404
            
            # Check ownership
            if vlan.user_id != session['user_id']:
                return jsonify(format_error_response('Permission denied')), 403
            
            data = request.get_json()
            
            # Update allowed fields
            if 'vlan_name' in data:
                is_valid, msg = validate_vlan_name(data['vlan_name'])
                if not is_valid:
                    return jsonify(format_error_response('Invalid VLAN name', msg)), 400
                vlan.vlan_name = data['vlan_name']
            
            if 'description' in data:
                vlan.description = data['description']
            
            if 'subnet_mask' in data:
                is_valid, msg = validate_subnet_mask(data['subnet_mask'])
                if not is_valid:
                    return jsonify(format_error_response('Invalid subnet mask', msg)), 400
                vlan.subnet_mask = data['subnet_mask']
                vlan.max_hosts = calculate_max_hosts(data['subnet_mask'])
            
            vlan.updated_at = datetime.utcnow()
            db.session.commit()
            
            log_activity(
                session['user_id'],
                'UPDATE',
                f'Updated VLAN {vlan.vlan_id}',
                'SUCCESS',
                vlan_id
            )
            
            return jsonify(format_success_response(
                data=vlan.to_dict(),
                message='VLAN updated successfully'
            )), 200
            
        except Exception as e:
            logger.error(f"Error updating VLAN: {e}")
            log_activity(session['user_id'], 'UPDATE', f'Error: {str(e)}', 'FAILED', vlan_id)
            return jsonify(format_error_response('Failed to update VLAN', str(e))), 500
    
    @app.route('/api/vlans/<vlan_id>', methods=['DELETE'])
    def delete_vlan(vlan_id):
        """Delete VLAN"""
        if 'user_id' not in session:
            return jsonify(format_error_response('Not authenticated')), 401
        
        try:
            vlan = VlanConfig.query.get(vlan_id)
            if not vlan:
                return jsonify(format_error_response('VLAN not found')), 404
            
            # Check ownership
            if vlan.user_id != session['user_id']:
                return jsonify(format_error_response('Permission denied')), 403
            
            # Connect to Cisco device and delete VLAN
            cisco_manager = get_cisco_manager(app.config['CISCO_CONFIG'])
            success, conn_msg = cisco_manager.connect()
            
            if not success:
                return jsonify(format_error_response('Device connection failed', conn_msg)), 503
            
            success, del_msg = cisco_manager.delete_vlan(vlan.vlan_id)
            cisco_manager.disconnect()
            
            if not success:
                log_activity(session['user_id'], 'DELETE', f'Failed to delete VLAN {vlan.vlan_id}', 'FAILED')
                return jsonify(format_error_response('Failed to delete VLAN on device', del_msg)), 500
            
            # Delete from database
            vlan_id_num = vlan.vlan_id
            db.session.delete(vlan)
            db.session.commit()
            
            log_activity(
                session['user_id'],
                'DELETE',
                f'Deleted VLAN {vlan_id_num}',
                'SUCCESS',
                vlan_id
            )
            
            return jsonify(format_success_response(
                message=f'VLAN {vlan_id_num} deleted successfully'
            )), 200
            
        except Exception as e:
            logger.error(f"Error deleting VLAN: {e}")
            log_activity(session['user_id'], 'DELETE', f'Error: {str(e)}', 'FAILED', vlan_id)
            return jsonify(format_error_response('Failed to delete VLAN', str(e))), 500
    
    # ==================== API ROUTES - DEVICE ====================
    
    @app.route('/api/device/status', methods=['GET'])
    def get_device_status():
        """Get Cisco device connection status"""
        try:
            cisco_manager = get_cisco_manager(app.config['CISCO_CONFIG'])
            success, msg = cisco_manager.connect()
            
            if success:
                success, info = cisco_manager.get_device_info()
                cisco_manager.disconnect()
                
                return jsonify(format_success_response(
                    data={
                        'connected': True,
                        'host': app.config['CISCO_CONFIG']['host'],
                        'device_type': app.config['CISCO_CONFIG']['device_type'],
                        'message': msg
                    }
                )), 200
            else:
                return jsonify(format_success_response(
                    data={'connected': False, 'message': msg}
                )), 200
        except Exception as e:
            logger.error(f"Error checking device status: {e}")
            return jsonify(format_success_response(
                data={'connected': False, 'error': str(e)}
            )), 200
    
    @app.route('/api/device/vlans', methods=['GET'])
    def get_device_vlans():
        """Get all VLANs from Cisco device"""
        try:
            cisco_manager = get_cisco_manager(app.config['CISCO_CONFIG'])
            success, msg = cisco_manager.connect()
            
            if not success:
                return jsonify(format_error_response('Failed to connect to device', msg)), 503
            
            success, vlans = cisco_manager.get_all_vlans()
            cisco_manager.disconnect()
            
            if not success:
                return jsonify(format_error_response('Failed to retrieve VLANs', vlans)), 500
            
            return jsonify(format_success_response(
                data={'device_vlans': vlans}
            )), 200
            
        except Exception as e:
            logger.error(f"Error getting device VLANs: {e}")
            return jsonify(format_error_response('Failed to get device VLANs', str(e))), 500
    
    # ==================== API ROUTES - ACTIVITY LOG ====================
    
    @app.route('/api/activities', methods=['GET'])
    def get_activities():
        """Get activity logs"""
        try:
            limit = request.args.get('limit', 50, type=int)
            activities = ActivityLog.query.order_by(
                ActivityLog.created_at.desc()
            ).limit(limit).all()
            
            return jsonify(format_success_response(
                data=[act.to_dict() for act in activities]
            )), 200
        except Exception as e:
            logger.error(f"Error getting activities: {e}")
            return jsonify(format_error_response('Failed to get activities', str(e))), 500
    
    @app.route('/api/activities/user/<user_id>', methods=['GET'])
    def get_user_activities(user_id):
        """Get activity logs for specific user"""
        try:
            limit = request.args.get('limit', 50, type=int)
            activities = ActivityLog.query.filter_by(
                user_id=user_id
            ).order_by(ActivityLog.created_at.desc()).limit(limit).all()
            
            return jsonify(format_success_response(
                data=[act.to_dict() for act in activities]
            )), 200
        except Exception as e:
            logger.error(f"Error getting user activities: {e}")
            return jsonify(format_error_response('Failed to get activities', str(e))), 500
    
    # ==================== ERROR HANDLERS ====================
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify(format_error_response('Resource not found')), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}")
        return jsonify(format_error_response('Internal server error')), 500


def log_activity(user_id: str, action: str, details: str, status: str, vlan_id: str = None):
    """Log user activity to database"""
    try:
        activity = ActivityLog(
            user_id=user_id,
            vlan_id=vlan_id,
            action=action,
            details=details,
            status=status,
            ip_address=get_client_ip()
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error logging activity: {e}")


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
