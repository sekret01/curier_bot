from order import Order


class Shift:
    """
    Описание смены

    В класс используются следующие данные:

    - плановое начало смены
    - плановый конец смены
    - фактическое начало смены
    - фактический конец смены
    - количество заработка за смену
    - информация о заказах (см в классе Order)
    - плановое рабочее время
    - фактическое рабочее время
    - состояние активности

    Все данные при сохранении передаются в словарь
    """

    active = False
    exsisting = False
    plan_start_time = None
    plan_end_time = None
    fact_start_time = ()
    fact_end_time = ()
    new_order = None
    struct_new_order = None
    orders = []
    payment = 0
    all_time = ()
    all_plan_time = ()

    def __init__(self, plan_start_time, plan_end_time):
        """инициализация смены с плановым начлом и концом"""
        self.plan_start_time = plan_start_time
        self.plan_end_time = plan_end_time
        self.fact_start_time = plan_start_time
        self.fact_end_time = plan_end_time

    def take_fact_start(self, fact_start_time):
        """получает фактическое начало смены (необходимо при отличии факта от плана)"""
        self.fact_start_time = fact_start_time

    def take_fact_end(self, fact_end_time):
        """получает фактический конец смены (необходимо при отличии факта от плана)"""
        self.fact_end_time = fact_end_time

    def add_order(self, number):
        """инициализация нового заказа, номер заказа"""
        self.new_order = Order(number)

    def add_order_time(self, time):
        """время доставки заказа"""
        self.new_order.take_time(time)

    def add_order_pay(self, pay):
        """обещанная сумма за заказ"""
        self.new_order.take_pay(pay)

    def struct_order(self):
        """обращение структуры заказа в словарь"""
        self.struct_new_order = {f"{self.new_order.number}": {"number": f"{self.new_order.number}",
                                 "time": f"{self.new_order.time[0]}:{self.new_order.time[1]}",
                                 "pay": f"{self.new_order.pay} руб"}}
        self.payment += int(self.new_order.pay)

    def save_order_in_orders(self):
        """добавление итогового словаря заказа в список заказов"""
        self.orders.append(self.struct_new_order)

    def start_shift(self):
        """активация смены"""
        self.active = True

    def end_shift(self):
        """деактивация смены"""
        self.active = False

    def count_all_time(self, start, end):
        """подсчет затраченного времени по факту"""
        start_sec = start[0]*60*60 + start[1]*60
        end_sec = end[0]*60*60 + end[1]*60
        all_sec = end_sec - start_sec
        hours = all_sec//60//60
        minuts = (all_sec - hours*60*60)//60
        self.all_time = (hours, minuts)

    def count_all_plan_time(self, start, end):
        """подсчет планового затраченного времени"""
        hours = end - start
        self.all_plan_time = hours

    def struct_shift(self):
        return {"plan time": f"{self.plan_start_time}:00 - {self.plan_end_time}:00",
                "fact time": f"{self.fact_start_time[0]}:{self.fact_start_time[1]} - {self.fact_end_time[0]}:{self.fact_end_time[1]}",
                "all fact time": f"{self.all_time[0]} ч, {self.all_time[1]} мин",
                "all plan time": self.all_plan_time,
                "payment": self.payment,
                "orders": self.orders}
