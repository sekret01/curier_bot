from work_shift import Shift
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ContentType, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram import F
import time
import pickle
import os
from config import TOKEN


rus_lan = ["Время по плану", "Фактическое время", "Время по плану", "Часов за смену", "Примерная зп", "Заказы", "Время", "Плата"]
eng_lan = ["plan time", "fact time", "all fact time", "all plan time", "payment", "orders", "time", "pay"]

token = TOKEN
chat_id = ""
registrate_shift = False
registrate_order = False

bot = Bot(token=token)
dp = Dispatcher()

shift = Shift(0, 0)
shifts = {}

btn_new_shift = KeyboardButton(text="добавить смену")
keyboard_add_shift = ReplyKeyboardMarkup(keyboard=[[btn_new_shift]], resize_keyboard=True)

btn_start_shift = KeyboardButton(text="Начать смену")
keyboard_start_shift = ReplyKeyboardMarkup(keyboard=[[btn_start_shift]], resize_keyboard=True)

btn_end_shift = KeyboardButton(text="Закончить смену")
btn_add_order = KeyboardButton(text="Новый заказ")
keyboard_work_shift = ReplyKeyboardMarkup(keyboard=[[btn_end_shift], [btn_add_order]], resize_keyboard=True)


def save_data(data) -> None:
    """сохранение статистики в файлы data.pickle и data.txt"""
    text = f""

    for keys, val in data.items():
        text += f"Смена  <{keys}>\n\n"
        for key, value in val.items():
            if key != "orders":
                text += f"\t{rus_lan[eng_lan.index(key)]} - {value}\n"
            else:
                text += f"\n\tЗаказы\n"
                for i in value:
                    for number, el in i.items():
                        text += f"\n\t\t{number}\n"
                        for dt, vl in el.items():
                            if dt != "number":
                                text += f"\t\t>> {rus_lan[eng_lan.index(dt)]} - {vl}\n"
        text += "\n\n\n\n"

    with open("data.pickle", "wb") as f:
        pickle.dump(data, f)
    with open("data.txt", "w", encoding="Windows-1251") as file:
        file.write(str(text))


def read_data() -> dict:
    """чтение сохраненных файлов для получения данных. При их отсутствии создаются новые"""
    if not os.path.exists("./data.pickle"):
        new_file = open("data.pickle", "w")
        new_file.close()
        return {}
    try:
        with open("data.pickle", "rb") as f:
            data = pickle.load(f)
            return data
    except EOFError:
        return {}


def see_static() -> tuple:
    """Просмотр статистики (смена - отработано часов - заработано руб)"""
    text = ""
    summa = 0
    hours = 0
    for num_sift, val_shift in shifts.items():
        text += f"{num_sift}   >  {val_shift["all plan time"]} ч  >   {val_shift["payment"]} р\n"
        summa += val_shift["payment"]
        hours += val_shift["all plan time"]
    summa_text = f"Всего:\n{summa} руб\n{hours} ч"
    return text, summa_text


@dp.message(Command(commands=['start']))
async def start(message: Message):
    await message.answer("Это бот созданный для помощи отслеживания работы\n"
                         "Для более полной информации вызовите команду /help",
                         reply_markup=keyboard_add_shift)


@dp.message(Command(commands=["help"]))
async def helping(message: Message):
    await message.answer("Действия:\n\n"
                         "Добавить смену  ->\n"
                         "Начать смену  ->\n"
                         "Добавлять по закакзы (номер и сумму выплаты)  ->\n"
                         "Закончить смену\n\n"
                         "Все сохранения происходят автоматически")
    await message.answer("Команды:\n"
                         "/stat - показать статистику\n"
                         "/clear - очистить данные\n")


@dp.message(Command(commands=["clear"]))
async def clear_data(message: Message):
    global shifts
    await message.answer("Удаление данных...")
    try:
        with open("data.pickle", "w"):
            pass
        with open("data.txt", "w"):
            pass
        shifts = {}
        await message.answer("Файлы были удалены")
    except Exception as e:
        await message.answer("Файлов сохранения нет")


@dp.message(Command(commands=['stat']))
async def start(message: Message):
    if shifts:
        statistic = see_static()
        await message.answer(text=statistic[0])
        await message.answer(text=statistic[1])
    else:
        await message.answer("Даные отсутствуют")


@dp.message(F.text.lower() == "добавить смену")
async def work_with_shift(message: Message):
    global registrate_shift
    registrate_shift = True
    await message.answer("Укажите время начала и конца смены через пробел\n"
                         "Время должно именть такой вид:\n"
                         "12 15")
    shift_time = message.text


@dp.message(F.text == "Начать смену")
async def start_shift(message: Message):
    global shift
    if shift.exsisting:

        shift.start_shift()
        fact_start = time.localtime(time.time())
        shift.take_fact_start((fact_start[3], fact_start[4]))

        await message.answer(f"Смена {shift.plan_start_time}:00 - {shift.plan_end_time}:00 началась в "
                             f"{shift.fact_start_time[0]}:{shift.fact_start_time[1]}", reply_markup=keyboard_work_shift)

    else:
        await message.answer("Сначала зарегситрируйте смену")


@dp.message(F.text == "Закончить смену")
async def end_shift(message: Message):
    global shift
    fact_end = time.localtime(time.time())
    shift.take_fact_end((fact_end[3], fact_end[4]))
    shift.count_all_time(shift.fact_start_time, shift.fact_end_time)
    shift.count_all_plan_time(shift.plan_start_time, shift.plan_end_time)

    shift.end_shift()
    structing_shift = shift.struct_shift()
    await message.answer("Смена закончена!", reply_markup=keyboard_add_shift)

    date_now = {"day": time.localtime(time.time())[2], "month": time.localtime(time.time())[1]}
    shifts.update([(F"{date_now["day"]}.{date_now["month"]}  {structing_shift["plan time"]}", structing_shift)])
    save_data(shifts)
    read_data()
    shift = Shift(0, 0)


@dp.message(F.text == "Новый заказ")
async def start_add_order(message: Message):
    global registrate_order
    registrate_order = True
    await message.answer("Регистрация заказа\nУкажите номер")


@dp.message(F.text[0].in_(["H", "Н"]))
async def add_number_order(message: Message):
    if registrate_order:
        shift.add_order(message.text)
        await message.answer("Укажите выплату ")
    else:
        await message.answer("Сначала добавтье заказ")


@dp.message(F.text.isdigit())
async def save_order(message: Message):
    global registrate_order
    if shift.new_order.active:
        shift.new_order.take_pay(message.text)
        pay_time = (time.localtime(time.time())[3], time.localtime(time.time())[1])
        shift.new_order.take_time(pay_time)

        shift.struct_order()
        shift.save_order_in_orders()

        await message.answer(f"Заказ {shift.new_order.number} сохранен, сумма - {shift.new_order.pay}")
        registrate_order = False
        shift.new_order.active = False

    else:
        await message.answer("Не можем найти заказ")


@dp.message(F.text)
async def settings_shift(message: Message):
    global registrate_shift, shift
    if registrate_shift:
        start_t, end_t = int(message.text.split()[0]), int(message.text.split()[1])
        shift = Shift(start_t, end_t)
        shift.exsisting = True
        await message.answer(f"Смена {shift.plan_start_time}:00 - {shift.plan_end_time}:00 зарегистрирована", reply_markup=keyboard_start_shift)
        registrate_shift = False


if __name__ == "__main__":
    print("start")
    shifts = read_data()
    dp.run_polling(bot)
