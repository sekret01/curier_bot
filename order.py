class Order():
    """описание заказа"""

    number = None
    active = True
    time = None
    pay = None

    def __init__(self, number):
        self.number = number

    def take_time(self, end_time):
        """время завершения заказа"""
        self.time = end_time

    def take_pay(self, pay):
        """обещанная сумма за заказ"""
        self.pay = pay

