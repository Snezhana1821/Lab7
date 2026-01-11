import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from decimal import Decimal
from infrastructure.repositories import InMemoryOrderRepository
from infrastructure.gateways import FakePaymentGateway
from domain.entities import Order
from domain.value_objects import Money


class TestInMemoryOrderRepository:
    """Тесты для InMemory репозитория"""
    
    def test_save_and_get_by_id(self):
        repository = InMemoryOrderRepository()
        order = Order(customer_id="test_customer")
        price = Money(Decimal('50'), 'USD')
        order.add_line("prod_1", "Product 1", price, 2)
        
        repository.save(order)
        retrieved = repository.get_by_id(order.id)
        
        assert retrieved is not None
        assert retrieved.id == order.id
        assert retrieved.customer_id == order.customer_id
    
    def test_get_nonexistent_order(self):
        repository = InMemoryOrderRepository()
        result = repository.get_by_id("non_existent_id")
        assert result is None
    
    def test_update_existing_order(self):
        repository = InMemoryOrderRepository()
        order = Order(customer_id="test_customer")
        price = Money(Decimal('50'), 'USD')
        order.add_line("prod_1", "Product 1", price, 2)
        
        repository.save(order)
        
        price2 = Money(Decimal('30'), 'USD')
        order.add_line("prod_2", "Product 2", price2, 1)
        repository.save(order)
        
        retrieved = repository.get_by_id(order.id)
        assert len(retrieved.lines) == 2


class TestFakePaymentGateway:
    """Тесты для Fake платежного шлюза"""
    
    def test_charge_always_succeeds(self):
        gateway = FakePaymentGateway()
        amount = Money(Decimal('100'), 'USD')
        result = gateway.charge("order_123", amount)
        assert result is True
