from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import numpy as np

# Load env
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Dummy data generator
np.random.seed(42)
domains = ["loan", "transaction", "kyc", "risk", "customer"]
start_date = datetime(2025, 4, 1)
rows = []

for i in range(5000):
    run_date = start_date + timedelta(days=np.random.randint(0, 30))
    domain = np.random.choice(domains)
    rules_checked = np.random.randint(4500, 6000)
    failed_rules = np.random.randint(0, 300)
    accuracy_pct = round(100 * (rules_checked - failed_rules) / rules_checked, 2)

    row = {
        "run_date": run_date.isoformat(),
        "domain": domain,
        "accuracy_pct": accuracy_pct,
        "rules_checked": rules_checked,
        "failed_rules": failed_rules
    }
    rows.append(row)

# Insert in batch of 100
for i in range(0, len(rows), 100):
    batch = rows[i:i+100]
    supabase.table("dq_log").insert(batch).execute()

print("Done seeding 5000 records to Supabase!")
