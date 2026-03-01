from abc import ABC, abstractmethod
import pandas as pd

class BaseDispatchStrategy(ABC):
    """
    SOLID: Strategy Pattern Interface.
    Defines the contract for calculating the precise 'Dispatch Trigger'.
    """

    @abstractmethod
    def calculate_true_ready_time(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculates T_FOR (Truth for Order Ready).
        Formula: T_FOR = max(T_Ready_Click, T_Physics) + Beta_Penalty
        """
        pass

    @abstractmethod
    def determine_dispatch_trigger(self, t_for: pd.Series, travel_time: pd.Series) -> pd.Series:
        """
        Calculates T_Dispatch (The moment the rider is notified).
        Formula: T_Dispatch = T_FOR - (T_Travel * Efficiency_Rider)
        """
        pass

    @abstractmethod
    def execute_dispatch_plan(self, df: pd.DataFrame, merchants: pd.DataFrame) -> pd.DataFrame:
        """
        Orchestrates the full dispatch calculation across the dataset.
        Returns a DataFrame with the optimized 't_dispatch' column.
        """
        pass