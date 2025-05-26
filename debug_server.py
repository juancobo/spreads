#!/usr/bin/env python
# Debug script to investigate Tornado server issues

import os
import sys
import tornado.ioloop
import tornado.web
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('debug-server')

# Simple request handler
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Debug server is working!")

def main():
    # Configure and start the server
    app = tornado.web.Application([
        (r"/", MainHandler),
    ])
    
    port = 3000
    logger.info(f"Attempting to start server on port {port}")
    
    try:
        # Try to listen on the port
        app.listen(port)
        logger.info(f"Server successfully started on port {port}")
        print(f"Debug server is running at http://localhost:{port}")
        
        # Start the IO loop
        tornado.ioloop.IOLoop.current().start()
    except Exception as e:
        logger.error(f"Failed to start server: {type(e).__name__}: {e}")
        print(f"Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print(f"Starting debug server from {os.path.abspath(__file__)}")
    print(f"Python version: {sys.version}")
    print(f"Tornado version: {tornado.version}")
    main()
