#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import logging
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Setup logging configuration"""
    log_dir = Path.home() / "Library" / "Logs" / "TAK-Manager" if sys.platform == "darwin" else Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"build-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_file

def build_frontend():
    """Build the React frontend"""
    web_dir = Path("web")
    if not web_dir.exists():
        logging.error("Web directory not found")
        sys.exit(1)

    logging.info("Building frontend...")
    npm_cmd = 'npm.cmd' if sys.platform == 'win32' else 'npm'
    try:
        # Clean previous build
        dist_dir = web_dir / "dist"
        if dist_dir.exists():
            logging.info("Cleaning previous frontend build...")
            shutil.rmtree(dist_dir)

        # Install dependencies
        subprocess.run([npm_cmd, 'install'], cwd=web_dir, check=True)
        # Build frontend
        subprocess.run([npm_cmd, 'run', 'build'], cwd=web_dir, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error building frontend: {e}")
        sys.exit(1)

def clean_build():
    """Clean build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            logging.info(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Remove any .spec files if not using our specific one
    for spec_file in Path('.').glob('*.spec'):
        if spec_file.name != 'tak-manager.spec':
            logging.info(f"Removing {spec_file}...")
            spec_file.unlink()
            
    # Clean pycache in subdirectories
    for pycache_dir in Path('.').glob('**/__pycache__'):
        logging.info(f"Cleaning {pycache_dir}...")
        shutil.rmtree(pycache_dir)

def ensure_resources():
    """Ensure all required resources exist"""
    resources_dir = Path("resources")
    resources_dir.mkdir(exist_ok=True)

    # Check for required files
    required_files = {
        'darwin': 'icon.icns',
        'win32': 'icon.ico',
        'linux': 'icon.png'
    }

    platform_file = required_files.get(sys.platform)
    if platform_file:
        icon_path = resources_dir / platform_file
        if not icon_path.exists():
            logging.warning(f"{platform_file} not found in resources directory")

def create_debug_script():
    """Create a debug launch script"""
    if sys.platform == "darwin":
        debug_script = Path("dist") / "debug_launch.command"
        with open(debug_script, "w") as f:
            f.write("""#!/bin/bash
# Change to the MacOS directory
cd "$(dirname "$0")/TAK Manager.app/Contents/MacOS"

# Set environment variables for debugging
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Run the application without any arguments
./TAK\\ Manager
""")
        # Make it executable
        debug_script.chmod(0o755)
        logging.info(f"Created debug launch script at {debug_script}")

def build_app():
    """Build the application using PyInstaller"""
    try:
        # Setup logging
        log_file = setup_logging()
        logging.info(f"Build log will be written to: {log_file}")

        # Clean previous builds
        clean_build()

        # Build frontend
        build_frontend()

        # Ensure resources exist
        ensure_resources()

        # Run PyInstaller
        logging.info("Building application with PyInstaller...")
        subprocess.run(['pyinstaller', 'tak-manager.spec', '--clean'], check=True)

        # Create debug launch script
        create_debug_script()

        # Create distribution archives
        dist_dir = Path('dist')
        if sys.platform == 'darwin':
            app_name = 'TAK Manager.app'
            if (dist_dir / app_name).exists():
                logging.info("Creating macOS ZIP archive...")
                shutil.make_archive(
                    str(dist_dir / 'TAK-Manager-macOS'),
                    'zip',
                    dist_dir,
                    app_name
                )
        elif sys.platform == 'win32':
            app_dir = dist_dir / 'TAK Manager'
            if app_dir.exists():
                logging.info("Creating Windows distribution archive...")
                shutil.make_archive(
                    str(dist_dir / 'TAK-Manager-Windows'),
                    'zip',
                    app_dir
                )
        else:  # Linux
            app_dir = dist_dir / 'tak-manager'
            if app_dir.exists():
                logging.info("Creating Linux distribution archive...")
                archive_name = str(dist_dir / 'TAK-Manager-Linux.tar.gz')
                subprocess.run(['tar', 'czf', archive_name, '-C', str(dist_dir), 'tak-manager'])

        logging.info("Build completed successfully!")
        logging.info(f"Output can be found in the {dist_dir} directory")
        logging.info(f"For debugging, check the log file at: {log_file}")

    except Exception as e:
        logging.error(f"Error during build: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    build_app()