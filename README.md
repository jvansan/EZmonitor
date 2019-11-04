# EZmonitor

A simple web app designed to monitor websites.

Uses Postgres database for storing data.

Built with ❤ using Python+Tornado.

--- 

### Configuration

EZmonitor uses a YAML based configuration. See below of `TEMPLATE.config.yaml`.

```YAML
database:
  user: <USERNAME> # default to postgres
  password: <PASSWORD> # default to ""
  db: <DATABASENAME> # default to test
  host: <HOSTNAME> # default to localhost
  port: <PORTNAME> # default to 5432
```


#### SQL Definitions

```sql
CREATE TABLE IF NOT EXISTS website(
    id SERIAL PRIMARY KEY,
    name TEXT,
    url TEXT,
    port INT
)
CREATE TABLE IF NOT EXISTS website_result(
    website_id INT PRIMARY KEY,
    peername TEXT,
    certificate_issuer TEXT,
    certificate_start_date DATE,
    certificate_end_date DATE
)
```