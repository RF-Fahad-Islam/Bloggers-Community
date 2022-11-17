PROD= True
SQLALCHEMY_DATABASE_URI_PROD = "postgresql://bloggers_community_user:SBSIwvrOMsiHjhPw6cfpZyEjmpkUIgI6@dpg-cdqs2mmn6mpqj2cjcncg-a/bloggers_community"
SQLALCHEMY_DATABASE_URI_DEV = "postgresql://bloggers_community_user:SBSIwvrOMsiHjhPw6cfpZyEjmpkUIgI6@dpg-cdqs2mmn6mpqj2cjcncg-a.singapore-postgres.render.com/bloggers_community"
# Flask Sqlalchemy Configuration
SQLALCHEMY_DATABASE_URI = "postgres://qdzxyoyoikdnzu:6810cdb1500d454eba19ff444a0ac92cdf12d5c5abbc3e7d232b5a0d685ac2bb@ec2-44-209-158-64.compute-1.amazonaws.com:5432/d3rm5t480v7qmo"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "Supersecretkey"
#Flask Session Configuration
SESSION_TYPE = 'sqlalchemy'