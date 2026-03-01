import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class ZomatoSim:
    def __init__(self, merchants_df, menu_df):
        self.merchants = merchants_df
        self.menu = menu_df

    def simulate_order(self, order_id):
        # 1. Setup Order Context
        m = self.merchants.sample(1).iloc[0]
        item = self.menu[self.menu['merchant_id'] == m['merchant_id']].sample(1).iloc[0]
        
        # 2. GROUND TRUTH (What actually happens in the kitchen)
        # Physics + 10% random noise (e.g. chef dropped a spoon)
        base_prep = item['p_base']
        noise = np.random.normal(0, 2) # Random variance in minutes
        actual_ready_time = base_prep + noise
        
        # 3. MERCHANT BEHAVIOR (The 'Lie' signal)
        # Dishonest merchants click 'Ready' much earlier than actual_ready_time
        # Honesty score 0.3 means they click 70% earlier than they should.
        lie_factor = (1 - m['base_honesty_score']) * 10 
        ready_click_time = max(1, actual_ready_time - lie_factor)
        
        # 4. TRUTHLINK DISPATCH (Your AI Logic)
        # Uses learned 'current_beta' and Physics Floor
        physics_floor = base_prep * 1.1 # Static safety floor
        predicted_ready = max(ready_click_time, physics_floor) + m['current_beta']
        
        # 5. RIDER TRAVEL
        rider_eta = np.random.uniform(5, 15)
        t_dispatch = predicted_ready - rider_eta

        return {
            "order_id": order_id,
            "merchant": m['merchant_name'],
            "actual_prep": round(actual_ready_time, 2),
            "click_time": round(ready_click_time, 2),
            "ai_predicted": round(predicted_ready, 2),
            "wait_saved": round(max(0, actual_ready_time - ready_click_time), 2)
        }
