import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy_utils import database_exists, create_database

if not os.environ.get('DB'):
    raise EnvironmentError("Database connection is not setup.")

engine = create_engine(os.environ.get('DB'), pool_recycle=3600, pool_size=500,
                       isolation_level='AUTOCOMMIT')

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

if not database_exists(engine.url):
    create_database(engine.url)