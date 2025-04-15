import os
import platform
import subprocess
import requests
import tempfile
from pathlib import Path
import psutil
from .models_config import MODELS

class OllamaManager:
    def __init__(self):
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.install_dir = self._get_install_dir()
        self.ollama_path = self._get_ollama_path()
    
    def _get_install_dir(self):
        """Get platform-specific install directory"""
        if self.system == 'windows':
            return Path(os.getenv('LOCALAPPDATA')) / 'Ollama'
        return Path.home() / '.ollama'
    
    def _get_ollama_path(self):
        """Get the Ollama executable path with Windows-specific checks"""
        if self.system == 'windows':
            # Check default install location
            default_path = self.install_dir / 'ollama.exe'
            if default_path.exists():
                return default_path
            
            # Check PATH environment variable
            try:
                result = subprocess.run(
                    ['where', 'ollama'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode == 0:
                    return Path(result.stdout.strip())
            except Exception:
                pass
            
            # Common alternative locations
            paths_to_check = [
                Path(os.getenv('ProgramFiles')) / 'Ollama' / 'ollama.exe',
                Path(os.getenv('ProgramFiles(x86)')) / 'Ollama' / 'ollama.exe',
                Path(os.getenv('LOCALAPPDATA')) / 'Programs' / 'Ollama' / 'ollama.exe'
            ]
            
            for path in paths_to_check:
                if path.exists():
                    return path
            
        return Path('/usr/local/bin/ollama')  # Default for non-Windows
    
    def is_ollama_downloaded(self):
        """Check if the Ollama installer file has already been downloaded (Windows only)."""
        if self.system == 'windows':
            temp_dir = tempfile.gettempdir()
            installer_path = Path(temp_dir) / 'OllamaSetup.exe'
            return installer_path.exists() and installer_path.stat().st_size > 0
        # For non-Windows systems, assume the installer method doesn't require a pre-downloaded file.
        return True
    
    def is_ollama_installed(self):
        """Check if Ollama is installed"""
        try:
            if self.system == 'windows':
                # Check both default install path and PATH
                path_exists = self.ollama_path.exists()
                which_result = subprocess.run(
                    ['where', 'ollama'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return path_exists or which_result.returncode == 0
            else:
                result = subprocess.run(['which', 'ollama'], capture_output=True, text=True)
                return result.returncode == 0
        except Exception:
            return False

    def is_ollama_running(self):
        """Check if Ollama process is running"""
        try:
            # Try querying ollama directly; add creation flags on Windows
            if self.system == 'windows':
                result = subprocess.run(
                    [str(self.ollama_path), 'list'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                result = subprocess.run(
                    [str(self.ollama_path), 'list'],
                    capture_output=True,
                    text=True
                )
            return result.returncode == 0
        except Exception:
            # Fallback to process check
            for proc in psutil.process_iter(['name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    proc_exe = proc.info['exe'].lower() if proc.info['exe'] else ''
                    if 'ollama' in proc_name or 'ollama' in proc_exe:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
    
    def is_model_installed(self, model_name="deepseek-r1:1.5b"):
        """Check if model is installed"""
        try:
            if self.system == 'windows':
                result = subprocess.run(
                    [str(self.ollama_path), 'list'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                result = subprocess.run(
                    [str(self.ollama_path), 'list'],
                    capture_output=True,
                    text=True
                )
            return model_name in result.stdout
        except Exception:
            return False
    
    def setup_ollama(self, progress_callback=None):
        print("DEBUG: Starting setup_ollama")
        if not self.is_ollama_installed():
            print("DEBUG: Ollama is not installed. Beginning installation.")
            if progress_callback:
                progress_callback('downloading', 0)
            self._install_ollama(progress_callback)
        else:
            print("DEBUG: Ollama is already installed.")

        if not self.is_ollama_running():
            print("DEBUG: Ollama is not running. Starting Ollama.")
            if progress_callback:
                progress_callback('starting', 80)
            self._start_ollama()
        else:
            print("DEBUG: Ollama is already running.")

        # Instead of checking for a single model, loop through all models in MODELS.
        for model in MODELS:
            if not self.is_model_installed(model):
                print(f"DEBUG: Model {model} is not installed. Pulling model.")
                if progress_callback:
                    progress_callback('pulling_model', 90)
                try:
                    self._pull_model(progress_callback, model)
                except Exception as e:
                    raise Exception(f"Failed to pull model {model}: {str(e)}")
            else:
                print(f"DEBUG: Model {model} is already installed.")

        if progress_callback:
            progress_callback('complete', 100)
        print("DEBUG: setup_ollama completed.")

    def _install_ollama(self, progress_callback=None):
        """Platform-specific installation with progress"""
        if self.system == 'windows':
            self._install_windows(progress_callback)
        else:
            self._install_unix(progress_callback)

    def _install_windows(self, progress_callback=None):
        """Install standalone CLI package on Windows silently using the standalone CLI package."""
        try:
            print("DEBUG: Starting standalone CLI installation for Windows.")
            temp_dir = tempfile.gettempdir()
            zip_path = Path(temp_dir) / 'ollama-windows-amd64.zip'

            # Verify if ZIP file is valid using Python's built-in method
            import zipfile
            def is_valid_zip(file_path):
                return file_path.exists() and zipfile.is_zipfile(str(file_path))

            # Remove corrupted ZIP files
            if zip_path.exists() and not is_valid_zip(zip_path):
                print("DEBUG: Invalid ZIP file detected. Removing.")
                zip_path.unlink(missing_ok=True)

            # Download ZIP file if it doesn't exist or was corrupted and removed
            if not zip_path.exists():
                print("DEBUG: Standalone CLI zip not found or corrupted. Downloading...")
                url = "https://imandiao.oss-cn-beijing.aliyuncs.com/ollama-windows-amd64.zip"
                if progress_callback:
                    progress_callback('downloading_cli_zip', 10)

                max_attempts = 3
                attempt = 0
                success = False
                while attempt < max_attempts and not success:
                    try:
                        response = requests.get(url, stream=True, timeout=300)
                        response.raise_for_status()
                        success = True
                    except requests.exceptions.RequestException as e:
                        attempt += 1
                        print(f"DEBUG: Download attempt {attempt} failed: {e}")
                        if attempt == max_attempts:
                            raise Exception("Failed to download CLI zip after several attempts") from e

                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0

                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=16384):  # 16kB chunks
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback and total_size > 0:
                                progress = 10 + int((downloaded / total_size) * 50)
                                progress_callback('downloading_cli_zip', progress)
                print("DEBUG: Standalone CLI zip downloaded.")

                # Validate the downloaded ZIP immediately
                if not is_valid_zip(zip_path):
                    zip_path.unlink(missing_ok=True)
                    raise Exception("Downloaded file is not a valid zip file.")
            else:
                print("DEBUG: Valid ZIP already downloaded.")
                if progress_callback:
                    progress_callback('cli_zip_exists', 10)

            # Extract ZIP file to installation directory
            if progress_callback:
                progress_callback('extracting_cli_zip', 60)

            target_dir = self.install_dir
            target_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
            print(f"DEBUG: Zip file extracted to {target_dir}.")

            if progress_callback:
                progress_callback('extracting_cli_zip', 80)

            # Update ollama_path to point to extracted executable
            self.ollama_path = target_dir / 'ollama.exe'
            if not self.ollama_path.exists():
                raise Exception("Standalone CLI installation failed: ollama.exe not found after extraction.")
            print(f"DEBUG: Standalone CLI installation successful. Executable located at {self.ollama_path}.")

            if progress_callback:
                progress_callback('complete_installation', 90)

            # Clean up the downloaded zip file
            zip_path.unlink(missing_ok=True)
            print("DEBUG: Cleaned up downloaded zip file.")

        except Exception as e:
            raise Exception(f"Standalone CLI installation failed: {str(e)}")

    def _install_unix(self, progress_callback=None):
        """Automatic silent install for Unix systems"""
        try:
            if progress_callback:
                progress_callback('installing', 10)
            
            # Run the install script directly in silent mode
            result = subprocess.run(
                "curl -fsSL https://ollama.com/install.sh | sh",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300
            )
            
            if progress_callback:
                progress_callback('installing', 80)
                
            if not self.is_ollama_installed():
                raise Exception("Installation verification failed")
                
        except Exception as e:
            raise Exception(f"Automatic installation failed: {str(e)}")
    
    def _start_ollama(self):
        """Start Ollama server using the standalone CLI on Windows with hidden window."""
        try:
            print("DEBUG: Attempting to start Ollama server using standalone CLI.")
            if self.system == 'windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = subprocess.CREATE_NO_WINDOW
                process = subprocess.Popen(
                    [str(self.ollama_path), 'serve'],
                    startupinfo=startupinfo,
                    creationflags=creationflags,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                import time
                time.sleep(5)
            else:
                process = subprocess.Popen(
                    [str(self.ollama_path), 'serve'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                import time
                time.sleep(5)
            print("DEBUG: Ollama server should now be running.")
        except subprocess.CalledProcessError as e:
            print("DEBUG: Failed to start Ollama:", e.stderr.decode())
    
    def _pull_model(self, progress_callback=None, model_name="deepseek-r1:1.5b"):
        """Pull model with progress debugging and hidden window on Windows."""
        try:
            print(f"DEBUG: Starting to pull model '{model_name}'.")
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['LANG'] = 'en_US.UTF-8'
            
            if self.system == 'windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = subprocess.CREATE_NO_WINDOW
            else:
                startupinfo = None
                creationflags = 0
            
            process = subprocess.Popen(
                [str(self.ollama_path), 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',  # Replace problematic characters instead of crashing
                bufsize=1,
                env=env,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            
            for line in process.stdout:
                line = line.strip()
                print(f"DEBUG: Pull model output: {line}")
                if 'pulling manifest' in line and progress_callback:
                    progress_callback('pulling_model', 90)
                elif 'downloading' in line and progress_callback:
                    progress_callback('pulling_model', 92)
                elif 'extracting' in line and progress_callback:
                    progress_callback('pulling_model', 95)
                elif 'complete' in line and progress_callback:
                    progress_callback('pulling_model', 99)
            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, process.args)
            print("DEBUG: Model pulling completed successfully.")
        except Exception as e:
            raise Exception(f"Failed to pull model: {str(e)}")