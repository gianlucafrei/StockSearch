# Setup

Folgende Anleitung zeigt Ihnen Schritt für Schritt wie Sie Stocksearch auf Ubuntu 16.04.4 x64 installieren.

### Installation Postgres 10

Als erstes müssen wir Postgres 10 auf dem System installieren. Wenn für die Dankebank jedoch ein anderer Rechner benützt werden soll überspringen Sie diesen Schritt.

```
echo 'deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main' >> /etc/apt/sources.list.d/pgdg.list
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
apt-get update
apt-get install postgresql-10
```

Nun müssen wir Postgres konfigurieren. Dafür wählen Sie ein sicheres Passwort für die Datenbank <DB-PASSWORD> und erstellen zwei neue Datenbanken.
```
sudo su postgres
    psql
        ALTER USER postgres WITH PASSWORD '<DB-PASSWORD>';
        CREATE DATABASE stocksearch;
        CREATE DATABASE stocksearchmock;
        \q
    exit
```

Nun müssen wir Postgres noch anweisen, Benutzername und Passwort als Login zu akzeptieren. Dafür müssen Sie die MD5 Methode im pg_hba.conf file erlauben.

Dafür sollten Sie folgende Zeile in Ihrer pg_hba.conf Datei hinzufügen und Postgres neu starten:

```
# for users connected via local IPv4 or IPv6 connections, always require md5
host    all   all        127.0.0.1/32          md5
```

```
vim /etc/postgresql/10/main/pg_hba.conf
    # Change file
/etc/init.d/postgresql restart
```

### Installation Python 3.6

Stocksearch benötigs Python 3.6, ebenfalls ist es zu empfehlen eine virtuelle Umgebung zu benützten. Desshalb installieren wir zusätzlich virtualenv.

```
add-apt-repository ppa:jonathonf/python-3.6
apt update

apt install python3.6
apt-get install virtualenv
```


### Installation Stocksearch

Am einfachsten clonen Sie das Git-Repository. Dazu benötigen Sie zugang zum Gitlab-Projekt, allerdings  können Sie das Repository auch kopieren.

```
# Download des Repos
git clone https://gitlab.ti.bfh.ch/freig3/project1-stocksanalytics.git
cd project1-stocksanalytics/

# Einrichtung der virtuellen Umgebung
virtualenv --python=/usr/bin/python3.6 env
source env/bin/activate

# Installation aller Dependencies mittels pip
pip install -r requirements.txt
```

### Installation Datenbankschema

Um das Schema zu in der Datenbank zu installieren füren Sie die beiden SQL-Skrips aus.

```
psql stocksearch postgres -f sql/stocksearchdump.sql
psql stocksearchmock postgres -f sql/stocksearchmockdump.sql
```

### Konfiguration

Die Zugänge zu den Datenbanken befindet sich in JSON-Konfigurationsdateien.
Erstellen Sie diese nach folgdenem Schema:

```
mkdir secured
echo '
{
    "key": "<QUANDLE-KEY>"
}
' >> secured/postgres.json

echo '{
    "db-host":    "127.0.0.1",
    "db-user":     "postgres",
    "db-password": "<DB-PASSWORD>",
    "db-database": "stocksearchmock"
}' >> secured/postgresmock.json

echo '{
    "db-host":    "127.0.0.1",
    "db-user":     "postgres",
    "db-password": "<DB-PASSWORD>",
    "db-database": "stocksear"
}' >> secured/postgres.json
```


### Start

Nun können Sie mittels folgendem Befehl Stocksearch ausführen. Wenn Sie dabei die `init` Option verwenden, werden zuerst alle Tests durchgeführt und die Dokumentation erstellt.

```
python run.py --init --host 0.0.0.0 --port 80
```

Um Stocksearch im Hintergrund zu bereiben verwenden Sie:

```
python run.py --init --host 0.0.0.0 --port 80 > /dev/null 2>&1 &
```