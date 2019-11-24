from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session


engine = create_engine('postgres://mburket@/dnstats', pool_recycle=3600, pool_size=100)

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
