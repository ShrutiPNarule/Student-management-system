from functools import wraps
from flask import session, redirect, url_for, flash

# -------------------------------------------------
# ROLE-BASED ACCESS CONTROL (RBAC) DECORATOR
# -------------------------------------------------
def require_roles(*allowed_roles):
    """
    Usage:
    @require_roles("admin", "auditor")
    def function():
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):

            # ---------- LOGIN CHECK ----------
            if "user_email" not in session:
                flash("Please login to continue.", "error")
                return redirect(url_for("login"))

            # ---------- ROLE CHECK ----------
            user_role = session.get("role")   # ✅ CONSISTENT SESSION KEY

            if user_role not in allowed_roles:
                flash("You are not allowed to perform this action.", "error")
                return redirect(url_for("index"))

            return view_func(*args, **kwargs)

        return wrapped
    return decorator


# -------------------------------------------------
# ROUTE IMPORTS
# -------------------------------------------------

# Core pages
from .index_route import *

# CRUD operations
from .add_route import *
from .edit_route import *
from .delete_route import *
from .recycle_bin_route import *

# Authentication
from .login_route import *
from .register_route import *
from .verify_otp import *
from .logout_route import *
from .remove_logged_account import *
from .resend_otp import *
from .forgot_password import *

# Logs / audit
from .log_route import *
