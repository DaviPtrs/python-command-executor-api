import http.server
import socketserver
import os
import subprocess

PATH = os.getenv('PYTHONPATH', os.getcwd())
PORT = int(os.getenv('PORT', 8080))

class MyHandler(http.server.BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    
    def do_GET(self):
        name = self.path[1:]
        self._set_response()
        response = ""
        response += self.exec_command(name)
        self.wfile.write(response.encode('utf_8'))

    def exec_command(self, name):
        scripts = os.listdir(PATH + '/scripts')
        if name in scripts:
            self.log_message(f"Executing script: {name}")
            try:
                proc = subprocess.Popen([f"{PATH}/scripts/{name}"], 
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
                (output, err) = proc.communicate()
                if err.decode('utf-8') != '':
                    output = f"{output.decode('utf-8')}\n{err.decode('utf-8')}"
                else:
                    output = output.decode('utf-8')
                response = f"Script output: {output}"
                self.log_message(response)
                return response
            except PermissionError as e:
                message = e.strerror + ': ' + e.filename
                self.log_error(message)
                return message
        else:
            response = f"No such command named by \"{name}\""
            return response

Handler = MyHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()