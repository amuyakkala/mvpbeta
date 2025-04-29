import sys
import json
from datetime import datetime
from pathlib import Path

def generate_test_logs(output_dir: str) -> bool:
    """
    Generate test log files for testing.
    
    Args:
        output_dir: Directory to save test logs
        
    Returns:
        bool indicating if generation was successful
    """
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate clean log
        clean_log = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": "Application started successfully",
            "metadata": {
                "service": "test-service",
                "version": "1.0.0",
                "environment": "production"
            },
            "events": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": "startup",
                    "status": "success"
                },
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": "health_check",
                    "status": "success"
                }
            ]
        }
        
        # Generate error log
        error_log = {
            "timestamp": datetime.now().isoformat(),
            "level": "ERROR",
            "message": "Failed to connect to database",
            "metadata": {
                "service": "test-service",
                "version": "1.0.0",
                "environment": "production"
            },
            "error": {
                "type": "DatabaseConnectionError",
                "message": "Connection refused",
                "stack_trace": [
                    "at Database.connect()",
                    "at Service.initialize()",
                    "at Application.start()"
                ]
            },
            "events": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": "startup",
                    "status": "failed"
                },
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": "retry",
                    "status": "failed"
                }
            ]
        }
        
        # Save logs
        clean_log_path = Path(output_dir) / "clean_log.json"
        error_log_path = Path(output_dir) / "error_log.json"
        
        with open(clean_log_path, "w") as f:
            json.dump(clean_log, f, indent=2)
        
        with open(error_log_path, "w") as f:
            json.dump(error_log, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"Error generating test logs: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_logs.py <output_directory>")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    if generate_test_logs(output_dir):
        print("Test logs generated successfully")
        sys.exit(0)
    else:
        print("Failed to generate test logs")
        sys.exit(1) 