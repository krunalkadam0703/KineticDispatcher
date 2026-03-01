import pandas as pd
import numpy as np
from src.abstractions.base_strategy import BaseDispatchStrategy

class PrecisionDispatchStrategy(BaseDispatchStrategy):
    """
    SOLID: Strategy Implementation.
    Calculates the T_Dispatch trigger by synchronizing Physics and Behavior.
    Goal: Minimize 'Rider Wait Waste' (RWW).
    """

    def __init__(self, efficiency_factor: float = 0.95):
        self.eta_rider = efficiency_factor  # Accounting for traffic/rider speed

    def calculate_true_ready_time(self, df: pd.DataFrame) -> pd.Series:
        """
        Formula: T_FOR = max(T_Ready_Click, T_Physics) + Beta_Penalty
        Determines when the food will ACTUALLY be ready.
        """
        # We take the maximum of the signal and physics to ignore 'impossible' clicks
        # then add the merchant's learned dishonesty (current_beta)
        ready_baseline = np.maximum(
            df['ready_click_timestamp'],
            df['order_timestamp'] + pd.to_timedelta(df['t_physics'], unit='m')
        )
        
        return ready_baseline + pd.to_timedelta(df['current_beta'], unit='m')

    def determine_dispatch_trigger(self, t_for: pd.Series, travel_time: pd.Series) -> pd.Series:
        """
        Formula: T_Dispatch = T_FOR - (T_Travel * eta)
        Back-calculates the notification time based on rider distance.
        """
        return t_for - pd.to_timedelta(travel_time * self.eta_rider, unit='m')

    def execute_dispatch_plan(self, df: pd.DataFrame, merchants: pd.DataFrame) -> pd.DataFrame:
        """
        Orchestrates the calculation and attaches the 't_dispatch' command.
        """
        # 1. Map current merchant penalties (Betas) to the orders
        df = df.merge(merchants[['merchant_id', 'current_beta']], on='merchant_id', how='left')
        
        # 2. Calculate the 'Truth for Order Ready' (T_FOR)
        df['t_for'] = self.calculate_true_ready_time(df)
        
        # 3. Calculate the 'Dispatch Notification Time' (T_Dispatch)
        df['t_dispatch'] = self.determine_dispatch_trigger(
            df['t_for'], 
            df['rider_travel_time_mins']
        )
        
        # 4. Success Metric: Predicted Wait vs Actual Wait
        # (T_FOR - T_Arrival)
        return df