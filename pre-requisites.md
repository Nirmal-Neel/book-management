# Pre-requisite

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
After this step is done, please follow the **README.md**
