import subprocess
import shutil
import os
from pathlib import Path
import platform
import PyInstaller.__main__

def build_vue_app():
    print("Building Vue app...")
    # Determine the correct path for the frontend folder (project root / frontend)
    project_root = Path(__file__).parent.parent
    frontend_path = project_root / "frontend"
    subprocess.run(["npm.cmd", "install"], cwd=str(frontend_path), check=True)
    subprocess.run(["npm.cmd", "run", "build"], cwd=str(frontend_path), check=True)

def clean_build():
    print("Cleaning previous builds...")
    project_root = Path(__file__).parent.parent
    for path in project_root.glob("dist/*"):
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    for path in project_root.glob("build/*"):
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

def run_pyinstaller():
    print("Running PyInstaller...")
    project_root = Path(__file__).parent.parent
    main_py = str(project_root / "main.py")
    
    # Build add-data arguments using the OS path separator
    add_data_frontend = f"{project_root / 'frontend' / 'dist'}{os.pathsep}frontend/dist"
    add_data_backend = f"{project_root / 'backend'}{os.pathsep}backend"
    add_data_vec = f"{project_root / 'backend' / 'pdf_helper' / 'vec0.dll'}{os.pathsep}backend/pdf_helper"

    pyinstaller_args = [
        main_py,
        "--name=Imandiao企业私有大模型",
        "--onefile",
        "--windowed",
        f"--add-data={add_data_frontend}",
        f"--add-data={add_data_backend}",
        f"--add-data={add_data_vec}",
        "--hidden-import=requests",
        "--hidden-import=psutil",
        "--hidden-import=cryptography",       
        "--hidden-import=cryptography.hazmat.backends.openssl",  
    ]
    
    if platform.system() == "Windows":
        icon_path = Path(__file__).parent / "icon.ico"
        pyinstaller_args.extend([f"--icon={icon_path}"])
    elif platform.system() == "Darwin":
        icon_path = Path(__file__).parent / "icon.icns" 
        pyinstaller_args.extend([
            f"--icon={icon_path}",
            "--osx-bundle-identifier=com.yourcompany.aidesktopapp"
        ])
    
    PyInstaller.__main__.run(pyinstaller_args)

def main():
    clean_build()
    build_vue_app()
    run_pyinstaller()
    print("Build completed successfully!")

if __name__ == "__main__":
    main()