import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from decimal import Decimal
from unittest.mock import Mock
from application.use_cases import PayOrderUseCase, PayOrderResult
from domain.entities import Order
from domain.value_objects import Money, OrderStatus


class TestPayOrderUseCase:
    """Тесты для Use Case оплаты заказа"""
    
    def test_successful_payment(self):
        """успешную оплату корректного заказа"""
        # Arrange
        order = Order(customer_id="customer_123")
        price = Money(Decimal('100'), 'USD')
        order.add_line("prod_1", "Product 1", price, 2)
        
        mock_repository = Mock()
        mock_repository.get_by_id.return_value = order
        mock_repository.save = Mock()
        
        mock_gateway = Mock()
        mock_gateway.charge.return_value = True
        
        use_case = PayOrderUseCase(mock_repository, mock_gateway)
        
        # Act
        result = use_case.execute(order.id)
        
        # Assert
        assert result.success is True
        assert result.order_id == order.id
        assert "successfully" in result.message
        
        mock_repository.get_by_id.assert_called_once_with(order.id)
        mock_gateway.charge.assert_called_once_with(order.id, order.total)
        mock_repository.save.assert_called_once_with(order)
        assert order.status == OrderStatus.PAID
    
    def test_order_not_found(self):
        mock_repository = Mock()
        mock_repository.get_by_id.return_value = None
        
        mock_gateway = Mock()
        mock_gateway.charge.return_value = True
        
        use_case = PayOrderUseCase(mock_repository, mock_gateway)
        
        result = use_case.execute("non_existent_id")
        
        assert result.success is False
        assert "not found" in result.message
        mock_gateway.charge.assert_not_called()
    
    def test_payment_gateway_failure(self):
        order = Order(customer_id="customer_123")
        price = Money(Decimal('100'), 'USD')
        order.add_line("prod_1", "Product 1", price, 2)
        
        mock_repository = Mock()
        mock_repository.get_by_id.return_value = order
        mock_repository.save = Mock()
        
        mock_gateway = Mock()
        mock_gateway.charge.return_value = False
        
        use_case = PayOrderUseCase(mock_repository, mock_gateway)
        
        result = use_case.execute(order.id)
        
        assert result.success is False
        assert "failed" in result.message.lower()
        mock_repository.save.assert_not_called()
    
    def test_payment_fails_for_empty_order(self):
        """ошибку при оплате пустого заказа"""
        empty_order = Order(customer_id="customer_123")
        
        mock_repository = Mock()
        mock_repository.get_by_id.return_value = empty_order
        
        mock_gateway = Mock()
        mock_gateway.charge.return_value = True
        
        use_case = PayOrderUseCase(mock_repository, mock_gateway)
        
        result = use_case.execute(empty_order.id)
        
        assert result.success is False
        assert "empty" in result.message.lower()
        mock_gateway.charge.assert_not_called()
    
    def test_payment_fails_for_already_paid_order(self):
        """ошибку при повторной оплате"""
        order = Order(customer_id="customer_123")
        price = Money(Decimal('100'), 'USD')
        order.add_line("prod_1", "Product 1", price, 2)
        order.pay()  # Mark as paid
        
        mock_repository = Mock()
        mock_repository.get_by_id.return_value = order
        
        mock_gateway = Mock()
        mock_gateway.charge.return_value = True
        
        use_case = PayOrderUseCase(mock_repository, mock_gateway)
        
        result = use_case.execute(order.id)
        
        assert result.success is False
        assert "already" in result.message.lower()
        mock_gateway.charge.assert_not_called()
