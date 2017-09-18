import os
import subprocess
import sys
import typing


_ONLY_PRINT_COMMANDS = True
_SCRIPT_DIR = os.path.dirname(__file__).replace('\\', '/') + '/'


def add_user(username: str, password: str, sudo_privileges: bool) -> None:
    run('adduser ' + username + ' --gecos "" --disabled-password')
    set_user_password(username, password)

    if sudo_privileges:
        run('usermod -aG sudo ' + username)


def apt_install(packages: typing.List[str]) -> None:
    command = 'apt -y install'

    for package in packages:
        command += ' ' + package

    run(command)


def apt_update_and_upgrade() -> None:
    run('apt update')
    run('apt -y upgrade')


def create_database(name: str, password: str) -> None:
    username = 'postgres_' + name
    run_postgres('CREATE DATABASE ' + name)
    run_postgres('CREATE USER ' + username +
                 ' WITH PASSWORD \'' + password + '\'')
    run_postgres('ALTER ROLE ' + username + ' SET client_encoding TO \'utf8\'')
    run_postgres('ALTER ROLE ' + username +
                 ' SET default_transaction_isolation TO \'read committed\'')
    run_postgres('ALTER ROLE ' + username + ' SET timezone TO \'UTC\'')
    run_postgres('GRANT ALL PRIVILEGES ON DATABASE ' +
                 name + ' TO ' + username)


def delete_user(username: str) -> None:
    run('rm -rf $(eval echo "~' + username + '")')
    run('userdel ' + username)


def delete_digitalocean_motd() -> None:
    run('rm -f /etc/update-motd.d/99-one-click')


def put_file(source: str, destination: str) -> None:
    source = _SCRIPT_DIR + 'files/' + source

    destination_dir, _, _ = destination.rpartition('/')

    if destination_dir:
        run('mkdir -p ' + destination_dir)

    run('cp -f ' + source + ' ' + destination)


def run(command: str) -> None:
    if _ONLY_PRINT_COMMANDS:
        print(command)
    else:
        print('>>> ' + command)
        process = subprocess.Popen(os.environ.get('SHELL', 'sh'),
                                   stdin=subprocess.PIPE)
        process.communicate((command + '\n').encode())


def run_postgres(command: str) -> None:
    run('sudo -u postgres bash -c "echo -e \\"' +
        command + ';\\n\\\\q\\" | psql"')


def set_authorized_ssh_keys(username: str, file_path: str) -> None:
    put_file(source=file_path,
             destination='$(eval echo "~' + username + '")/.ssh/authorized_keys')
    run('chmod 700 $(eval echo "~' + username + '")/.ssh')
    run('chmod 600 $(eval echo "~' + username + '")/.ssh/authorized_keys')
    run('chown -R ' + username + ':' + username +
        ' $(eval echo "~' + username + '")/.ssh')


def set_only_print_commands(value: bool) -> None:
    global _ONLY_PRINT_COMMANDS
    _ONLY_PRINT_COMMANDS = value


def set_firewall(settings: typing.List[typing.Tuple[str, str]]) -> None:
    run('ufw --force reset')

    for setting in settings:
        run('ufw ' + setting[1] + ' "' + setting[0] + '"')

    run('ufw --force enable')
    run('rm -f /etc/ufw/*.rules.*_*')


def set_user_password(username: str, password: str) -> None:
    run('echo "' + username + ':' + password + '" | chpasswd')
