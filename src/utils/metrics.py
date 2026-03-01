import pandas as pd
import numpy as np

class MetricsEvaluator:
    """
    SOLID: Single Responsibility Principle.
    Evaluates the business impact of TruthLink vs. the Baseline (Merchant Signals).
    """

    @staticmethod
    def calculate_kpis(df: pd.DataFrame) -> dict:
        """
        Compares the 'Old Way' (Merchant Clicks) vs. 'TruthLink Way' (T_Dispatch).
        """
        # 1. Baseline: When would the rider have arrived if we trusted the Merchant?
        # Arrival = Ready_Click + Travel_Time (assuming instant dispatch)
        df['baseline_arrival'] = df['ready_click_timestamp'] + pd.to_timedelta(df['rider_travel_time_mins'], unit='m')
        
        # 2. TruthLink: When does the rider arrive with our AI?
        df['ai_arrival'] = df['t_dispatch'] + pd.to_timedelta(df['rider_travel_time_mins'], unit='m')

        # 3. Calculate Rider Wait Waste (RWW)
        # RWW = Actual_Handover - Arrival (Only if positive)
        df['baseline_wait'] = (df['actual_handover_timestamp'] - df['baseline_arrival']).dt.total_seconds() / 60.0
        df['ai_wait'] = (df['actual_handover_timestamp'] - df['ai_arrival']).dt.total_seconds() / 60.0
        
        # Clip to 0 (You can't have negative wait time; that's 'Food Wait' instead)
        df['baseline_wait'] = df['baseline_wait'].clip(lower=0)
        df['ai_wait'] = df['ai_wait'].clip(lower=0)

        # 4. Aggregate Impact
        metrics = {
            'avg_baseline_wait_mins': round(df['baseline_wait'].mean(), 2),
            'avg_ai_wait_mins': round(df['ai_wait'].mean(), 2),
            'total_hours_saved': round((df['baseline_wait'].sum() - df['ai_wait'].sum()) / 60, 2),
            'wait_reduction_percentage': round(
                (1 - (df['ai_wait'].mean() / df['baseline_wait'].mean())) * 100, 2
            )
        }
        
        return metrics

    @staticmethod
    def report_impact(metrics: dict):
        """Prints a professional business impact report."""
        print("\n" + "="*40)
        print("🚀 TRUTHLINK IMPACT REPORT")
        print("="*40)
        print(f"Standard Wait Time:  {metrics['avg_baseline_wait_mins']} mins")
        print(f"TruthLink Wait Time: {metrics['avg_ai_wait_mins']} mins")
        print(f"Wait Reduction:      {metrics['wait_reduction_percentage']}%")
        print(f"Fleet Time Saved:    {metrics['total_hours_saved']} hours")
        print("="*40 + "\n")