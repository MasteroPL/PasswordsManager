FROM mysql:5.7
COPY ./initdb/ /docker-entrypoint-initdb.d/
COPY ./custom.cnf /etc/mysql/conf.d/custom.cnf
