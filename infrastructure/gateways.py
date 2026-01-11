from application.interfaces import PaymentGateway
import domain


class FakePaymentGateway(PaymentGateway):
    """Fake реализация платежного шлюза"""
    
    def charge(self, order_id: str, money: domain.value_objects.Money) -> bool:
        print(f"[FakePaymentGateway] Charging {money} for order {order_id}")
        return True  # Всегда успешно
