from dataclasses import dataclass
from typing import List
from decimal import Decimal
from uuid import uuid4
from .value_objects import Money, OrderStatus


@dataclass
class OrderLine:
    """Часть агрегата Order"""
    product_id: str
    product_name: str
    price: Money
    quantity: int
    
    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
    
    @property
    def total(self) -> Money:
        return Money(self.price.amount * Decimal(self.quantity))


class Order:
    """Агрегат заказа - сущность"""
    
    def __init__(self, customer_id: str, order_id: str = None):
        self.id = order_id or str(uuid4())
        self.customer_id = customer_id
        self.status = OrderStatus.PENDING
        self.lines: List[OrderLine] = []
    
    def add_line(self, product_id: str, product_name: str, price: Money, quantity: int = 1) -> None:
        """Добавить строку заказа"""
        if self.status == OrderStatus.PAID:
            raise ValueError("Cannot modify paid order")
        
        # Проверка дублирования продукта
        for line in self.lines:
            if line.product_id == product_id:
                raise ValueError(f"Product {product_id} already in order")
        
        self.lines.append(OrderLine(
            product_id=product_id,
            product_name=product_name,
            price=price,
            quantity=quantity
        ))
    
    def pay(self) -> None:
        """Оплатить заказ - доменная операция"""
        # Инвариант: нельзя оплатить пустой заказ
        if not self.lines:
            raise ValueError("Cannot pay empty order")
        
        # Инвариант: нельзя оплатить заказ повторно
        if self.status == OrderStatus.PAID:
            raise ValueError("Order already paid")
        
        self.status = OrderStatus.PAID
    
    @property
    def total(self) -> Money:
        """Общая сумма заказа"""
        if not self.lines:
            return Money(Decimal('0'))
        
        total = Money(Decimal('0'), self.lines[0].price.currency)
        for line in self.lines:
            total += line.total
        return total
    
    def __repr__(self):
        return f"Order(id={self.id}, status={self.status.value}, total={self.total})"
