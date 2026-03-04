import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

def launch_gnucash(gnucash_file):
    job_file = os.path.join(os.getcwd(), 'src', 'powershell', 'gnucash_interface.ps1')
    result = subprocess.run(
        ['powershell', '-ExecutionPolicy', 'Bypass', '-File', job_file, gnucash_file],
        capture_output=True,
        text=True
    )
    return result

if __name__ == '__main__':
    gnucash_file = 'test_data/test_accounts.xml.gnucash'
    launch_gnucash(gnucash_file)

