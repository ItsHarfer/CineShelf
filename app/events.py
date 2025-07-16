import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Set up module-level logger
logger = logging.getLogger(__name__)


@event.listens_for(Engine, "connect")
def _enable_sqlite_fk(dbapi_con, con_record):
    # bei SQLite den Foreign-Key-Support einschalten
    cursor = dbapi_con.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
