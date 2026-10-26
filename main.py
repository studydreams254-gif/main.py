import os
import random
import asyncio
import sqlite3
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = "8868240972:AAHjAeJYp9o4n_MUJd_Ne5qdVvKC6s74XLM"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- MAVZULAR BO'YICHA SAVOLLAR BAZASI ---
CATEGORIES_DATA = {
    "🐍 Python / IT": [
        {
            "question": "Python dasturlash tili ilk bor qaysi yilda taqdim etilgan?",
            "options": ["1989-yil", "1991-yil", "2000-yil", "1995-yil"],
            "correct_id": 1,
            "explanation": "Python 1991-yilda Guido van Rossum tomonidan ommaga taqdim etilgan."
        },
        {
            "question": "Python-da funksiya yaratish uchun qaysi kalit so'z ishlatiladi?",
            "options": ["func", "def", "function", "create"],
            "correct_id": 1,
            "explanation": "Python'da funksiyalar 'def' (define) so'zi orqali e'lon qilinadi."
        },
        {
            "question": "Kompyuterning 'miyasi' deb ataladigan asosiy qurilma nima?",
            "options": ["Protsessor (CPU)", "Operativ xotira (RAM)", "Qattiq disk (SSD)", "Videokarta"],
            "correct_id": 0,
            "explanation": "CPU kompyuterning barcha hisob-kitoblarini bajaruvchi asosiy qurilma."
        },
        {
            "question": "Python-da o'zgarmas (immutable) to'plam turi qaysi?",
            "options": ["list", "dict", "tuple", "set"],
            "correct_id": 2,
            "explanation": "Tuple elementlari yaratilgandan so'ng ularni o'zgartirib bo'lmaydi."
        },
        {
            "question": "Python-da ro'yxatga (list) yangi element qo'shish metodi qaysi?",
            "options": ["add()", "push()", "append()", "insert_end()"],
            "correct_id": 2,
            "explanation": "Python ro'yxatlarida 'append()' metodi elementni oxiriga qo'shadi."
        }
    ],
    "🌍 Geografiya": [
        {
            "question": "Yer sharidagi eng baland cho'qqi qaysi?",
            "options": ["Everest (Jomolungma)", "K2", "Monblan", "Elbrus"],
            "correct_id": 0,
            "explanation": "Everest dengiz sathidan 8848 metr baland bo'lib, eng baland cho'qqidir."
        },
        {
            "question": "Quyosh sistemasidagi eng katta sayyora qaysi?",
            "options": ["Mars", "Saturn", "Yupiter", "Venera"],
            "correct_id": 2,
            "explanation": "Yupiter o'lchami bo'yicha Quyosh sistemasidagi eng yirik sayyoradir."
        },
        {
            "question": "Dunyoda eng ko'p aholiga ega davlat qaysi?",
            "options": ["Xitoy", "AQSH", "Hindiston", "Indoneziya"],
            "correct_id": 2,
            "explanation": "Hozirgi vaqtda Hindiston dunyoda aholi soni bo'yicha 1-o'rinda turadi."
        },
        {
            "question": "Dunyodagi eng katta okean qaysi?",
            "options": ["Atlantika okeani", "Tinch okeani", "Hind okeani", "Shimoliy muz okeani"],
            "correct_id": 1,
            "explanation": "Tinch okeani Yer yuzidagi eng ulkan va chuqur okeandir."
        },
        {
            "question": "Qadimgi dunyo mo'jizasi bo'lgan Piramidalar qaysi davlatda joylashgan?",
            "options": ["Gretsiya", "Misr", "Turkiya", "Iroq"],
            "correct_id": 1,
            "explanation": "Giza piramidalari Misr davlatida joylashgan."
        }
    ],
    "📜 Tarix": [
        {
            "question": "Sohibqiron Amir Temur qaysi yilda tavallud topgan?",
            "options": ["1342-yil", "1336-yil", "1370-yil", "1380-yil"],
            "correct_id": 1,
            "explanation": "Amir Temur 1336-yil 9-aprelda Xo'ja Ilg'or qishlog'ida tug'ilgan."
        },
        {
            "question": "O'zbekiston BMTga qaysi yilda a'zo bo'lgan?",
            "options": ["1991-yil", "1992-yil", "1993-yil", "1995-yil"],
            "correct_id": 1,
            "explanation": "O'zbekiston 1992-yil 2-martda BMTga to'laqonli a'zo bo'lgan."
        },
        {
            "question": "Buyuk shoir Alisher Navoiy qaysi shaharda tavallud topgan?",
            "options": ["Hirot", "Samarqand", "Buxoro", "Toshkent"],
            "correct_id": 0,
            "explanation": "Alisher Navoiy 1441-yil 9-fevralda Hirot shahrida tug'ilgan."
        },
        {
            "question": "Mirzo Ulug'bek qaysi shaharda mashhur rasadxona qurdirgan?",
            "options": ["Hirot", "Samarqand", "Buxoro", "Shahrisabz"],
            "correct_id": 1,
            "explanation": "Ulug'bek rasadxonasi 1420-yillarda Samarqandda barpo etilgan."
        },
        {
            "question": "O'zbekiston Respublikasi mustaqillikka qachon erishgan?",
            "options": ["1989-yil 1-sentabr", "1990-yil 31-avgust", "1991-yil 1-sentabr", "1992-yil 8-dekabr"],
            "correct_id": 2,
            "explanation": "O'zbekiston mustaqilligi 1991-yil 1-sentabrda e'lon qilingan."
        }
    ]
}

# --- MA'LUMOTLAR BAZASI (SQLite) ---
def init_db():
    conn = sqlite3.connect("quiz_game.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            high_score INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def save_score(user_id: int, full_name: str, score: int):
    conn = sqlite3.connect("quiz_game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT high_score FROM players WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row is None:
        cursor.execute("INSERT INTO players (user_id, full_name, high_score) VALUES (?, ?, ?)",
                       (user_id, full_name, score))
    else:
        if score > row[0]:
            cursor.execute("UPDATE players SET high_score = ?, full_name = ? WHERE user_id = ?",
                           (score, full_name, user_id))
    conn.commit()
    conn.close()

def get_top_players():
    conn = sqlite3.connect("quiz_game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, high_score FROM players ORDER BY high_score DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    return rows

user_states = {}

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Testni boshlash")],
        [KeyboardButton(text="🏆 Reyting (Top-10)")]
    ],
    resize_keyboard=True
)

category_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🐍 Python / IT"), KeyboardButton(text="🌍 Geografiya")],
        [KeyboardButton(text="📜 Tarix"), KeyboardButton(text="🎲 Aralash test")],
        [KeyboardButton(text="⬅️ Bosh menyuga qaytish")]
    ],
    resize_keyboard=True
)

async def send_next_question(user_id: int):
    state = user_states.get(user_id)
    if not state:
        return

    step = state["step"]
    quiz = state["questions"][step]

    await bot.send_poll(
        chat_id=user_id,
        question=f"[{state['category']}] ❓ {step + 1}/{len(state['questions'])}. {quiz['question']}",
        options=quiz["options"],
        type="quiz",
        correct_option_id=quiz["correct_id"],
        explanation=quiz["explanation"],
        open_period=20,
        is_anonymous=False
    )

    asyncio.create_task(timer_checker(user_id, step))

async def timer_checker(user_id: int, current_step: int):
    await asyncio.sleep(21)
    state = user_states.get(user_id)
    if state and state["step"] == current_step:
        await bot.send_message(user_id, "⌛ <b>Vaqt tugadi!</b> Keyingi savolga o'tamiz...", parse_mode="HTML")
        await advance_quiz(user_id)

async def advance_quiz(user_id: int):
    state = user_states.get(user_id)
    if not state:
        return

    state["step"] += 1
    total = len(state["questions"])

    if state["step"] < total:
        await asyncio.sleep(1)
        await send_next_question(user_id)
    else:
        score = state["score"]
        save_score(user_id, state["name"], score)
        percentage = int((score / total) * 100)

        if percentage >= 80:
            status = "A'lo natija! 🎓👏"
        elif percentage >= 60:
            status = "Yaxshi! 👍"
        else:
            status = "Yana sinab ko'ring! 💪"

        result_text = (
            f"🏁 <b>Test yakunlandi!</b>\n\n"
            f"📚 Yo'nalish: <b>{state['category']}</b>\n"
            f"👤 Ishtirokchi: <b>{state['name']}</b>\n"
            f"🎯 Natija: <b>{score} / {total}</b> ta to'g'ri\n"
            f"📈 Samaradorlik: <b>{percentage}%</b>\n"
            f"🏆 Baho: <i>{status}</i>\n\n"
            f"<i>Natijangiz umumiy reyting bazasiga saqlandi!</i>"
        )
        await bot.send_message(user_id, result_text, reply_markup=main_menu, parse_mode="HTML")
        del user_states[user_id]

# --- BUYRUQLAR ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        f"Assalomu alaykum, <b>{message.from_user.first_name}</b>!\n\n"
        "🎯 <b>Intellektual Quiz Bot</b>ga xush kelibsiz.\n"
        "Boshlash uchun pastdagi <b>'🚀 Testni boshlash'</b> tugmasini bosing:",
        reply_markup=main_menu,
        parse_mode="HTML"
    )

@dp.message(F.text == "🚀 Testni boshlash")
@dp.message(Command("quiz"))
async def choose_category_handler(message: types.Message):
    await message.answer(
        "📚 Qaysi yo'nalish bo'yicha bilimingizni sinab ko'rmoqchisiz?\n"
        "Quyidagi fanlardan birini tanlang:",
        reply_markup=category_menu
    )

@dp.message(F.text == "⬅️ Bosh menyuga qaytish")
async def back_to_menu_handler(message: types.Message):
    await message.answer("Bosh menyudasiz:", reply_markup=main_menu)

@dp.message(F.text.in_(["🐍 Python / IT", "🌍 Geografiya", "📜 Tarix", "🎲 Aralash test"]))
async def start_quiz_category(message: types.Message):
    user_id = message.from_user.id
    selected_category = message.text

    if selected_category == "🎲 Aralash test":
        all_pool = []
        for cat_questions in CATEGORIES_DATA.values():
            all_pool.extend(cat_questions)
        chosen_questions = random.sample(all_pool, min(5, len(all_pool)))
    else:
        cat_pool = CATEGORIES_DATA[selected_category]
        chosen_questions = random.sample(cat_pool, min(5, len(cat_pool)))

    user_states[user_id] = {
        "step": 0,
        "score": 0,
        "questions": chosen_questions,
        "name": message.from_user.full_name,
        "category": selected_category
    }

    await message.answer(
        f"🚀 <b>{selected_category}</b> bo'yicha test boshlandi!\n"
        f"Jami: <b>{len(chosen_questions)} ta savol</b>. Omad!",
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="HTML"
    )
    await send_next_question(user_id)

@dp.poll_answer()
async def poll_answer_handler(quiz_answer: types.PollAnswer):
    user_id = quiz_answer.user.id
    state = user_states.get(user_id)
    if not state:
        return

    current_quiz = state["questions"][state["step"]]
    if quiz_answer.option_ids[0] == current_quiz["correct_id"]:
        state["score"] += 1

    await advance_quiz(user_id)

@dp.message(F.text == "🏆 Reyting (Top-10)")
async def leaderboard_handler(message: types.Message):
    top_players = get_top_players()
    if not top_players:
        await message.answer("Hozircha reyting jadvalida hech kim yo'q.")
        return

    text = "🏆 <b>Eng yuqori natijalar (Top-10):</b>\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, (name, score) in enumerate(top_players, 1):
        icon = medals[i - 1] if i <= 3 else f"{i}."
        text += f"{icon} <b>{name}</b> — {score} ball\n"

    await message.answer(text, parse_mode="HTML")

# --- RENDER SERVERI UCHUN TALAB QILINGAN QISM ---
async def handle_ping(request):
    return web.Response(text="Bot muvaffaqiyatli ishlayapti!")

async def main():
    init_db()

    # Render uchun portni ochish
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print(f"Bot va veb-server {port}-portda ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
