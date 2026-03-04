import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

GNUCASH_HOME = os.getenv('GNUCASH_HOME')
GNUCASH_EXE = os.path.join(GNUCASH_HOME, 'gnucash.exe') if GNUCASH_HOME else None

def launch_gnucash(gnucash_file):
    job_file = os.path.join(os.getcwd(), 'src', 'powershell', 'gnucash_interface.ps1')
    result = subprocess.run(
        ['powershell', '-ExecutionPolicy', 'Bypass', '-File', job_file, gnucash_file],
        capture_output=True
    )
    return result.returncode

if __name__ == '__main__':
    gnucash_file = 'test_data/test_accounts.xml.gnucash'
    launch_gnucash(gnucash_file)

