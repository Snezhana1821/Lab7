from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"


@dataclass(frozen=True)
class Money:
    """Value Object для денежных сумм"""
    amount: Decimal
    currency: str = "USD"
    
    def __post_init__(self):
        if self.amount < Decimal('0'):
            raise ValueError("Amount cannot be negative")
    
    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __repr__(self):
        return f"Money({self.amount:.2f} {self.currency})"
