from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import Database
import config
from handlers import get_main_menu
import sqlite3
router = Router()


class AdminStates(StatesGroup):
    WAITING_FOR_SERVER_NAME = State()
    WAITING_FOR_CHANNEL_ID = State()
    WAITING_FOR_MODERATION_GROUP = State()
# Состояния для добавления администратора
class AdminStatesTwo(StatesGroup):
    WAITING_FOR_ADMIN_ID = State()  # Ожидаем ID нового администратора

# Кнопки для админки
admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить администратора")],
        [KeyboardButton(text="➕ Добавить Группу")],
        [KeyboardButton(text="📋 Список Групп")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Кнопка назад
back_button = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⬅️ Назад")]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Обработка нажатия на кнопку "🛠 Админ-панель"
@router.message(F.text == "🛠 Админ-панель")
async def admin_panel(message: Message):
    if not Database.is_admin(message.from_user.id) and message.from_user.id not in config.ADMIN_IDS:
        await message.answer("У вас нет доступа к админ-панели")
        return

    await message.answer("Выберите действие:", reply_markup=admin_menu)

# Обработка кнопки "Назад" для возвращения в главное меню
@router.message(F.text == "⬅️ Назад")
async def back_to_main_menu(message: Message):
    await message.answer("Вы вернулись в главное меню.", reply_markup=get_main_menu(message.from_user.id))



@router.message(lambda msg: msg.text == "➕ Добавить Группу")
async def add_server_start(message: Message, state: FSMContext):
    if not Database.is_admin(message.from_user.id) and message.from_user.id not in config.ADMIN_IDS:
        return

    await message.answer("Введите название сервера:", reply_markup=back_button)
    await state.set_state(AdminStates.WAITING_FOR_SERVER_NAME)


@router.message(lambda msg: msg.text == "📋 Список Групп")
async def list_servers(message: Message):
    if not Database.is_admin(message.from_user.id) and message.from_user.id not in config.ADMIN_IDS:
        return

    db = Database()
    servers = db.get_servers()
    db.close()

    if not servers:
        await message.answer("Серверов пока нет")
        return

    response = "Список серверов:\n\n"
    for server_id, name in servers:
        response += f"{server_id}. {name}\n"

    await message.answer(response)


@router.message(AdminStates.WAITING_FOR_SERVER_NAME)
async def process_server_name(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await state.clear()
        await message.answer("Вы вернулись в админ-панель", reply_markup=admin_menu)
        return

    await state.update_data(server_name=message.text)
    await message.answer("Введите ID канала для публикации объявлений:", reply_markup=back_button)
    await state.set_state(AdminStates.WAITING_FOR_CHANNEL_ID)


@router.message(AdminStates.WAITING_FOR_CHANNEL_ID)
async def process_channel_id(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await state.clear()
        await message.answer("Вы вернулись в админ-панель", reply_markup=admin_menu)
        return

    await state.update_data(channel_id=message.text)
    await message.answer("Введите ID группы модерации:", reply_markup=back_button)
    await state.set_state(AdminStates.WAITING_FOR_MODERATION_GROUP)


@router.message(AdminStates.WAITING_FOR_MODERATION_GROUP)
async def process_moderation_group(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await state.clear()
        await message.answer("Вы вернулись в админ-панель", reply_markup=admin_menu)
        return

    data = await state.get_data()
    db = Database()
    try:
        db.add_server(
            name=data['server_name'],
            channel_id=data['channel_id'],
            moderation_group_id=message.text
        )
        await message.answer("Сервер успешно добавлен!", reply_markup=admin_menu)
    except Exception as e:
        await message.answer(f"Ошибка при добавлении сервера: {str(e)}", reply_markup=admin_menu)
    finally:
        db.close()
        await state.clear()


# Обработка нажатия на кнопку "Добавить администратора"
@router.message(F.text == "Добавить администратора")
async def add_admin(message: Message, state: FSMContext):
    if not Database.is_admin(message.from_user.id) and message.from_user.id not in config.ADMIN_IDS:
        await message.answer("У вас нет доступа к этой функции.")
        return

    await message.answer("Введите ID пользователя, которого вы хотите добавить в администраторы:")
    await state.set_state(AdminStatesTwo.WAITING_FOR_ADMIN_ID)

@router.message(AdminStatesTwo.WAITING_FOR_ADMIN_ID)
async def process_admin_id(message: Message, state: FSMContext):
    user_id = message.text

    # Проверка, что ID — число
    if not user_id.isdigit():
        await message.answer("Пожалуйста, введите корректный ID пользователя.")
        return

    user_id = int(user_id)

    # Подключение к базе данных
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    # Проверка, существует ли пользователь
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        await message.answer(f"Пользователь с ID {user_id} не найден в базе данных.")
        conn.close()
        await state.clear()
        return

    # Обновляем роль
    cursor.execute("UPDATE users SET role = 'admin' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    await message.answer(f"Пользователь с ID {user_id} теперь администратор.")

    await state.clear()

    await message.answer("Выберите действие:", reply_markup=admin_menu)