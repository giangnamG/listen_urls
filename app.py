from flask import Flask, request, send_from_directory
import sqlite3, json
import init_db
from urllib.parse import urlparse
from datetime import datetime
import random, base64, html, os
app = Flask(__name__)

@app.route('/', methods=['GET'])

def index():
    try:
        query = request.args.get('query')
        if query.startswith('http'):
            parsed_url = urlparse(query)
            row = {
                'scheme': parsed_url.scheme,
                'host': parsed_url.netloc,
                'path': parsed_url.path,
                'params': parsed_url.params,
                'query': parsed_url.query,
                'fragment': parsed_url.fragment,
                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            table_name = 'urls'
        elif query != '':
            print(query)
            row = {
                'string': query,
                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            table_name = 'strings'
        else:
            row = None
            
        if row is not None:
            con = sqlite3.connect('database.sqlite')
            if table_name == 'urls':
                con.execute(f'''
                    insert into {table_name} (scheme, host, path, params, query, fragment, time) values (?,?,?,?,?,?,?)
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
            elif table_name == 'strings':
                con.execute(f'''
                    insert into {table_name} (string, time) values (?,?)
                    ''', 
                    (   row['string'],
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
    
    _type = request.args.get('type')
    logs = []
    
    if _type == 'urls':
        res = cur.execute('select * from urls order by time desc limit 5')
        rows = res.fetchall()
        res.close()
        con.close()
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
        count = len(rows)
    elif _type == 'string':
        res = cur.execute('select * from strings order by time desc limit 5')
        rows = res.fetchall()
        res.close()
        con.close()
        for row in rows:
            logs.append({
                'string': row[1],
                'time': row[2]
            })
        count = len(rows)
        
    if count >= 50:
        init_db.reset_db()
        
    return json.dumps(logs, indent=4)

@app.route('/create_payload', methods=['GET','POST'])
def create_payload():
    if request.method == 'GET':
        return '''
        <div>Create payload</div>
        <form method="POST">
            <label for="payload">Payload:</label><br>
            <textarea name="payload" rows=20 cols=100></textarea>
            <br>
            <button type="submit" name="store">Store</button>
        </form>
    '''
    elif request.method == 'POST':
        payload = request.form.get('payload')
        code_identifier = random.randint(100000,999999)
        con = sqlite3.connect('database.sqlite')
        cur = con.cursor()
        cur.execute('insert into payloads (code_identifier, payload, time) values (?,?,?)', (code_identifier, base64.b64encode(payload.encode()).decode(), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        con.commit()
        con.close()
        return f'''
            Payload stored successfully <a href="/payloads/{code_identifier}">View payload</a>'''
@app.route('/payloads/<code_identifier>', methods=['GET'])
def payloads(code_identifier):
    try:
        con = sqlite3.connect('database.sqlite')
        cur = con.cursor()
        res = cur.execute(f'select * from payloads where code_identifier = {code_identifier} limit 1')
        rows = cur.fetchall()
        payload = base64.b64decode(rows[0][2]).decode()
        print(payload)
        return html.escape(payload) 
    except Exception as e:
        return f'Error: {str(e)}'

@app.route('/upload', methods=['GET','POST'])
def upload():
    UPLOAD_DIRECTORY = './uploads'
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        ext = '.'.join(filename.split('.')[1:])
        name = filename.split('.')[0]+'_'+str(random.randint(100000,999999))+'.'+ext
        filepath = os.path.join(UPLOAD_DIRECTORY, name)
        file.save(filepath)
        return f"""File '{filename}' uploaded successfully.<br>
                <a href='{filepath}'>View file {filepath}</a><br>
                <a href="/file_contents/{name}">view contents</a>
                """
    else:
        return '''
        <div>Upload a file</div>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file">
            <button type="submit" name="upload">Upload</button>
        </form>
        '''
@app.route('/uploads/', methods=['GET'])
def uploads():
    files = os.listdir('./uploads')
    if len(files) > 50:
        os.system('rm -rf /uploads/*')
        return 'cleaned! empty folder uploaded'
    views = '<br>'.join(f'<a href="/uploads/{file}">{file}</a> <a href="/file_contents/{file}">contents</a>' for file in files)
    return views
@app.route('/uploads/<filename>', methods=['GET'])
def view_file(filename):
    UPLOAD_DIRECTORY = './uploads'
    filepath = os.path.join(UPLOAD_DIRECTORY, filename)
    if os.path.isfile(filepath):
        return send_from_directory(UPLOAD_DIRECTORY, filename)
    else:
        return "File not found."
@app.route('/file_contents/<filename>', methods=['GET'])
def file_contents(filename):
    UPLOAD_DIRECTORY = './uploads'
    filepath = os.path.join(UPLOAD_DIRECTORY, filename)
    try:
        contents = open(filepath, 'r').read()
        print(contents)
        return {
            'filename': filename,
            'contents': contents
        }
    except:
        return send_from_directory(UPLOAD_DIRECTORY, filename)
    
if __name__ == '__main__':
    init_db.run()
    app.run(host='0.0.0.0', port=5000, debug=True)