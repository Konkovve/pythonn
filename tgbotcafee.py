#tg - @cafe_sir_bot


import json 
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(filename='bot_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class Menu:
    def __init__(self):
        self.items = {
            "1": {"name": "Кофе", "price": 100},
            "2": {"name": "Чай", "price": 50},
            "3": {"name": "Пирожное", "price": 150},
            "4": {"name": "Стейк", "price": 1500},
            "5": {"name": "Морсик", "price": 120},
            "6": {"name": "Хлеб к заказу", "price": 30},
            "7": {"name": "Салат Оливье", "price": 444},

        }

    def get_menu_text(self):
        return "\n".join([f"{key}: {item['name']} - {item['price']} руб." for key, item in self.items.items()])

class Order:
    def __init__(self):
        self.items = []
        self.total = 0

    def add_item(self, item_id, menu):
        if item_id in menu.items:
            item = menu.items[item_id]
            self.items.append(item)
            self.total += item["price"]

    def clear_order(self):
        self.items = []
        self.total = 0

    def get_order_text(self):
        if not self.items:
            return "Корзина пуста."
        order_list = "\n".join([f"- {item['name']} ({item['price']} руб.)" for item in self.items])
        return f"Ваш заказ:\n{order_list}\n\nИтого: {self.total} руб."

    def save_order(self, username):
        order_data = {
            "user": username,
            "items": self.items,
            "total": self.total,
        }
        with open("orders.json", "a") as f:
            f.write(json.dumps(order_data, ensure_ascii=False) + "\n")

class CafeBot:
    def __init__(self):
        self.menu = Menu()
        self.orders = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        self.orders[chat_id] = Order()
        logger.info(f"Пользователь {update.effective_user.username} запустил бота.")

        keyboard = [
            ["Добавить блюдо"],
            ["Моя корзина", "Очистить корзину"],
            ["Оформить заказ"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "Добро пожаловать в виртуальное кафе!\n" "Выберите действие:", reply_markup=reply_markup
        )

    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info(f"Пользователь {update.effective_user.username} запросил меню.")
        await update.message.reply_text(f"Меню:\n{self.menu.get_menu_text()}")

    async def add(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info(f"Пользователь {update.effective_user.username} начал добавление блюда.")
        await update.message.reply_text("Введите номер блюда для добавления в заказ:\n" + self.menu.get_menu_text())

    async def add_item(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        item_id = update.message.text.strip()

        if chat_id not in self.orders:
            self.orders[chat_id] = Order()

        if item_id in self.menu.items:
            self.orders[chat_id].add_item(item_id, self.menu)
            logger.info(f"Пользователь {update.effective_user.username} добавил блюдо {item_id} в заказ.")
            await update.message.reply_text("Блюдо добавлено в заказ.")
        else:
            logger.warning(f"Пользователь {update.effective_user.username} ввел некорректный номер блюда: {item_id}.")
            await update.message.reply_text("Некорректный номер блюда.")


    async def order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        order = self.orders.get(chat_id, Order())
        logger.info(f"Пользователь {update.effective_user.username} запросил содержимое корзины.")
        await update.message.reply_text(order.get_order_text())

    async def clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        if chat_id in self.orders:
            self.orders[chat_id].clear_order()
        logger.info(f"Пользователь {update.effective_user.username} очистил корзину.")
        await update.message.reply_text("Корзина очищена.")

    async def checkout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        username = update.effective_user.username
        order = self.orders.get(chat_id, Order())

        if not order.items:
            logger.info(f"Пользователь {username} попытался оформить пустой заказ.")
            await update.message.reply_text("Корзина пуста. Добавьте блюда перед оформлением заказа.")
        else:
            order.save_order(username)
            logger.info(f"Пользователь {username} оформил заказ на сумму {order.total} руб.")
            self.orders[chat_id].clear_order()
            await update.message.reply_text("Ваш заказ оформлен! Спасибо за покупку.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip().lower()
        if text == "меню":
            await self.menu(update, context)
        elif text == "добавить блюдо":
            await self.add(update, context)
        elif text == "моя корзина":
            await self.order(update, context)
        elif text == "очистить корзину":
            await self.clear(update, context)
        elif text == "оформить заказ":
            await self.checkout(update, context)
        else:
            await self.add_item(update, context)

def main():
    cafe_bot = CafeBot()
    app = ApplicationBuilder().token("8157544097:AAGNJ5N9ZnGaNDOqWZiIg-YKgkUgx_iu6Y0").build()

    app.add_handler(CommandHandler("start", cafe_bot.start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cafe_bot.handle_message))

    logger.info("Бот запущен и готов к работе.")
    app.run_polling()

if __name__ == "__main__":
    main()