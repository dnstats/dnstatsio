import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy_utils import database_exists, create_database


engine = create_engine(os.environ.get('DB'), pool_recycle=3600, pool_size=250,
                       isolation_level='AUTOCOMMIT')

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

if not database_exists(engine.url):
    create_database(engine.url)