FROM postgres:latest

# install Python 3
RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get -y install python3.7-dev
RUN apt-get -y install postgresql-server-dev-10 gcc python3-dev musl-dev

# install psycopg2 library with PIP
RUN pip3 install psycopg2

# add the 'postgres' admin role

# expose Postgres port
EXPOSE 5432

# bind mount Postgres volumes for persistent data
VOLUME ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]
USER postgres
#RUN chown -R postgres:postgres /etc/postgresql
#RUN chown -R postgres:postgres /var/log/postgresql
#RUN chown -R postgres:postgres /var/lib/postgresql
