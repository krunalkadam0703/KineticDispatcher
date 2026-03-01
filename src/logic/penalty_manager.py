import pandas as pd
import numpy as np
from src.abstractions.base_observer import BasePenaltyObserver

class PenaltyManager(BasePenaltyObserver):
    """
    SOLID: Observer Implementation.
    Learns the 'Signal Gap' (The Lie) for each merchant using EMA.
    Formula: Beta_new = (Alpha * G) + (1 - Alpha) * Beta_old
    """

    def __init__(self, alpha: float = 0.2):
        # Alpha determines how much 'weight' we give to the newest order.
        # 0.2 means slow, stable learning; 0.8 means highly reactive.
        self.alpha = alpha

    def calculate_signal_gap(self, ready_click_ts: pd.Series, handover_ts: pd.Series) -> pd.Series:
        """
        G = T_Actual_Handover - T_Ready_Click
        Calculates how many minutes 'early' the merchant clicked.
        """
        gap = (handover_ts - ready_click_ts).dt.total_seconds() / 60.0
        # We only penalize 'Early' clicks (positive gaps). 
        # Negative gaps mean the food was actually ready BEFORE they clicked.
        return gap.clip(lower=0)

    def update_merchant_state(self, current_beta: float, new_gap: float) -> float:
        """
        Recursive Update Formula (EMA).
        Learns the behavioral pattern over time.
        """
        if pd.isna(current_beta):
            return new_gap  # Start with the first gap as the baseline
            
        return (self.alpha * new_gap) + ((1 - self.alpha) * current_beta)

    def process_batch(self, orders_df: pd.DataFrame, merchants_df: pd.DataFrame) -> pd.DataFrame:
        """
        Orchestrates the learning loop across all merchants.
        """
        # 1. Calculate the 'Truth Gap' for every order in the batch
        orders_df['current_gap'] = self.calculate_signal_gap(
            orders_df['ready_click_timestamp'], 
            orders_df['actual_handover_timestamp']
        )

        # 2. Group by merchant and find the 'Mean Gap' for this specific batch
        batch_performance = orders_df.groupby('merchant_id')['current_gap'].mean().reset_index()

        # 3. Update the 'current_beta' in the merchant registry
        # We merge the new performance with the existing registry
        updated_merchants = merchants_df.merge(
            batch_performance, on='merchant_id', how='left'
        )

        # Apply the EMA formula
        updated_merchants['current_beta'] = updated_merchants.apply(
            lambda x: self.update_merchant_state(x.get('current_beta', 0), x['current_gap']) 
            if pd.notna(x['current_gap']) else x.get('current_beta', 0),
            axis=1
        )

        return updated_merchants.drop(columns=['current_gap'])