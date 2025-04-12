from supabase import create_client, Client
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Load .env config
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Seed data
domains = ['loan', 'customer', 'risk', 'investment', 'kyc']
np.random.seed(42)

for i in range(10):
    run_date = datetime(2025, 4, 1) + pd.Timedelta(days=i * 2)
    for domain in domains:
        total = np.random.randint(4000, 6000)
        failed = np.random.randint(50, 400)  # deliberately vary
        accuracy = round(100 * (total - failed) / total, 2)

        supabase.table("dq_log").insert({
            "run_date": run_date.isoformat(),
            "domain": domain,
            "accuracy_pct": accuracy,
            "rules_checked": total,
            "failed_rules": failed
        }).execute()

print("✅ Dummy data inserted to Supabase.")
