import http.server
import socketserver
import sys
import os

def run_server(directory, port):
    # Change the current directory to the specified directory
    os.chdir(directory)

    # Define a simple handler to serve files from the specified directory
    handler = http.server.SimpleHTTPRequestHandler

    # Set up the HTTP server
    with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
        print(f"Serving files from {directory} on port {port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
            httpd.shutdown()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python server.py <directory> <port>")
        sys.exit(1)

    directory = sys.argv[1]
    port = int(sys.argv[2])

    run_server(directory, port)
