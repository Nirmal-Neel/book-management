# Steps to deploy to ec2
1. Create an ec2 instance
2. Go inside the instance and run the below commands
3. git clone https://github.com/Nirmal-Neel/book-management.git
```
cd book-management
sudo apt-get update
sudo apt install python3-pip
pip3 install -r requirements.txt
```

# Adding self signed certificate
```
sudo apt-get install openssl
cd /etc/nginx
sudo mkdir ssl
```

```
sudo openssl req -batch -x509 -nodes -days 365 \
-newkey rsa:2048 \
-keyout /etc/nginx/ssl/server.key \
-out /etc/nginx/ssl/server.crt
```

## nginx configuration
```
sudo apt install nginx
cd /etc/nginx/sites-enabled/
sudo nano fastapi_nginx

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

```
sudo service nginx restart
```
