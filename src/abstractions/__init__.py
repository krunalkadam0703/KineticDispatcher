from .base_observer import BasePenaltyObserver
from .base_strategy import BaseDispatchStrategy

# This allows for cleaner imports elsewhere:
# e.g., from src.abstractions import BasePenaltyObserver
__all__ = [
    "BasePenaltyObserver",
    "BaseDispatchStrategy"
]