class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///lr_queue.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'supersecretkey'
