from db import get_connection
from flask import session
import json

def log_action(action, entity_type="", entity_id="", metadata=None):
    """
    Log an activity to the activity_log table.
    
    Args:
        action: The action performed (e.g., "CREATE", "UPDATE", "DELETE")
        entity_type: Type of entity (e.g., "STUDENT", "USER")
        entity_id: ID of the affected entity
        metadata: Optional dict with additional info
    """
    user_id = session.get("user_id")
    ip_address = ""  # You can get this from request.remote_addr if needed
    
    if metadata is None:
        metadata = {}

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO activity_log (user_id, action, entity_type, entity_id, metadata, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user_id, action, entity_type, entity_id, json.dumps(metadata), ip_address)
        )
        conn.commit()
    finally:
        cur.close()
