from abc import ABC, abstractmethod
from typing import Optional


class OrderRepository(ABC):
    """Интерфейс репозитория заказов"""
    
    @abstractmethod
    def get_by_id(self, order_id: str) -> Optional['domain.entities.Order']:
        """Получить заказ по ID"""
        pass
    
    @abstractmethod
    def save(self, order: 'domain.entities.Order') -> None:
        """Сохранить заказ"""
        pass


class PaymentGateway(ABC):
    """Интерфейс платежного шлюза"""
    
    @abstractmethod
    def charge(self, order_id: str, money: 'domain.value_objects.Money') -> bool:
        """Выполнить платеж"""
        pass
