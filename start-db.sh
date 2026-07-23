sudo apt-get update && sudo apt-get install -y postgresql postgresql-contrib && sudo service postgresql start
sudo -u postgres psql -c "CREATE USER episense WITH PASSWORD 'episense' SUPERUSER;"
sudo -u postgres psql -c "CREATE DATABASE episense_test;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE episense_test TO episense;"
