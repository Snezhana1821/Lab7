from typing import Dict, Optional
from application.interfaces import OrderRepository
import domain


class InMemoryOrderRepository(OrderRepository):
    """InMemory реализация репозитория заказов"""
    
    def __init__(self):
        self._storage: Dict[str, domain.entities.Order] = {}
    
    def get_by_id(self, order_id: str) -> Optional[domain.entities.Order]:
        return self._storage.get(order_id)
    
    def save(self, order: domain.entities.Order) -> None:
        self._storage[order.id] = order
