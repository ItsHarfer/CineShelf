# File: app/events.py
"""
Purpose:
    Enable SQLite foreign key support on each new database connection.

Features:
    - Listens for SQLAlchemy Engine "connect" events
    - Executes PRAGMA to turn on foreign key enforcement in SQLite

Required Modules:
    - logging: application logging
    - sqlalchemy.event: event listener registration
    - sqlalchemy.engine.Engine: target for event

Author:
    Martin Haferanke

Date:
    2025-07-18
"""
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Module-level logger
logger = logging.getLogger(__name__)


@event.listens_for(Engine, "connect")
def _enable_sqlite_fk(dbapi_con, con_record) -> None:
    """
    Enable SQLite foreign key constraint enforcement on new DBAPI connections.

    :param dbapi_con: DBAPI connection object
    :param con_record: Connection record (unused)
    :raises Exception: if PRAGMA execution fails
    """
    try:
        cursor = dbapi_con.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
        logger.info("SQLite foreign key enforcement enabled.")
    except Exception as e:
        logger.exception("Failed to enable SQLite foreign keys: %s", e)
        raise
