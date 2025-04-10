from flask import Flask, Response
from metrics import generate_metrics
from prometheus_client import REGISTRY
from proxysql_collector import ProxySQLCollector
import prometheus_client

app = Flask(__name__)

REGISTRY.register(ProxySQLCollector())

@app.route('/metrics')
def metrics():
    return Response(prometheus_client.generate_latest(), mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9104)
    # app.run(debug=True)
    # Uncomment the above line for debugging purposes