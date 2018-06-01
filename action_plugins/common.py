import subprocess
import os

from ansible.errors import AnsibleActionFail

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

def _version(v):
    return tuple(map(int, v.split('.')))

def _dcos_path():
    dcos_path = os.environ.copy()
    dcos_path["PATH"] = os.getcwd() + ':' + dcos_path["PATH"]
    display.vvv('dcos cli: path environment variable: {}'.format(dcos_path["PATH"]) )
    return dcos_path

def ensure_dcos():
    """Check whether the dcos cli is installed."""

    try:
        r = subprocess.check_output(['dcos', '--version']).decode()
    except subprocess.CalledProcessError:
        raise AnsibleActionFail("DC/OS CLI is not installed!")

    raw_version = ''
    for line in r.strip().split('\n'):
        display.vvv(line)
        k, v = line.split('=')
        if k == 'dcoscli.version':
            raw_version = v

    v = _version(raw_version)
    if v < (0, 5, 0):
        raise AnsibleActionFail(
            "DC/OS CLI 0.5.x is required, found {}".format(v))
    if v >= (0, 7, 0):
        raise AnsibleActionFail(
            "DC/OS CLI version > 0.5.x detected, may not work")
    display.vvv("dcos: all prerequisites seem to be in order")


def run_command(cmd, description='run command', stop_on_error=False):
    """Run a command and catch exceptions for Ansible."""
    display.vvv("command: " + ' '.join(cmd))

    from subprocess import CalledProcessError, check_output

    try:
        output = check_output(cmd, env=_dcos_path())
        returncode = 0
    except CalledProcessError as e:
        output = e.output
        returncode = e.returncode
        if stop_on_error and returncode != 0:
             raise AnsibleActionFail('Failed to {}: {}'.format(description, e))

    return output