import pandas as pd
import numpy as np

class PhysicsEngine:
    """
    SOLID: Single Responsibility Principle.
    Responsible for calculating the 'Physical Floor' of food preparation.
    Ignores merchant signals and focuses on the laws of the kitchen.
    """

    def __init__(self):
        # Configuration for Rush Hour impact
        self.LUNCH_PEAK = (12, 14)  # 12 PM to 2 PM
        self.DINNER_PEAK = (19, 21) # 7 PM to 9 PM
        self.RUSH_MULTIPLIER = 1.4
        self.DEFAULT_MULTIPLIER = 1.0

    def calculate_rush_coefficient(self, hour: int) -> float:
        """
        Formula: C_rush
        Determines the kitchen load multiplier based on the time of day.
        """
        if (self.LUNCH_PEAK[0] <= hour <= self.LUNCH_PEAK[1]) or \
           (self.DINNER_PEAK[0] <= hour <= self.DINNER_PEAK[1]):
            return self.RUSH_MULTIPLIER
        return self.DEFAULT_MULTIPLIER

    def estimate_prep_floor(self, p_base: float, order_hour: int) -> float:
        """
        Formula: T_Physics = P_base * C_rush
        Calculates the minimum viable prep time.
        """
        c_rush = self.calculate_rush_coefficient(order_hour)
        return round(p_base * c_rush, 2)

    def apply_physics_to_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Vectorized application of physics formulas to the entire order set.
        Adds 't_physics' column to the DataFrame.
        """
        # Using NumPy vectorization for high performance
        df['t_physics'] = df.apply(
            lambda row: self.estimate_prep_floor(row['p_base'], row['order_hour']), 
            axis=1
        )
        return df