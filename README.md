# Steps to run the service

First need to create and EC2 instance and need to run the following commands.
```shell
sudo apt update
sudo apt install python3-pip git docker-ce docker-ce-cli containerd.io nginx openssl
```
## Pre-requisite

This service depends on two external service
1. A postgresql server
2. A redis server

First setup the postgres server and optionally the redis server. Then run the below commands

```shell
git clone https://github.com/Nirmal-Neel/book-management.git
cd book-management
pip3 install -r requirements.txt
```

Then update the following files with the correct db string

1. **book-management/docker-compose.yml (line number 9)**
2. **book-management/app/alembic.ini (line number 61)**

Then need to run the alembic migration for database table creation. Run the following commands
```shell
alembic upgrade head
```

Run the docker compose file to start the server
```shell
sudo docker-compose up -d
```

### Nginx setup
Before setting up nginx, need to generate self signed certificate.
```shell
cd /etc/nginx
sudo mkdir ssl
sudo openssl req -batch -x509 -nodes -days 365 \
-newkey rsa:2048 \
-keyout /etc/nginx/ssl/server.key \
-out /etc/nginx/ssl/server.crt
```
Once the certificate and key is generated, we need to complete the nginx setup. For that -
```shell
cd /etc/nginx/sites-enabled/
sudo nano fastapi_nginx
```
In that fastapi_nginx file, put the following -
```shell
server {
    listen 443 ssl;
    ssl on;
    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;
    server_name <ip address of the ec2 instance>;
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
server {
    listen 80 default_server;
    server_name _;
    return 301 https://$host$request_uri;
}
```
Once this is saved, run the below command
```
sudo service nginx restart
```
