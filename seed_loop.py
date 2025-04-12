from supabase import create_client
import os
from datetime import datetime, timedelta
import numpy as np

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

domains = ['loan', 'customer', 'risk', 'investment', 'kyc']
run_date = datetime.now().isoformat()
np.random.seed()

rows = []
for domain in domains:
    total = np.random.randint(4500, 6000)
    failed = np.random.randint(0, 300)
    accuracy = round(100 * (total - failed) / total, 2)

    rows.append({
        "run_date": run_date,
        "domain": domain,
        "accuracy_pct": accuracy,
        "rules_checked": total,
        "failed_rules": failed
    })

supabase.table("dq_log").insert(rows).execute()
print(f"✅ Inserted {len(rows)} dummy rows at {run_date}")
