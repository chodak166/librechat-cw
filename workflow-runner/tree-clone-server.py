import http.server
import socketserver
import os
import base64
import urllib.parse
import shlex

PORT = os.getenv('TREE_CLONE_PORT', 8001)
PREFIX = os.getenv('TREE_CLONE_PREFIX', '/app/ai-workspace')

class Handler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        # Parse query parameters
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        dir_path = params.get('src', [None])[0]
        local_path = params.get('dst', [None])[0]

        if not local_path:
            local_path = './'

        if not dir_path:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing 'src' parameter")
            return

        dir_path = os.path.join(PREFIX, dir_path)
        print("Cloning directory:", dir_path)
        if not os.path.exists(dir_path):
            print("Directory not found:", dir_path)
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Directory not found")
            return

        # Generate the replication script
        script = self.generate_script(dir_path, local_path)

        # Send the script as the response
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(script.encode())

    def generate_script(self, dir_path, local_path):
        script_lines = []
        script_lines.append("#!/bin/bash\n")
        script_lines.append(f"mkdir -p {shlex.quote(local_path)}\n")

        for root, dirs, files in os.walk(dir_path):
            rel_root = os.path.relpath(root, dir_path)
            local_root = os.path.join(local_path, rel_root)
            local_root_quoted = shlex.quote(local_root)

            # Create directories
            for d in dirs:
                dir_path_quoted = shlex.quote(os.path.join(local_root, d))
                script_lines.append(f"mkdir -p {dir_path_quoted}\n")

            # Create files
            for f in files:
                file_path = os.path.join(root, f)
                with open(file_path, "rb") as file:
                    encoded_content = base64.b64encode(file.read()).decode('utf-8')
                    file_path_quoted = shlex.quote(os.path.join(local_root, f))
                    script_lines.append(f"echo '{encoded_content}' | base64 -d > {file_path_quoted}\n")

        return "".join(script_lines)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving on port {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            httpd.server_close()
