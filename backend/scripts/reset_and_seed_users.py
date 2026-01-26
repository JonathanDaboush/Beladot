import sys
import os
import subprocess

# Always run from project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'backend', 'scripts')

# Helper to run a script with correct PYTHONPATH

def run_script(script_name):
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    env = os.environ.copy()
    env['PYTHONPATH'] = PROJECT_ROOT
    result = subprocess.run([
        sys.executable, script_path
    ], env=env, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"Failed to run {script_name}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    print("Clearing all users...")
    run_script('clear_users.py')
    print("Seeding demo users...")
    run_script('seed_demo_data.py')
    print("Done. Users table should be clean and seeded.")
