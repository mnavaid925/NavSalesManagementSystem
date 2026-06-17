"""Project bootstrap that runs before Django reads settings.

Two jobs:
  1. Register PyMySQL as the `MySQLdb` driver (pure-python, no compiler on Windows).
  2. Apply a compatibility shim for MariaDB < 10.5 — XAMPP ships MariaDB 10.4, but
     Django 5.1 sets the MySQL/MariaDB version floor to 10.5 and would refuse to
     connect. We relax that floor. INSERT ... RETURNING is gated on
     `mysql_version >= (10, 5)` in Django's own feature flags, so on 10.4 it is
     already disabled automatically. See .claude/tasks/lessons.md (L4).
"""
import pymysql

pymysql.install_as_MySQLdb()


def _apply_mariadb_10_4_shim():
    """Make Django 5.1 talk to XAMPP's MariaDB 10.4.

    Two things must change:
      1. Lower the version floor (Django 5.1 requires MariaDB >= 10.5).
      2. Disable INSERT ... RETURNING. Because 10.5 is Django's minimum, it now
         enables RETURNING for *any* MariaDB without a version sub-check, so on
         10.4 (which has no RETURNING) we must turn the feature flags off
         explicitly — assigning plain values overrides the cached_property
         descriptors for every connection. (lesson L4)
    """
    try:
        from django.db.backends.mysql.features import DatabaseFeatures
        DatabaseFeatures.minimum_database_version = (10, 4)
        DatabaseFeatures.can_return_columns_from_insert = False
        DatabaseFeatures.can_return_rows_from_bulk_insert = False
    except Exception:
        pass
    try:
        from django.db.backends.mysql.base import DatabaseWrapper
        # Belt-and-suspenders for this single dev DB: never raise on the version floor.
        DatabaseWrapper.check_database_version_supported = lambda self: None
    except Exception:
        pass


_apply_mariadb_10_4_shim()
