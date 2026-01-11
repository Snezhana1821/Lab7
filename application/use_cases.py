from dataclasses import dataclass
from typing import Optional
from .interfaces import OrderRepository, PaymentGateway
import domain


@dataclass
class PayOrderResult:
    """Результат выполнения use case"""
    success: bool
    order_id: str
    message: str = ""


class PayOrderUseCase:
    """Use Case для оплаты заказа"""
    
    def __init__(self, repository: OrderRepository, gateway: PaymentGateway):
        self.repository = repository
        self.gateway = gateway
    
    def execute(self, order_id: str) -> PayOrderResult:
        """
        Выполнить оплату заказа:
        1. Загрузить заказ через OrderRepository
        2. Выполнить доменную операцию оплаты
        3. Вызвать платёж через PaymentGateway
        4. Сохранить заказ
        5. Возвратить результат оплаты
        """
        try:
            # 1. Загрузить заказ через OrderRepository
            order = self.repository.get_by_id(order_id)
            if order is None:
                return PayOrderResult(
                    success=False,
                    order_id=order_id,
                    message=f"Order {order_id} not found"
                )
            
            # 2. Выполнить доменную операцию оплаты
            order.pay()
            
            # 3. Вызвать платёж через PaymentGateway
            if not self.gateway.charge(order_id, order.total):
                return PayOrderResult(
                    success=False,
                    order_id=order_id,
                    message="Payment gateway charge failed"
                )
            
            # 4. Сохранить заказ
            self.repository.save(order)
            
            # 5. Возвратить результат оплаты
            return PayOrderResult(
                success=True,
                order_id=order_id,
                message="Order paid successfully"
            )
            
        except ValueError as e:
            return PayOrderResult(
                success=False,
                order_id=order_id,
                message=str(e)
            )
