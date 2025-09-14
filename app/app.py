from flask import Flask
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import boto3
from datetime import datetime

app = Flask(__name__)

ssm = boto3.client('ssm')
DB_HOST = ssm.get_parameter(Name='/app/db/host')['Parameter']['Value']
DB_NAME = 'appdb'
DB_USER = ssm.get_parameter(Name='/app/db/user')['Parameter']['Value']
DB_PASS = ssm.get_parameter(Name='/app/db/pass', WithDecryption=True)['Parameter']['Value']
PORT = int(os.environ.get('PORT', 5000))
cloudwatch = boto3.client('cloudwatch')

@app.route('/')
def home():
    cloudwatch.put_metric_data(Namespace='App', MetricData=[{
        'MetricName': 'Requests',
        'Value': 1,
        'Unit': 'Count',
        'Timestamp': datetime.utcnow()
    }])
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        cur.close()
        conn.close()
        return f"<h1>Users from RDS (Pi Credit App):</h1><ul>{''.join([f'<li>{user['name']}</li>' for user in users])}</ul>"
    except Exception as e:
        return f"<h1>Error connecting to RDS: {str(e)}</h1>"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
