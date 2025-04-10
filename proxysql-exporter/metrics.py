import pymysql
import prometheus_client
from prometheus_client import Gauge
import time

def connect_to_proxysql(max_retries=5, delay=5):
    """Connect to ProxySQL with retries."""
    for attempt in range(max_retries):
        try:
            connection = pymysql.connect(
                host='proxysql',  # container name
                port=6032,
                user='radmin',
                password='radmin',
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection  # Connected successfully
        except pymysql.MySQLError as e:
            print(f"Connection attempt {attempt+1} failed: {e}")
            time.sleep(delay)
    raise Exception("Failed to connect to ProxySQL after multiple retries")

# === Metric Definitions ===
#backend_servers_online = Gauge('proxysql_backend_servers_online', 'Number of backend servers ONLINE')
#backend_servers_offline = Gauge('proxysql_backend_servers_offline', 'Number of backend servers OFFLINE')

#pool_conn_used = Gauge('proxysql_pool_conn_used', 'Number of used connections in connection pool')
#pool_conn_free = Gauge('proxysql_pool_conn_free', 'Number of free connections in connection pool')
#pool_conn_errors = Gauge('proxysql_pool_conn_errors', 'Number of connection errors in connection pool')

#query_digest_count = Gauge('proxysql_query_digest_count', 'Number of times query patterns were executed')
#query_digest_latency = Gauge('proxysql_query_digest_avg_latency', 'Average latency of query patterns')

memory_usage_bytes = Gauge('proxysql_memory_usage_bytes', 'Memory usage of ProxySQL in bytes')
uptime_seconds = Gauge('proxysql_uptime_seconds', 'Uptime of ProxySQL in seconds')
# === Metric Fetching Functions ===

def fetch_backend_server_status(cursor):
    """Fetch backend servers online/offline count."""
    cursor.execute("SELECT status, count(*) as cnt FROM mysql_servers GROUP BY status;")
    statuses = {row['status']: row['cnt'] for row in cursor.fetchall()}
    backend_servers_online.set(statuses.get('ONLINE', 0))
    backend_servers_offline.set(statuses.get('OFFLINE_SOFT', 0) + statuses.get('OFFLINE_HARD', 0))

def fetch_connection_pool_metrics(cursor):
    """Fetch connection pool statistics."""
    cursor.execute("SELECT sum(ConnUsed) as used, sum(ConnFree) as free, sum(conn_errors_tcp) as errors FROM stats_mysql_connection_pool;")
    result = cursor.fetchone()
    pool_conn_used.set(result['used'] or 0)
    pool_conn_free.set(result['free'] or 0)
    pool_conn_errors.set(result['errors'] or 0)

def fetch_query_digest_metrics(cursor):
    """Fetch query digest statistics."""
    cursor.execute("SELECT sum(count_star) as total_queries, avg(avg_us) as avg_latency FROM stats_mysql_query_digest;")
    result = cursor.fetchone()
    query_digest_count.set(result['total_queries'] or 0)
    query_digest_latency.set(result['avg_latency'] or 0)

def fetch_internal_metrics(cursor):
    """Fetch internal ProxySQL stats like memory and uptime."""
    cursor.execute("SELECT Variable_Name, Variable_Value FROM stats_mysql_global WHERE Variable_Name IN ('Uptime', 'Bytes_data');")
    for row in cursor.fetchall():
        if row['Variable_Name'] == 'Uptime':
            uptime_seconds.set(row['Variable_Value'])
        elif row['Variable_Name'] == 'Bytes_data':
            memory_usage_bytes.set(row['Variable_Value'])


def generate_metrics():
    try:
        connection = connect_to_proxysql()
        cursor = connection.cursor()

        fetch_backend_server_status(cursor)
        fetch_connection_pool_metrics(cursor)
        #fetch_query_digest_metrics(cursor)
        fetch_internal_metrics(cursor)

        cursor.close()
        connection.close()

        return prometheus_client.generate_latest()
    except Exception as e:
        return f"# Error: {str(e)}\n"
# This function generates Prometheus metrics for ProxySQL.