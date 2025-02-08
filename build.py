"""Build script for creating executable."""

import os
import shutil
from pathlib import Path
import PyInstaller.__main__
import traceback
import sys

def clean_build_dirs():
    """Remove old build and dist directories."""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name} directory")

def build_exe():
    """Run PyInstaller build process."""
    print("Building executable...")
    PyInstaller.__main__.run([
        'pyrogue.spec',
        '--clean'
    ])

if __name__ == "__main__":
    try:
        clean_build_dirs()
        build_exe()
        print("Build complete! Executable is in the 'dist' directory")
    except Exception as e:
        print("\nError during build:")
        print(f"{type(e).__name__}: {e}")
        print("\nStack trace:")
        traceback.print_exc()
    
    print("\nPress Enter to exit...")
    input()
