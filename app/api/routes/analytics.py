from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_role

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

# 1) Production daily totals (great for line chart)
@router.get("/production/daily")
def production_daily(
    from_ts: datetime = Query(...),
    to_ts: datetime = Query(...),
    claims: dict = Depends(require_role({"admin", "analyst", "viewer"})),
    db: Session = Depends(get_db),
):
    tenant_id = claims["tenant_id"]
    sql = text("""
        SELECT
          date_trunc('day', event_ts) AS day,
          SUM(good_qty) AS good_qty,
          SUM(scrap_qty) AS scrap_qty
        FROM production_events
        WHERE tenant_id = :tenant_id
          AND event_ts >= :from_ts AND event_ts < :to_ts
        GROUP BY 1
        ORDER BY 1;
    """)
    return db.execute(sql, {"tenant_id": tenant_id, "from_ts": from_ts, "to_ts": to_ts}).mappings().all()

# 2) Downtime top reasons (bar chart)
@router.get("/downtime/top-reasons")
def downtime_top_reasons(
    from_ts: datetime = Query(...),
    to_ts: datetime = Query(...),
    limit: int = Query(10, ge=1, le=50),
    claims: dict = Depends(require_role({"admin", "analyst", "viewer"})),
    db: Session = Depends(get_db),
):
    tenant_id = claims["tenant_id"]
    sql = text("""
        SELECT
          reason,
          ROUND(SUM(EXTRACT(EPOCH FROM (end_ts - start_ts)) / 60.0)::numeric, 2) AS downtime_minutes
        FROM downtime_events
        WHERE tenant_id = :tenant_id
          AND start_ts >= :from_ts AND start_ts < :to_ts
        GROUP BY reason
        ORDER BY downtime_minutes DESC
        LIMIT :limit;
    """)
    return db.execute(sql, {"tenant_id": tenant_id, "from_ts": from_ts, "to_ts": to_ts, "limit": limit}).mappings().all()

# 3) Data-quality issues summary (stacked bar / KPI)
@router.get("/data-quality/issues-summary")
def dq_issues_summary(
    from_ts: datetime = Query(...),
    to_ts: datetime = Query(...),
    claims: dict = Depends(require_role({"admin", "analyst", "viewer"})),
    db: Session = Depends(get_db),
):
    tenant_id = claims["tenant_id"]
    sql = text("""
        SELECT
          severity,
          system_name,
          COUNT(*) AS issue_count
        FROM data_quality_issues
        WHERE tenant_id = :tenant_id
          AND detected_ts >= :from_ts AND detected_ts < :to_ts
          AND status = 'open'
        GROUP BY severity, system_name
        ORDER BY issue_count DESC;
    """)
    return db.execute(sql, {"tenant_id": tenant_id, "from_ts": from_ts, "to_ts": to_ts}).mappings().all()
