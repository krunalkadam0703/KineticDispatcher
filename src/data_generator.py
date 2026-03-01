import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class TruthLinkDataGenerator:
    """
    SOLID: Responsible for generating a relational ecosystem of 
    Merchants, Menu Items, and Orders with built-in Signal Gaps.
    """
    def __init__(self, num_merchants=100, num_items=500, num_orders=2000):
        self.num_merchants = num_merchants
        self.num_items = num_items
        self.num_orders = num_orders

    def generate_all(self):
        # 1. Generate Merchants
        merchants = self._create_merchants()
        
        # 2. Generate Menu Items (linked to merchants)
        menu = self._create_menu(merchants)
        
        # 3. Generate Orders (the transactional 'truth' data)
        orders = self._create_orders(merchants, menu)
        
        return merchants, menu, orders

    def _create_merchants(self):
        return pd.DataFrame({
            'merchant_id': [f"M_{i:03d}" for i in range(self.num_merchants)],
            'merchant_name': [f"Restaurant_{i}" for i in range(self.num_merchants)],
            'base_honesty_score': np.random.uniform(0.3, 0.95, self.num_merchants), # The "Liar" factor
            'kitchen_capacity': np.random.randint(3, 15, self.num_merchants),
            'lat': np.random.uniform(12.90, 13.00, self.num_merchants),
            'lon': np.random.uniform(77.50, 77.65, self.num_merchants)
        })

    def _create_menu(self, merchants):
        items = []
        for _, m in merchants.iterrows():
            # Each merchant has ~5 items
            for j in range(5):
                items.append({
                    'item_id': f"ITM_{m['merchant_id']}_{j}",
                    'merchant_id': m['merchant_id'],
                    'item_name': f"Dish_{j}",
                    'p_base': np.random.randint(8, 25) # Base minutes to cook
                })
        return pd.DataFrame(items)

    def _create_orders(self, merchants, menu):
        orders = []
        start_time = datetime(2026, 3, 1, 11, 0) # Peak Lunch Hour

        for i in range(self.num_orders):
            m_row = merchants.sample(1).iloc[0]
            m_menu = menu[menu['merchant_id'] == m_row['merchant_id']]
            item_row = m_menu.sample(1).iloc[0]
            
            # --- APPLY FORMULAS ---
            # 1. Physics: Real Prep = p_base * Rush Coefficient
            # Simulate a rush between 1 PM and 2 PM
            order_ts = start_time + timedelta(minutes=i * 2)
            is_rush = 1.4 if 13 <= order_ts.hour <= 14 else 1.0
            real_prep_duration = item_row['p_base'] * is_rush
            
            # 2. Behavioral: The "Ready Click" (The Lie)
            # High honesty = click near actual. Low honesty = click much earlier.
            lie_buffer = (1 - m_row['base_honesty_score']) * 12 
            ready_click_offset = max(2, real_prep_duration - lie_buffer)
            
            # 3. Timestamps
            ready_click_ts = order_ts + timedelta(minutes=ready_click_offset)
            actual_handover_ts = order_ts + timedelta(minutes=real_prep_duration)
            
            # Rider travel time (Independent variable)
            rider_travel = np.random.randint(5, 18)

            orders.append({
                'order_id': f"ORD_{i:05d}",
                'merchant_id': m_row['merchant_id'],
                'item_id': item_row['item_id'],
                'p_base_ordered': item_row['p_base'], # Storing for easier physics calculation
                'order_timestamp': order_ts,
                'ready_click_timestamp': ready_click_ts,
                'actual_handover_timestamp': actual_handover_ts,
                'rider_travel_time_mins': rider_travel
            })
        return pd.DataFrame(orders)

if __name__ == "__main__":
    generator = TruthLinkDataGenerator()
    m, mn, o = generator.generate_all()
    
    # Save to RAW folder
    m.to_csv("data/raw/merchants.csv", index=False)
    mn.to_csv("data/raw/menu_items.csv", index=False)
    o.to_csv("data/raw/orders.csv", index=False)
    print("✅ Data Ecosystem Created: 100 Merchants, 500 Menu Items, 2000 Orders.")