from backend.ollama.ollama_manager import OllamaManager
import subprocess
import os

manager = OllamaManager()

print("=== System Info ===")
print(f"OS: {manager.system}")
print(f"Install dir: {manager.install_dir}")
print(f"Ollama path: {manager.ollama_path}")

print("\n=== Before Setup ===")
print("Installed:", manager.is_ollama_installed())
print("Running:", manager.is_ollama_running())
print("Model installed:", manager.is_model_installed())

print("\n=== Checking Windows Services ===")
try:
    services = subprocess.run(
        ['sc', 'query', 'Ollama'],
        capture_output=True,
        text=True
    )
    print(services.stdout)
except Exception as e:
    print(f"Service check failed: {e}")

print("\n=== Running Setup ===")
try:
    manager.setup_ollama()
    print("Setup completed successfully")
except Exception as e:
    print(f"Setup failed: {e}")

print("\n=== After Setup ===")
print("Installed:", manager.is_ollama_installed())
print("Running:", manager.is_ollama_running())
print("Model installed:", manager.is_model_installed())

print("\n=== Path Verification ===")
print("Ollama path exists:", manager.ollama_path.exists())
print("Full path:", os.path.abspath(manager.ollama_path))

print("\n=== Version Check ===")
try:
    result = subprocess.run(
        [str(manager.ollama_path), '--version'],
        capture_output=True,
        text=True
    )
    print("Version output:", result.stdout.strip())
except Exception as e:
    print(f"Version check failed: {e}")
    print("PATH environment variable:", os.getenv('PATH'))