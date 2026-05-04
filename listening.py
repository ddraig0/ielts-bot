from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
import keyboards as kb
from ai_service import generate_listening_exercise, check_listening_answer
from handlers.start import check_access

router = Router()

class ListeningState(StatesGroup):
    answering = State()

@router.callback_query(F.data == "section_listening")
async def cb_listening_menu(call: CallbackQuery):
    if not await check_access(call):
        return
    await call.message.edit_text(
        "🎧 *Listening Bölməsi*\n\nReal IELTS imtahanında audio dinləyirsiniz. Burada AI tərəfindən yaradılmış transkrip əsasında məşq edirsiniz.\n\n🎯 4 sual • ⏱️ ~10 dəqiqə",
        parse_mode="Markdown",
        reply_markup=kb.listening_menu()
    )

@router.callback_query(F.data == "listening_new")
async def cb_listening_new(call: CallbackQuery, state: FSMContext):
    if not await check_access(call):
        return
    
    await call.message.edit_text("⏳ AI tapşırıq hazırlayır...")
    db.log_usage(call.from_user.id, "listening")
    
    try:
        data = generate_listening_exercise()
    except Exception as e:
        await call.message.edit_text("❌ Xəta baş verdi.", reply_markup=kb.listening_menu())
        return
    
    await state.set_state(ListeningState.answering)
    await state.update_data(exercise=data, current_q=0, score=0)
    
    text = (
        f"🎧 *Listening Tapşırığı*\n"
        f"_{data['scenario'].title()}_\n\n"
        f"📝 _{data.get('note', '')}_\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"*Transkrip:*\n\n{data['transcript']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 Mətni diqqətlə oxuyun, sonra sualları cavablandırın."
    )
    
    await call.message.edit_text(text, parse_mode="Markdown")
    await _send_listening_question(call.message, data, 0)

async def _send_listening_question(message: Message, data: dict, q_index: int):
    q = data["questions"][q_index]
    total = len(data["questions"])
    hint = f"\n💡 İpucu: _{q.get('hint', '')}_" if q.get('hint') else ""
    
    text = f"❓ *Sual {q['num']}/{total}*\n\n{q['question']}{hint}\n\n💬 *Cavabınızı yazın:*"
    await message.answer(text, parse_mode="Markdown")

@router.message(ListeningState.answering)
async def process_listening_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    exercise = data["exercise"]
    current_q = data["current_q"]
    score = data["score"]
    
    q = exercise["questions"][current_q]
    
    await message.answer("⏳ Cavabınız yoxlanılır...")
    
    try:
        result = check_listening_answer(q, message.text)
        is_correct = result.get("is_correct", False)
        feedback_text = result.get("feedback", "")
    except:
        is_correct = message.text.strip().lower() == q["answer"].strip().lower()
        feedback_text = f"Düzgün cavab: {q['answer']}"
    
    if is_correct:
        score += 1
        feedback = f"✅ *Düzgün!* {feedback_text}"
    else:
        feedback = f"❌ *Yanlış.* {feedback_text}"
    
    next_q = current_q + 1
    await state.update_data(current_q=next_q, score=score)
    
    if next_q >= len(exercise["questions"]):
        await state.clear()
        total = len(exercise["questions"])
        summary = (
            f"{feedback}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏁 *Tapşırıq Tamamlandı!*\n\n"
            f"📊 Nəticəniz: *{score}/{total}*"
        )
        await message.answer(summary, parse_mode="Markdown", reply_markup=kb.listening_menu())
    else:
        await message.answer(feedback, parse_mode="Markdown")
        await _send_listening_question(message, exercise, next_q)
