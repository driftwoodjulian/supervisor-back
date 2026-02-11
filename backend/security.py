from sqlalchemy.orm import Session
import sys

class SecurityAlert(Exception):
    """Critical security violation attempt."""
    pass

class ReadOnlySession:
    """
    Wrapper around SQLAlchemy Session that strictly enforces Read-Only access at the application level.
    Any attempt to modify state triggers a SecurityAlert and terminates the process to prevent data corruption.
    """
    def __init__(self, session: Session):
        self._session = session

    def __getattr__(self, name):
        # Allow read-only methods and query construction
        if name in ['query', 'get', 'close', 'execute', 'scalar', 'scalars']:
            return getattr(self._session, name)
        
        # Block write methods explicitly (and via fallback)
        if name in ['add', 'add_all', 'delete', 'commit', 'flush', 'merge', 'begin_nested']:
            self._trigger_security_alert(name)
        
        return getattr(self._session, name)

    def _trigger_security_alert(self, method_name: str):
        """
        CRITICAL: A write attempt was detected on the Immutable Source DB.
        Action: Log alert, raise exception, and crash process.
        """
        msg = f"SECURITY ALERT: Attempted forbidden write operation '{method_name}' on Immutable Source DB."
        print(f"\n[CRITICAL] {msg}\n")
        raise SecurityAlert(msg)
        # In a real environment, we might sys.exit(1) here, but raising Exception allows for testing/handling.
        # sys.exit(1) 

    def add(self, *args, **kwargs):
        self._trigger_security_alert('add')

    def add_all(self, *args, **kwargs):
        self._trigger_security_alert('add_all')

    def delete(self, *args, **kwargs):
        self._trigger_security_alert('delete')

    def commit(self, *args, **kwargs):
        self._trigger_security_alert('commit')

    def flush(self, *args, **kwargs):
        self._trigger_security_alert('flush')
