import os

def create_file(path, content=""):
    """Helper function to create a file with the given content."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def create_project_structure(project_name):
    """Create the directory structure for the project."""
    os.makedirs(project_name, exist_ok=True)

    services = [
        {"name": "stock_fetcher", "modules": ["httpx", "pika", "redis"]},
        {"name": "stock_processor", "modules": ["httpx", "tortoise-orm", "pika", "redis"]},
        {"name": "notification", "modules": ["fastapi", "celery", "redis", "smtplib"]},
        {"name": "user_management", "modules": ["fastapi", "tortoise-orm", "redis"]},
        {"name": "admin_monitoring", "modules": ["fastapi", "prometheus_client", "grafana_api"]}
    ]
    
    for service in services:
        service_path = os.path.join(project_name, service["name"])
        
        # Create basic service directories
        os.makedirs(os.path.join(service_path, "app", "services"), exist_ok=True)
        os.makedirs(os.path.join(service_path, "app", "models"), exist_ok=True)
        os.makedirs(os.path.join(service_path, "app", "routes"), exist_ok=True)
        os.makedirs(os.path.join(service_path, "app", "dependencies"), exist_ok=True)
        os.makedirs(os.path.join(service_path, "logs"), exist_ok=True)
        os.makedirs(os.path.join(service_path, "tests"), exist_ok=True)
        
        # Create basic files
        create_file(os.path.join(service_path, "app", "main.py"), f"# {service['name'].capitalize()} Service\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {{'message': '{service['name'].capitalize()} Service'}}\n")
        create_file(os.path.join(service_path, "app", "config.py"), "from pydantic_settings import BaseSettings\n\nclass Settings(BaseSettings):\n    DATABASE_URL: str = \"mysql://user:password@localhost:3306/db\"\n    REDIS_URL: str = \"redis://localhost:6379/0\"\n    RABBITMQ_URL: str = \"amqp://guest:guest@localhost:5672/\"\n\n    class Config:\n        env_file = \".env\"\n\nsettings = Settings()\n")
        create_file(os.path.join(service_path, ".env"), "DATABASE_URL=mysql://user:password@localhost:3306/db\nREDIS_URL=redis://localhost:6379/0\nRABBITMQ_URL=amqp://guest:guest@localhost:5672/\n")
        create_file(os.path.join(service_path, "tests", "test_main.py"), "from fastapi.testclient import TestClient\nfrom app.main import app\n\nclient = TestClient(app)\n\ndef test_read_root():\n    response = client.get('/')\n    assert response.status_code == 200\n    assert response.json() == {'message': '" + service['name'].capitalize() + " Service'}\n")
        
        # Create Dockerfile
        create_file(os.path.join(service_path, "Dockerfile"), "FROM python:3.12-slim\nWORKDIR /app\nCOPY . /app\nRUN pip install --no-cache-dir -r requirements.txt\nCMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n")
        
        # Create requirements.txt with service-specific modules
        requirements_content = "\n".join(service["modules"])
        create_file(os.path.join(service_path, "requirements.txt"), f"fastapi\nuvicorn\n{requirements_content}\n")

        print(f"Created {service['name']} microservice with required modules.")

def main():
    project_name = input("Enter your project name: ")
    create_project_structure(project_name)
    print(f"\nProject {project_name} created successfully!")

if __name__ == "__main__":
    main()
