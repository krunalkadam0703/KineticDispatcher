from abc import ABC, abstractmethod
import pandas as pd

class BasePenaltyObserver(ABC):
    """
    SOLID: Interface for behavioral observation.
    Following the Observer Pattern, any class implementing this must 
    be able to 'listen' to order completion data and update merchant reliability.
    """

    @abstractmethod
    def calculate_signal_gap(self, ready_click_ts: pd.Timestamp, handover_ts: pd.Timestamp) -> float:
        """
        Calculates the delta between the merchant's claim and GPS truth.
        Formula: G = T_Actual_Handover - T_Ready_Click
        """
        pass

    @abstractmethod
    def update_merchant_state(self, merchant_id: str, signal_gap: float) -> None:
        """
        Updates the internal beta (penalty) for a specific merchant 
        using the Recursive Update/EMA formula.
        """
        pass

    @abstractmethod
    def process_batch(self, orders_df: pd.DataFrame, merchants_df: pd.DataFrame) -> pd.DataFrame:
        """
        Orchestrates the update across an entire dataset of orders.
        Returns a modified merchants_df with updated 'current_beta' values.
        """
        pass