#!/usr/bin/env python
# Simple test server to check port binding

import tornado.ioloop
import tornado.web
from tornado.web import Application, RequestHandler
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test-server")

class MainHandler(RequestHandler):
    def get(self):
        self.write("Hello, world! Test server is running.")

def main():
    port = 3000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    app = Application([
        (r"/", MainHandler),
    ])
    
    try:
        logger.info(f"Attempting to start server on port {port}")
        app.listen(port)
        logger.info(f"Server successfully started on port {port}")
        print(f"Server running at http://localhost:{port}/")
        tornado.ioloop.IOLoop.current().start()
    except OSError as e:
        logger.error(f"Could not start server on port {port}: {e}")
        print(f"ERROR: Could not start server on port {port}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {e}")
        print(f"ERROR: Unexpected error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    main()
