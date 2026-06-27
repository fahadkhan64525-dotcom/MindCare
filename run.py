#!/usr/bin/env python
"""
Startup script for MindCare API
Handles initialization and starts the server
"""
import numpy
import sys
import os
import argparse
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import app, init_db, logger
from config import get_config, Config


def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'flask',
        'flask_cors',
        'sklearn',
        'pandas',
        'numpy',
        'joblib'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.error("Please install them using: pip install -r requirements.txt")
        return False
    
    logger.info("All dependencies are installed")
    return True


def check_model():
    """Check if model is trained"""
    config = get_config()
    
    if not os.path.exists(config.MODEL_PATH):
        logger.warning(f"Model file not found at {config.MODEL_PATH}")
        logger.warning("The API will use fallback rule-based prediction")
        logger.info("To train the model, run: python train_model.py")
        return False
    
    logger.info("Model file found and ready")
    return True


def main():
    parser = argparse.ArgumentParser(description='MindCare API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--train', action='store_true', help='Train model before starting')
    args = parser.parse_args()
    
    logger.info("="*60)
    logger.info("MindCare Mental Health Support API")
    logger.info("="*60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Train model if requested
    if args.train:
        logger.info("\nTraining model...")
        try:
            from train_model import main as train_main
            train_main()
        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")
            sys.exit(1)
    else:
        check_model()
    
    # Initialize database
    logger.info("\nInitializing database...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        sys.exit(1)
    
    # Start server
    logger.info("\n" + "="*60)
    logger.info(f"Starting API server on {args.host}:{args.port}")
    logger.info("="*60)
    logger.info(f"\nAccess the API at: http://localhost:{args.port}")
    logger.info(f"API Documentation: http://localhost:{args.port}/")
    logger.info("\nPress CTRL+C to stop the server\n")
    
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug or app.config.get('DEBUG', False)
        )
    except KeyboardInterrupt:
        logger.info("\n\nServer shutdown by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
