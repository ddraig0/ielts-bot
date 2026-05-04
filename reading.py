from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
import keyboards as kb
from ai_service import generate_reading_passage, check_reading_answer
from handlers.start import check_access
import json

router = Router()

class ReadingState(StatesGroup):
    answering = State()

@router.callback_query(F.data == "section_reading")
async def cb_reading_menu(call: CallbackQuery):
    if not await check_access(call):
        return
    await call.message.edit_text(
        "📖 *Reading Bölməsi*\n\nAI tərəfindən yaradılmış akademik IELTS mətnlərini oxuyun və sualları cavablandırın.\n\n🎯 5 sual • ⏱️ ~15 dəqiqə",
        parse_mode="Markdown",
        reply_markup=kb.reading_menu()
    )

@router.callback_query(F.data == "reading_new")
async def cb_reading_new(call: CallbackQuery, state: FSMContext):
    if not await check_access(call):
        return
    
    await call.message.edit_text("⏳ AI mətn hazırlayır... (10-15 saniyə)")
    db.log_usage(call.from_user.id, "reading")
    
    try:
        data = generate_reading_passage()
    except Exception as e:
        await call.message.edit_text(f"❌ Xəta baş verdi. Yenidən cəhd edin.", reply_markup=kb.reading_menu())
        return
    
    await state.set_state(ReadingState.answering)
    await state.update_data(passage_data=data, current_q=0, score=0)
    
    passage_text = (
        f"📖 *Mövzu: {data['topic'].title()}*\n\n"
        f"{data['passage']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 *{len(data['questions'])} sual var. Birinci sualı göndərirəm...*"
    )
    
    await call.message.edit_text(passage_text, parse_mode="Markdown")
    await _send_question(call.message, data, 0)

async def _send_question(message: Message, data: dict, q_index: int):
    q = data["questions"][q_index]
    total = len(data["questions"])
    
    q_text = f"❓ *Sual {q['num']}/{total}* — _{q['type']}_\n\n{q['question']}"
    
    if q["type"] == "Multiple Choice" and "options" in q:
        q_text += "\n\n" + "\n".join(q["options"])
        q_text += "\n\n💬 *Cavabınızı yazın (A, B, C, və ya D):*"
    elif q["type"] == "True/False/Not Given":
        q_text += "\n\n💬 *Cavabınızı yazın (TRUE / FALSE / NOT GIVEN):*"
    else:
        q_text += "\n\n💬 *Cavabınızı yazın:*"
    
    await message.answer(q_text, parse_mode="Markdown")

@router.message(ReadingState.answering)
async def process_reading_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    passage_data = data["passage_data"]
    current_q = data["current_q"]
    score = data["score"]
    
    questions = passage_data["questions"]
    q = questions[current_q]
    
    result = check_reading_answer(q, message.text)
    
    if result["is_correct"]:
        score += 1
        feedback = f"✅ *Düzgün!*\n\n💡 {result['explanation']}"
    else:
        feedback = f"❌ *Yanlış.*\n\nDüzgün cavab: *{result['correct_answer']}*\n\n💡 {result['explanation']}"
    
    next_q = current_q + 1
    await state.update_data(current_q=next_q, score=score)
    
    if next_q >= len(questions):
        # Finished
        await state.clear()
        band = _score_to_band(score, len(questions))
        summary = (
            f"{feedback}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏁 *Tapşırıq Tamamlandı!*\n\n"
            f"📊 Nəticəniz: *{score}/{len(questions)}*\n"
            f"🎯 Təxmini Band Score: *{band}*"
        )
        await message.answer(summary, parse_mode="Markdown", reply_markup=kb.reading_menu())
    else:
        await message.answer(feedback, parse_mode="Markdown")
        await _send_question(message, passage_data, next_q)

def _score_to_band(score: int, total: int) -> str:
    pct = score / total
    if pct >= 0.9: return "8.0-9.0"
    elif pct >= 0.75: return "7.0-7.5"
    elif pct >= 0.6: return "6.0-6.5"
    elif pct >= 0.45: return "5.0-5.5"
    else: return "4.0-4.5"
