from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlalchemy import text
from app.db.session import engine
from app.core.security import hash_password

def seed():
    now = datetime.now(timezone.utc)

    tenant_a = str(uuid4())
    tenant_b = str(uuid4())

    user_a = str(uuid4())
    user_b = str(uuid4())

    # machines
    m1 = str(uuid4())
    m2 = str(uuid4())
    m3 = str(uuid4())
    m4 = str(uuid4())

    pw_hash = hash_password("Pass123!")

    with engine.begin() as conn:
        # tenants
        conn.execute(text("INSERT INTO tenants (id, name) VALUES (:id, :name) ON CONFLICT DO NOTHING"),
                     [{"id": tenant_a, "name": "CustomerA"}, {"id": tenant_b, "name": "CustomerB"}])

        # users (same password for demo)
        conn.execute(text("""
            INSERT INTO users (id, tenant_id, email, password_hash, role, is_active)
            VALUES (:id, :tenant_id, :email, :ph, :role, true)
            ON CONFLICT (email) DO NOTHING
        """), [
            {"id": user_a, "tenant_id": tenant_a, "email": "analyst@customera.com", "ph": pw_hash, "role": "analyst"},
            {"id": user_b, "tenant_id": tenant_b, "email": "analyst@customerb.com", "ph": pw_hash, "role": "analyst"},
        ])

        # machines
        conn.execute(text("""
            INSERT INTO machines (id, tenant_id, machine_code, machine_name)
            VALUES (:id, :tenant_id, :code, :name)
            ON CONFLICT (tenant_id, machine_code) DO NOTHING
        """), [
            {"id": m1, "tenant_id": tenant_a, "code": "CNC-01", "name": "CNC Machine 01"},
            {"id": m2, "tenant_id": tenant_a, "code": "ASM-02", "name": "Assembly Line 02"},
            {"id": m3, "tenant_id": tenant_b, "code": "CNC-99", "name": "CNC Machine 99"},
            {"id": m4, "tenant_id": tenant_b, "code": "PKG-10", "name": "Packaging 10"},
        ])

        # production events (last 14 days)
        prod_rows = []
        for i in range(14):
            day = now - timedelta(days=13 - i)
            prod_rows.append({"id": str(uuid4()), "tenant_id": tenant_a, "machine_id": m1,
                              "event_ts": day, "good": 100 + i*3, "scrap": i % 3})
            prod_rows.append({"id": str(uuid4()), "tenant_id": tenant_a, "machine_id": m2,
                              "event_ts": day, "good": 80 + i*2, "scrap": (i+1) % 4})
            prod_rows.append({"id": str(uuid4()), "tenant_id": tenant_b, "machine_id": m3,
                              "event_ts": day, "good": 120 + i*4, "scrap": (i+2) % 5})
            prod_rows.append({"id": str(uuid4()), "tenant_id": tenant_b, "machine_id": m4,
                              "event_ts": day, "good": 60 + i*1, "scrap": (i+3) % 2})

        conn.execute(text("""
            INSERT INTO production_events (id, tenant_id, machine_id, event_ts, good_qty, scrap_qty)
            VALUES (:id, :tenant_id, :machine_id, :event_ts, :good, :scrap)
        """), prod_rows)

        # downtime events (few sample)
        conn.execute(text("""
            INSERT INTO downtime_events (id, tenant_id, machine_id, start_ts, end_ts, reason)
            VALUES (:id, :tenant_id, :machine_id, :start_ts, :end_ts, :reason)
        """), [
            {"id": str(uuid4()), "tenant_id": tenant_a, "machine_id": m1,
             "start_ts": now - timedelta(days=2, hours=5), "end_ts": now - timedelta(days=2, hours=4, minutes=10),
             "reason": "Tool Change"},
            {"id": str(uuid4()), "tenant_id": tenant_a, "machine_id": m2,
             "start_ts": now - timedelta(days=1, hours=3), "end_ts": now - timedelta(days=1, hours=2, minutes=20),
             "reason": "Material Shortage"},
            {"id": str(uuid4()), "tenant_id": tenant_b, "machine_id": m3,
             "start_ts": now - timedelta(days=3, hours=2), "end_ts": now - timedelta(days=3, hours=1, minutes=5),
             "reason": "Maintenance"},
        ])

        # data quality issues
        conn.execute(text("""
            INSERT INTO data_quality_issues (id, tenant_id, system_name, severity, issue_type, field_name, record_id, detected_ts, status)
            VALUES (:id, :tenant_id, :system, :severity, :type, :field, :record, :ts, :status)
        """), [
            {"id": str(uuid4()), "tenant_id": tenant_a, "system": "ERP", "severity": "high",
             "type": "Missing Field", "field": "standard_time", "record": "OP-1023", "ts": now - timedelta(days=5), "status": "open"},
            {"id": str(uuid4()), "tenant_id": tenant_a, "system": "MES", "severity": "medium",
             "type": "Inconsistent Value", "field": "work_center", "record": "WC-12", "ts": now - timedelta(days=6), "status": "open"},
            {"id": str(uuid4()), "tenant_id": tenant_b, "system": "WMS", "severity": "critical",
             "type": "Outdated Record", "field": "location", "record": "BIN-77", "ts": now - timedelta(days=2), "status": "open"},
        ])

    print("Seed complete.")
    print("Demo users:")
    print(" - analyst@customera.com / Pass123!")
    print(" - analyst@customerb.com / Pass123!")
