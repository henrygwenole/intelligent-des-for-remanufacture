# plant-sim-bridge/license_config.py
"""
Plant Simulation License Configuration
Configure your license server settings here
"""

# Your Strathclyde University License Server Configuration
LICENSE_CONFIG = {
    "primary_server": "28000@afrc-ls4.afrc.strath.ac.uk",
    
    # Backup servers (if available)
    "backup_servers": [
        # Add backup license servers here if you have them
        # "28000@backup-server.strath.ac.uk",
    ],
    
    # Connection settings
    "connection_timeout": 30,  # seconds
    "retry_attempts": 3,
    "retry_delay": 5,  # seconds between retries
    
    # Advanced settings
    "auto_configure_registry": True,  # Attempt to set registry keys
    "auto_configure_environment": True,  # Set environment variables
    "validate_license_on_connect": True,  # Test license after connection
    
    # Plant Simulation settings
    "plant_sim_progid": "Tecnomatix.PlantSimulation.RemoteControl.25.4",
    "auto_create_model": True,  # Create new model on connection
    "enable_com_interface": True,  # Enable COM interface
    "set_visible": True,  # Make Plant Simulation visible
}

# License server validation
def validate_license_server(server_string):
    """Validate license server format: port@hostname"""
    try:
        if '@' not in server_string:
            return False
        port, hostname = server_string.split('@', 1)
        return port.isdigit() and len(hostname.strip()) > 0
    except:
        return False

# Get primary license server
def get_primary_license_server():
    """Get the primary license server configuration"""
    return LICENSE_CONFIG["primary_server"]

# Get all license servers
def get_all_license_servers():
    """Get all configured license servers"""
    servers = [LICENSE_CONFIG["primary_server"]]
    servers.extend(LICENSE_CONFIG["backup_servers"])
    return [s for s in servers if validate_license_server(s)]

# Environment variable names that Plant Simulation checks
ENVIRONMENT_VARIABLES = [
    "SPLM_LICENSE_SERVER",
    "LM_LICENSE_FILE", 
    "FLEXLM_LICENSE_FILE"
]

# Registry paths where license info might be stored
REGISTRY_PATHS = [
    r"SOFTWARE\Siemens\PLMLicense",
    r"SOFTWARE\WOW6432Node\Siemens\PLMLicense", 
    r"SOFTWARE\Tecnomatix\Plant Simulation\25.4",
    r"SOFTWARE\WOW6432Node\Tecnomatix\Plant Simulation\25.4",
    r"SOFTWARE\Siemens\Licensing",
    r"SOFTWARE\WOW6432Node\Siemens\Licensing"
]