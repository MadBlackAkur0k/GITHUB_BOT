FROM postgres:13

ENV POSTGRES_PASSWORD=Qq12345

COPY init.sql /docker-entrypoint-initdb.d/

# Создаем директории и устанавливаем права доступа
RUN mkdir -p /oracle/pg_data/archive/ && \
    chown -R postgres:postgres /oracle/pg_data/archive/ && \
    chmod 700 /oracle/pg_data/archive/ && \
    chown -R postgres:postgres /var/lib/postgresql/data && \
    chmod 700 /var/lib/postgresql/data

USER postgres

CMD ["pg_ctl -D /var/lib/postgresql/data -l logfile start"]
