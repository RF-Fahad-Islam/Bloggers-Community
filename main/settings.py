from . import db
# Flask Sqlalchemy Configuration
SQLALCHEMY_DATABASE_URI = "postgres://qdzxyoyoikdnzu:6810cdb1500d454eba19ff444a0ac92cdf12d5c5abbc3e7d232b5a0d685ac2bb@ec2-44-209-158-64.compute-1.amazonaws.com:5432/d3rm5t480v7qmo"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "Supersecretkey"
#Flask Session Configuration
SESSION_TYPE = 'sqlalchemy'
SESSION_SQLALCHEMY = db