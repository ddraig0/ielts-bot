from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
import keyboards as kb
from ai_service import generate_writing_task, evaluate_writing
from handlers.start import check_access

router = Router()

class WritingState(StatesGroup):
    writing_task1 = State()
    writing_task2 = State()

@router.callback_query(F.data == "section_writing")
async def cb_writing_menu(call: CallbackQuery):
    if not await check_access(call):
        return
    await call.message.edit_text(
        "✍️ *Writing Bölməsi*\n\nEsselerinizi AI IELTS ekspertinə göndərin — Band Score + ətraflı rəy alın!\n\n📊 *Task 1* — Qrafik/Cədvəl təsviri (min. 150 söz)\n✍️ *Task 2* — Əsaslandırılmış esse (min. 250 söz)",
        parse_mode="Markdown",
        reply_markup=kb.writing_menu()
    )

@router.callback_query(F.data == "writing_task1")
async def cb_writing_task1(call: CallbackQuery, state: FSMContext):
    if not await check_access(call):
        return
    db.log_usage(call.from_user.id, "writing_task1")
    task = generate_writing_task("task1")
    
    await state.set_state(WritingState.writing_task1)
    await state.update_data(task=task)
    
    text = (
        f"✍️ *IELTS Writing Task 1*\n\n"
        f"📋 *Tapşırıq:*\n{task['prompt']}\n\n"
        f"⏱️ Vaxt: {task['time_limit']}\n"
        f"📝 Min. söz sayı: {task['word_count']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💬 *Essenizi aşağıya yazın və göndərin:*"
    )
    await call.message.edit_text(text, parse_mode="Markdown")

@router.callback_query(F.data == "writing_task2")
async def cb_writing_task2(call: CallbackQuery, state: FSMContext):
    if not await check_access(call):
        return
    db.log_usage(call.from_user.id, "writing_task2")
    task = generate_writing_task("task2")
    
    await state.set_state(WritingState.writing_task2)
    await state.update_data(task=task)
    
    text = (
        f"✍️ *IELTS Writing Task 2*\n\n"
        f"📋 *Mövzu:*\n_{task['prompt']}_\n\n"
        f"⏱️ Vaxt: {task['time_limit']}\n"
        f"📝 Min. söz sayı: {task['word_count']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💬 *Essenizi aşağıya yazın və göndərin:*"
    )
    await call.message.edit_text(text, parse_mode="Markdown")

@router.message(WritingState.writing_task1)
async def process_writing_task1(message: Message, state: FSMContext):
    await _evaluate_essay(message, state, "task1")

@router.message(WritingState.writing_task2)
async def process_writing_task2(message: Message, state: FSMContext):
    await _evaluate_essay(message, state, "task2")

async def _evaluate_essay(message: Message, state: FSMContext, task_type: str):
    word_count = len(message.text.split())
    min_words = 150 if task_type == "task1" else 250
    
    if word_count < 50:
        await message.answer("⚠️ Esse çox qısa görünür. Tapşırığa uyğun tam esse yazın.")
        return
    
    data = await state.get_data()
    task = data["task"]
    
    await state.clear()
    await message.answer(f"⏳ AI essenizi qiymətləndirir... ({word_count} söz)\nBu 20-30 saniyə çəkə bilər.")
    
    if word_count < min_words:
        warning = f"\n\n⚠️ *Qeyd:* {word_count} söz yazmısınız, minimum {min_words} söz tələb olunur."
    else:
        warning = ""
    
    try:
        evaluation = evaluate_writing(task["prompt"], task_type, message.text)
        await message.answer(evaluation + warning, parse_mode="Markdown", reply_markup=kb.writing_menu())
    except Exception as e:
        await message.answer("❌ Qiymətləndirmə zamanı xəta baş verdi. Yenidən cəhd edin.", reply_markup=kb.writing_menu())
