from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
import keyboards as kb
from ai_service import generate_speaking_question, evaluate_speaking
from handlers.start import check_access

router = Router()

class SpeakingState(StatesGroup):
    part1_answering = State()
    part2_answering = State()
    part3_answering = State()

@router.callback_query(F.data == "section_speaking")
async def cb_speaking_menu(call: CallbackQuery):
    if not await check_access(call):
        return
    await call.message.edit_text(
        "🎙️ *Speaking Bölməsi*\n\nIELTS Speaking imtahanını simulyasiya edin. Cavablarınızı yazın — AI ətraflı rəy verəcək.\n\n💡 Real imtahanda danışırsınız, burada yazarak məşq edirsiniz.",
        parse_mode="Markdown",
        reply_markup=kb.speaking_menu()
    )

@router.callback_query(F.data == "speaking_part1")
async def cb_speaking_part1(call: CallbackQuery, state: FSMContext):
    if not await check_access(call):
        return
    db.log_usage(call.from_user.id, "speaking_part1")
    
    q_data = generate_speaking_question(1)
    await state.set_state(SpeakingState.part1_answering)
    await state.update_data(q_data=q_data, current_q=0, answers=[])
    
    text = (
        f"🎙️ *IELTS Speaking Part 1*\n"
        f"_{q_data['title']}_\n\n"
        f"⏱️ {q_data['time']}\n\n"
        f"💡 _{q_data['tip']}_\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"❓ *Sual 1:* {q_data['questions'][0]}\n\n"
        f"💬 *Cavabınızı yazın:*"
    )
    await call.message.edit_text(text, parse_mode="Markdown")

@router.message(SpeakingState.part1_answering)
async def process_speaking_part1(message: Message, state: FSMContext):
    data = await state.get_data()
    q_data = data["q_data"]
    current_q = data["current_q"]
    answers = data["answers"]
    
    answers.append({"question": q_data["questions"][current_q], "answer": message.text})
    next_q = current_q + 1
    
    if next_q < len(q_data["questions"]):
        await state.update_data(current_q=next_q, answers=answers)
        await message.answer(
            f"❓ *Sual {next_q + 1}:* {q_data['questions'][next_q]}\n\n💬 *Cavabınızı yazın:*",
            parse_mode="Markdown"
        )
    else:
        await state.clear()
        await message.answer("⏳ AI bütün cavablarınızı qiymətləndirir...")
        
        full_q = "\n".join([f"Q{i+1}: {a['question']}" for i, a in enumerate(answers)])
        full_a = "\n".join([f"A{i+1}: {a['answer']}" for i, a in enumerate(answers)])
        combined_q = f"Part 1 Questions:\n{full_q}"
        combined_a = f"Student answers:\n{full_a}"
        
        try:
            evaluation = evaluate_speaking(1, combined_q, combined_a)
            await message.answer(evaluation, parse_mode="Markdown", reply_markup=kb.speaking_menu())
        except:
            await message.answer("❌ Qiymətləndirmə xətası. Yenidən cəhd edin.", reply_markup=kb.speaking_menu())

@router.callback_query(F.data == "speaking_part2")
async def cb_speaking_part2(call: CallbackQuery, state: FSMContext):
    if not await check_access(call):
        return
    db.log_usage(call.from_user.id, "speaking_part2")
    
    q_data = generate_speaking_question(2)
    await state.set_state(SpeakingState.part2_answering)
    await state.update_data(q_data=q_data)
    
    card = q_data["cue_card"]
    points = "\n".join([f"   • {p}" for p in card["points"]])
    
    text = (
        f"🎙️ *IELTS Speaking Part 2*\n\n"
        f"🃏 *Cue Card:*\n*{card['title']}*\n\n"
        f"Haqqında danışın:\n{points}\n\n"
        f"⏱️ Hazırlıq: {q_data['prep_time']} | Danışıq: {q_data['speak_time']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💬 *Cavabınızı yazın (ən azı 150 söz):*"
    )
    await call.message.edit_text(text, parse_mode="Markdown")

@router.message(SpeakingState.part2_answering)
async def process_speaking_part2(message: Message, state: FSMContext):
    data = await state.get_data()
    q_data = data["q_data"]
    card = q_data["cue_card"]
    
    await state.clear()
    await message.answer("⏳ AI cavabınızı qiymətləndirir...")
    
    try:
        evaluation = evaluate_speaking(2, card["title"], message.text)
        
        # Add follow-up question
        follow_up = f"\n\n━━━━━━━━━━━━━━━━━━━━\n🔄 *Follow-up sual:*\n_{card['follow_up']}_"
        await message.answer(evaluation + follow_up, parse_mode="Markdown", reply_markup=kb.speaking_menu())
    except:
        await message.answer("❌ Qiymətləndirmə xətası.", reply_markup=kb.speaking_menu())

@router.callback_query(F.data == "speaking_part3")
async def cb_speaking_part3(call: CallbackQuery, state: FSMContext):
    if not await check_access(call):
        return
    db.log_usage(call.from_user.id, "speaking_part3")
    
    q_data = generate_speaking_question(3)
    await state.set_state(SpeakingState.part3_answering)
    await state.update_data(q_data=q_data, current_q=0, answers=[])
    
    text = (
        f"🎙️ *IELTS Speaking Part 3*\n"
        f"_{q_data['title']}_\n\n"
        f"💡 _{q_data['tip']}_\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"❓ *Sual 1:* {q_data['questions'][0]}\n\n"
        f"💬 *Cavabınızı yazın:*"
    )
    await call.message.edit_text(text, parse_mode="Markdown")

@router.message(SpeakingState.part3_answering)
async def process_speaking_part3(message: Message, state: FSMContext):
    data = await state.get_data()
    q_data = data["q_data"]
    current_q = data["current_q"]
    answers = data["answers"]
    
    answers.append({"question": q_data["questions"][current_q], "answer": message.text})
    next_q = current_q + 1
    
    if next_q < len(q_data["questions"]):
        await state.update_data(current_q=next_q, answers=answers)
        await message.answer(
            f"❓ *Sual {next_q + 1}:* {q_data['questions'][next_q]}\n\n💬 *Cavabınızı yazın:*",
            parse_mode="Markdown"
        )
    else:
        await state.clear()
        await message.answer("⏳ AI bütün cavablarınızı qiymətləndirir...")
        
        full_q = "\n".join([f"Q{i+1}: {a['question']}" for i, a in enumerate(answers)])
        full_a = "\n".join([f"A{i+1}: {a['answer']}" for i, a in enumerate(answers)])
        
        try:
            evaluation = evaluate_speaking(3, full_q, full_a)
            await message.answer(evaluation, parse_mode="Markdown", reply_markup=kb.speaking_menu())
        except:
            await message.answer("❌ Qiymətləndirmə xətası.", reply_markup=kb.speaking_menu())
