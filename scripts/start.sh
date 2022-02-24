#!bin/bash

UWSGI_INI=sharkle-server_uwsgi.ini
VIRTUAL_ENV=sharkle-venv
WORKING_DIR=/home/ec2-user/build/sharkle

export PATH=/home/ec2-user/.pyenv/bin:/home/ec2-user/.pyenv/plugins/pyenv-virtualenv/shims:/home/ec2-user/.pyenv/shims:/home/ec2-user/.pyenv/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/home/ec2-user/.local/bin:/home/ec2-user/bin

source /home/ec2-user/.bashrc

echo "[Deploy] : Activate virtual env"
pyenv activate $VIRTUAL_ENV

cd $WORKING_DIR

echo "[Deploy] : Copy Secretes to root directory"
cp /home/ec2-user/.env/.env $WORKING_DIR

echo "[Deploy] : Install Requirements"
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "[Deploy] : Migrate"
python manage.py makemigrations
python manage.py migrate

cd /home/ec2-user/

echo "[Deploy] : Running Uwsgi"
uwsgi -i $UWSGI_INI

echo "[Deploy] : Running Nginx"
sudo systemctl start nginx
