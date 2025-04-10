from prometheus_client.core import GaugeMetricFamily, REGISTRY
import pymysql
from metrics import connect_to_proxysql  # or define locally

class ProxySQLCollector(object):
    def collect(self):
        connection = connect_to_proxysql()
        cursor = connection.cursor()

        ## Top Query Digest Metrics
        cursor.execute("""
            SELECT 
                digest_text,
                sum(count_star) as total_queries,
                sum(sum_time) as total_latency
            FROM stats_mysql_query_digest
            GROUP BY digest_text
            ORDER BY total_queries DESC
            LIMIT 5;
        """)
        rows = cursor.fetchall()

        for row in rows:
            digest = row['digest_text'] or "unknown_query"
            
            g_query_count = GaugeMetricFamily(
                'proxysql_query_digest_count',
                'Count of query patterns',
                labels=['digest']
            )
            g_query_count.add_metric([digest], row['total_queries'] or 0)
            yield g_query_count

            g_query_latency = GaugeMetricFamily(
                'proxysql_query_digest_latency',
                'Total latency of query patterns (microseconds)',
                labels=['digest']
            )
            g_query_latency.add_metric([digest], row['total_latency'] or 0)
            yield g_query_latency

        ## Connection Pool Metrics
        cursor.execute("""
            SELECT 
                SUM(ConnUsed) as conn_used,
                SUM(ConnFree) as conn_free
            FROM stats_mysql_connection_pool;
        """)
        row = cursor.fetchone()
        g_conn_used = GaugeMetricFamily('proxysql_pool_conn_used', 'Number of used connections in pool')
        g_conn_used.add_metric([], row['conn_used'] or 0)
        yield g_conn_used

        g_conn_free = GaugeMetricFamily('proxysql_pool_conn_free', 'Number of free connections in pool')
        g_conn_free.add_metric([], row['conn_free'] or 0)
        yield g_conn_free

        ## Backend Servers Online
        cursor.execute("""
            SELECT 
              COUNT(*) as backend_online 
            FROM mysql_servers 
            WHERE status = 'ONLINE';
        """)
        row = cursor.fetchone()
        g_backend_online = GaugeMetricFamily('proxysql_backend_servers_online', 'Number of backend servers ONLINE')
        g_backend_online.add_metric([], row['backend_online'] or 0)
        yield g_backend_online

        ## Bytes Traffic (Sent / Received)
        cursor.execute("""
            SELECT
              SUM(Bytes_data_sent) as bytes_sent,
              SUM(Bytes_data_recv) as bytes_recv
            FROM stats_mysql_connection_pool;
        """)
        row = cursor.fetchone()
        g_bytes_sent = GaugeMetricFamily('proxysql_bytes_sent', 'Total bytes sent to backend')
        g_bytes_sent.add_metric([], row['bytes_sent'] or 0)
        yield g_bytes_sent

        g_bytes_recv = GaugeMetricFamily('proxysql_bytes_received', 'Total bytes received from backend')
        g_bytes_recv.add_metric([], row['bytes_recv'] or 0)
        yield g_bytes_recv

        cursor.close()
        connection.close()
        