import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

class DataRepository:
    """
    SOLID: Repository Pattern.
    Decouples the business logic from the data storage mechanism.
    If we switch from CSV to SQL later, only this file changes.
    """

    def __init__(self, raw_dir: str = "data/raw/", processed_dir: str = "data/processed/"):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir

    def load_raw_dataset(self, filename: str) -> pd.DataFrame:
        """Loads a CSV from the raw data directory."""
        path = os.path.join(self.raw_dir, filename)
        if not os.path.exists(path):
            logger.error(f"Data source not found: {path}")
            raise FileNotFoundError(f"Missing required file: {path}")
        
        return pd.read_csv(path)

    def save_processed_results(self, df: pd.DataFrame, filename: str):
        """Saves the final optimized dispatch results to the processed directory."""
        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)
            
        path = os.path.join(self.processed_dir, filename)
        df.to_csv(path, index=False)
        logger.info(f"💾 Optimized results persisted to: {path}")

    def update_merchant_registry(self, merchants_df: pd.DataFrame):
        """
        Persists the updated Beta values (learned dishonesty) 
        back to the merchant master file.
        """
        path = os.path.join(self.raw_dir, "merchants.csv")
        merchants_df.to_csv(path, index=False)
        logger.info(f"🔄 Merchant reliability scores updated in registry.")