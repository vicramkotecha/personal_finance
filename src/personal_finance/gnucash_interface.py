import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

PS_DIR = os.path.join(os.getcwd(), 'src', 'powershell')


def _run_ps1(script_name, *args):
    script_path = os.path.join(PS_DIR, script_name)
    result = subprocess.run(
        ['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path, *args],
        capture_output=True,
        text=True
    )
    return result


def launch_gnucash(gnucash_file):
    result = _run_ps1('launch_gnucash.ps1', gnucash_file)
    if result.returncode != 0:
        return result, None
    pid = int(result.stdout.strip())
    return result, pid


def close_gnucash(pid):
    result = _run_ps1('close_gnucash.ps1', str(pid))
    return result


def enter_transaction(pid, date, description, transfer, deposit, withdrawal):
    result = _run_ps1(
        'enter_transaction.ps1',
        str(pid), date, description, transfer, deposit, withdrawal,
    )
    return result


def open_account_register(pid, account_name):
    result = _run_ps1('open_account_register.ps1', str(pid), account_name)
    return result


if __name__ == '__main__':
    gnucash_file = 'test_data/test_accounts.xml.gnucash'
    launch_result, pid = launch_gnucash(gnucash_file)
    if pid:
        close_result = close_gnucash(pid)

