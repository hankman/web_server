bind = '127.0.0.1:5000'
worker_class = 'sync'
loglevel = 'info'
accesslog = '/home/cfan/web_server/log/access.log'
access_log_format = "%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s"
errorlog = '/home/cfan/web_server/log/error.log'
workers = 3
