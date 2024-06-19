from flask import Flask, request
import sqlite3, json
import init_db
from urllib.parse import urlparse
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET'])

def index():
    try:
        query = request.args.get('query')
        if query.startswith('http'):
            parsed_url = urlparse(query)
            print(parsed_url)
            row = {
                'scheme': parsed_url.scheme,
                'host': parsed_url.netloc,
                'path': parsed_url.path,
                'params': parsed_url.params,
                'query': parsed_url.query,
                'fragment': parsed_url.fragment,
                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            row = None
        if row is not None:
            con = sqlite3.connect('database.sqlite')
            
            con.execute('''
                insert into urls (scheme, host, path, params, query, fragment, time) values (?,?,?,?,?,?,?)
                ''', 
                (   row['scheme'], 
                    row['host'], 
                    row['path'], 
                    row['params'], 
                    row['query'],
                    row['fragment'], 
                    row['time']
                )
            )
            con.commit()
            con.close()
        return json.dumps(row)
    except Exception as e:
        return '{}'
@app.route('/get_logs', methods=['GET'])
def get_logs():
    con = sqlite3.connect('database.sqlite')
    cur = con.cursor()
        
    res = cur.execute('select * from urls order by time desc limit 5')
    rows = res.fetchall()
    res.close()
    con.close()
    logs = []
    for row in rows:
        logs.append({
            'scheme': row[1],
            'host': row[2],
            'path': row[3],
            'params': row[4],
            'query': row[5],
            'fragment': row[6],
            'time': row[7]
        })

    return json.dumps(logs, indent=4)

if __name__ == '__main__':
    init_db.run()
    app.run(host='0.0.0.0', port=5000, debug=True)