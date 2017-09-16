import os

from helpers import *


ONLY_PRINT_COMMANDS = False

ROOT_PASSWORD = 'placeholder'
SERVER_ADMIN_USERNAME = 'serveradmin'
SERVER_ADMIN_PASSWORD = 'placeholder'


# Check rights and environment.
try:
    if os.geteuid() != 0:
        print("WARNING: Script not running as root; only printing commands.")
        set_only_print_commands(True)
    else:
        set_only_print_commands(ONLY_PRINT_COMMANDS)
except AttributeError:
    print("WARNING: Script not running on Unix system; only printing commands.")
    set_only_print_commands(True)

# Delete DigitalOcean Message Of The Day.
delete_digitalocean_motd()

# Create and configure users.
set_user_password(username='root', password=ROOT_PASSWORD)
add_user(username=SERVER_ADMIN_USERNAME,
         password=SERVER_ADMIN_PASSWORD,
         sudo_privileges=True)

# Configure SSH access.
run('rm -f $(eval echo "~root")/.ssh/authorized_keys')
set_authorized_ssh_keys(username=SERVER_ADMIN_USERNAME,
                        file_path='authorized_keys')
put_file(source='sshd_config', destination='/etc/ssh/sshd_config')
run('systemctl reload sshd')

# Update & upgrade system and install packages.
apt_update_and_upgrade()
apt_install([
    'letsencrypt',
    'libpq-dev',
    'postgresql', 'postgresql-contrib',
    'python3-pip', 'python3-dev',
    'nginx',
])

# Set up firewall.
set_firewall([
    ('OpenSSH', 'limit'),
    ('Nginx Full', 'allow'),
])

# Install Python virtual environments.
run('pip3 install --upgrade pip')
run('pip3 install virtualenv')

create_database('test', 'placeholder')
