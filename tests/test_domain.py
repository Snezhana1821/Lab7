import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from decimal import Decimal
from domain.entities import Order, OrderLine
from domain.value_objects import Money, OrderStatus


class TestMoney:
    """Тесты для Value Object Money"""
    
    def test_money_creation(self):
        money = Money(Decimal('100.50'), 'USD')
        assert money.amount == Decimal('100.50')
        assert money.currency == 'USD'
    
    def test_money_addition(self):
        money1 = Money(Decimal('50'), 'USD')
        money2 = Money(Decimal('30.50'), 'USD')
        result = money1 + money2
        assert result.amount == Decimal('80.50')
    
    def test_money_addition_different_currencies_fails(self):
        money1 = Money(Decimal('50'), 'USD')
        money2 = Money(Decimal('30.50'), 'EUR')
        try:
            money1 + money2
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "different currencies" in str(e)
    
    def test_money_negative_amount_fails(self):
        try:
            Money(Decimal('-10'), 'USD')
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "cannot be negative" in str(e)


class TestOrderLine:
    """Тесты для OrderLine"""
    
    def test_order_line_creation(self):
        price = Money(Decimal('10.99'), 'USD')
        line = OrderLine("prod_1", "Product 1", price, 2)
        assert line.product_id == "prod_1"
        assert line.total.amount == Decimal('21.98')
    
    def test_order_line_zero_quantity_fails(self):
        price = Money(Decimal('10.99'), 'USD')
        try:
            OrderLine("prod_1", "Product 1", price, 0)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Quantity must be positive" in str(e)


class TestOrder:
    """Тесты для агрегата Order"""
    
    def test_order_creation(self):
        order = Order(customer_id="customer_123")
        assert order.status == OrderStatus.PENDING
        assert order.customer_id == "customer_123"
        assert len(order.lines) == 0
    
    def test_add_line(self):
        order = Order(customer_id="customer_123")
        price = Money(Decimal('10'), 'USD')
        order.add_line("prod_1", "Product 1", price, 2)
        
        assert len(order.lines) == 1
        assert order.total.amount == Decimal('20')
    
    def test_cannot_add_duplicate_product(self):
        order = Order(customer_id="customer_123")
        price = Money(Decimal('10'), 'USD')
        order.add_line("prod_1", "Product 1", price, 2)
        
        try:
            order.add_line("prod_1", "Product 1", price, 3)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "already in order" in str(e)
    
    def test_cannot_add_line_to_paid_order(self):
        order = Order(customer_id="customer_123")
        price = Money(Decimal('10'), 'USD')
        order.add_line("prod_1", "Product 1", price, 2)
        order.pay()
        
        try:
            order.add_line("prod_2", "Product 2", price, 1)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Cannot modify paid order" in str(e)
    
    def test_pay_empty_order_fails(self):
        """нельзя оплатить пустой заказ"""
        order = Order(customer_id="customer_123")
        
        try:
            order.pay()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Cannot pay empty order" in str(e)
    
    def test_pay_already_paid_order_fails(self):
        """нельзя оплатить заказ повторно"""
        order = Order(customer_id="customer_123")
        price = Money(Decimal('10'), 'USD')
        order.add_line("prod_1", "Product 1", price, 2)
        
        order.pay()  # Первая оплата
        
        try:
            order.pay()  # Вторая оплата
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Order already paid" in str(e)
    
    def test_order_total_calculation(self):
        """итоговая сумма равна сумме строк"""
        order = Order(customer_id="customer_123")
        price1 = Money(Decimal('10'), 'USD')
        price2 = Money(Decimal('5'), 'USD')
        
        order.add_line("prod_1", "Product 1", price1, 2)  # 20
        order.add_line("prod_2", "Product 2", price2, 3)  # 15
        
        assert order.total.amount == Decimal('35')  # 20 + 15
    
    def test_order_status_after_payment(self):
        order = Order(customer_id="customer_123")
        price = Money(Decimal('10'), 'USD')
        order.add_line("prod_1", "Product 1", price, 1)
        order.pay()
        
        assert order.status == OrderStatus.PAID
