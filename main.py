import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.data_pipeline.repository import DataRepository
from src.data_pipeline.cleaner import DataCleaner
from src.engines.physics_engine import PhysicsEngine
from src.logic.penalty_manager import PenaltyManager
from src.logic.dispatch_strategies import PrecisionDispatchStrategy
from src.utils.metrics import MetricsEvaluator

class TruthLinkOrchestrator:
    def __init__(self, repo, cleaner, physics, penalty_mgr, strategy):
        self.repo = repo
        self.cleaner = cleaner
        self.physics = physics
        self.penalty_mgr = penalty_mgr
        self.strategy = strategy

    def execute(self):
        print("\n--- PHASE 1: HISTORICAL LEARNING PIPELINE ---")
        orders_raw = "orders.csv"
        menu_raw = "menu_items.csv"
        merchants_raw = "merchants.csv"
        
        # 1. Pipeline Execution
        df = self.cleaner.clean_and_prepare(
            os.path.join(self.repo.raw_dir, orders_raw),
            os.path.join(self.repo.raw_dir, menu_raw),
            os.path.join(self.repo.raw_dir, merchants_raw)
        )
        
        merchants_registry = self.repo.load_raw_dataset(merchants_raw)
        df = self.physics.apply_physics_to_batch(df)
        updated_merchants = self.penalty_mgr.process_batch(df, merchants_registry)
        self.repo.update_merchant_registry(updated_merchants)
        
        final_df = self.strategy.execute_dispatch_plan(df, updated_merchants)
        stats = MetricsEvaluator.calculate_kpis(final_df)
        MetricsEvaluator.report_impact(stats)
        
        self.repo.save_processed_results(final_df, "optimized_dispatch_results.csv")
        return updated_merchants

class LiveSystemSimulator:
    """
    Simulates the 'Real World' using the parameters learned in Phase 1.
    """
    def __init__(self, merchants_df, menu_df, physics_engine):
        self.merchants = merchants_df
        self.menu = menu_df
        self.physics = physics_engine

    def run(self, num_orders=10):
        print("\n--- PHASE 2: LIVE DISPATCH SIMULATION ---")
        print(f"{'MERCHANT':<18} | {'PHYSICS':<8} | {'BETA (LIE)':<10} | {'RIDER ETA':<10} | {'DISPATCH IN'}")
        print("-" * 75)
        
        for i in range(num_orders):
            m = self.merchants.sample(1).iloc[0]
            # Get an item for this merchant
            m_menu = self.menu[self.menu['merchant_id'] == m['merchant_id']]
            item = m_menu.sample(1).iloc[0] if not m_menu.empty else {'p_base': 15}

            # 1. Physics Engine Calculation
            t_phys = self.physics.estimate_prep_floor(item['p_base'], datetime.now().hour)
            
            # 2. Behavioral Penalty (Learned Beta)
            beta = m.get('current_beta', 0)
            
            # 3. Rider Logistics
            rider_eta = np.random.uniform(4, 12)
            
            # 4. Dispatch Decision: T_FOR - Rider_ETA
            # We assume current time is T=0
            t_for = t_phys + beta
            t_dispatch = t_for - rider_eta
            
            status = f"{t_dispatch:.2f} min" if t_dispatch > 0 else "🚨 IMMEDIATE"
            
            print(f"{m['merchant_name'][:18]:<18} | {t_phys:<8.1f} | {beta:<10.2f} | {rider_eta:<10.2f} | {status}")

if __name__ == "__main__":
    # Setup
    repo = DataRepository()
    cleaner = DataCleaner()
    physics = PhysicsEngine()
    penalty_mgr = PenaltyManager(alpha=0.3)
    strategy = PrecisionDispatchStrategy()

    orchestrator = TruthLinkOrchestrator(repo, cleaner, physics, penalty_mgr, strategy)
    
    try:
        # Step 1: Learn from the past
        updated_merchants = orchestrator.execute()
        
        # Step 2: Simulate the present
        menu_items = repo.load_raw_dataset("menu_items.csv")
        simulator = LiveSystemSimulator(updated_merchants, menu_items, physics)
        simulator.run(num_orders=15)
        
        print("\n✅ All systems nominal. Simulation complete.")
    except Exception as e:
        print(f"❌ System Error: {str(e)}")