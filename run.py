import os
from over_achiever.api import app

if __name__ == "__main__":
    print("If you run locally, browse to localhost:5000")
    context = ('/etc/nginx/certs/server/server.crt', '/etc/nginx/certs/server/server.key')
    host = '0.0.0.0'
    port = int(os.environ.get("PORT", 5000))
    app.run(host=host, port=port, ssl_context=context, threaded=True, debug=True)
