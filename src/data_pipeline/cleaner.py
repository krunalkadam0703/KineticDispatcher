import pandas as pd
import numpy as np
import logging

# Configure basic logging for data integrity issues
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCleaner:
    """
    SOLID: Single Responsibility Principle.
    Gatekeeper for Data Integrity, Type Safety, and Relational Joins.
    """

    @staticmethod
    def clean_and_prepare(orders_path: str, menu_path: str, merchants_path: str) -> pd.DataFrame:
        # 1. Load Data
        orders = pd.read_csv(orders_path)
        menu = pd.read_csv(menu_path)
        merchants = pd.read_csv(merchants_path)

        # 2. STRICT TYPE MATCHING & DATA VALIDATION
        # Ensure ID columns are strings to prevent join errors (e.g., 101 vs "101")
        id_cols = ['merchant_id', 'item_id']
        for df in [orders, menu, merchants]:
            for col in id_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()

        # 3. TIMESTAMP CONVERSION & ANOMALY DETECTION
        ts_columns = ['order_timestamp', 'ready_click_timestamp', 'actual_handover_timestamp']
        for col in ts_columns:
            orders[col] = pd.to_datetime(orders[col], errors='coerce')

        # Drop rows where critical timestamps failed to parse
        initial_count = len(orders)
        orders = orders.dropna(subset=ts_columns)
        if len(orders) < initial_count:
            logger.warning(f"Dropped {initial_count - len(orders)} rows due to invalid timestamps.")

        # 4. LOGICAL VALIDATION (Temporal Consistency)
        # Rule: Actual Handover cannot happen before the Order Timestamp
        valid_mask = orders['actual_handover_timestamp'] >= orders['order_timestamp']
        orders = orders[valid_mask]

        # 5. RELATIONAL JOINS
        # Join Menu to get 'p_base' (Prep Physics)
        df = orders.merge(menu[['item_id', 'p_base']], on='item_id', how='left')
        
        # Join Merchants to get 'kitchen_capacity' and 'base_honesty_score'
        df = df.merge(merchants[['merchant_id', 'base_honesty_score', 'kitchen_capacity']], 
                      on='merchant_id', how='left')

        # 6. MISSING VALUE IMPUTATION (The "Safety Net")
        # If an item is missing from menu, assume median prep time (15 mins)
        if df['p_base'].isnull().any():
            median_p = df['p_base'].median() if not df['p_base'].isnull().all() else 15.0
            df['p_base'] = df['p_base'].fillna(median_p)
            logger.info(f"Imputed missing p_base with {median_p} minutes.")

        # If honesty score is missing, assume the merchant is a "Liar" (Safety First)
        df['base_honesty_score'] = df['base_honesty_score'].fillna(0.5)

        # 7. FEATURE ENGINEERING
        df['order_hour'] = df['order_timestamp'].dt.hour
        
        # Calculate Signal Gap (G): The "Ground Truth" for our Observer
        df['raw_signal_gap'] = (
            (df['actual_handover_timestamp'] - df['ready_click_timestamp']).dt.total_seconds() / 60.0
        ).round(2)

        return df