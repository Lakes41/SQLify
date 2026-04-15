import subprocess
import sys

def run():
    print("Starting pip install...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        capture_output=True, text=True
    )
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
    print("RETURN CODE:", result.returncode)

if __name__ == "__main__":
    run()
