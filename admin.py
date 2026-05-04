from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
import keyboards as kb
from config import ADMIN_IDS, SUBSCRIPTION_PRICE
import datetime

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

class AdminState(StatesGroup):
    waiting_user_id_payment = State()
    waiting_months = State()
    waiting_user_id_ban = State()

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    stats = db.get_stats()
    text = (
        f"👑 *Admin Panel*\n\n"
        f"📊 Statistika:\n"
        f"• Ümumi istifadəçi: *{stats['total_users']}*\n"
        f"• Aktiv abunəçi: *{stats['active_subscriptions']}*\n"
        f"• Sınaq dövrü: *{stats['trial_users']}*\n"
        f"• Ümumi ödəniş: *{stats['total_payments']}*\n"
        f"• Ümumi gəlir: *{stats['total_revenue']:.2f} AZN*"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=kb.admin_keyboard())

@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    stats = db.get_stats()
    text = (
        f"📊 *Canlı Statistika*\n\n"
        f"👥 Ümumi istifadəçi: *{stats['total_users']}*\n"
        f"✅ Aktiv abunəçi: *{stats['active_subscriptions']}*\n"
        f"🆓 Sınaq dövrü: *{stats['trial_users']}*\n"
        f"💳 Ümumi ödəniş: *{stats['total_payments']}*\n"
        f"💰 Ümumi gəlir: *{stats['total_revenue']:.2f} AZN*"
    )
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.admin_keyboard())

@router.callback_query(F.data == "admin_users")
async def cb_admin_users(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    
    users = db.get_all_users()
    now = datetime.datetime.now()
    
    lines = []
    for u in users[-20:]:  # Last 20
        uid, uname, name, sub_end, trial_end, banned = u
        status = "🚫" if banned else ("✅" if sub_end and datetime.datetime.fromisoformat(sub_end) > now else "🆓")
        lines.append(f"{status} {name} (@{uname or '?'}) — ID: `{uid}`")
    
    text = f"👥 *Son 20 İstifadəçi:*\n\n" + "\n".join(lines)
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.admin_keyboard())

@router.callback_query(F.data == "admin_confirm_payment")
async def cb_admin_confirm_payment(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await state.set_state(AdminState.waiting_user_id_payment)
    await call.message.edit_text("💳 *Ödəniş Təsdiqləmə*\n\nİstifadəçinin ID-sini göndərin:", parse_mode="Markdown")

@router.message(AdminState.waiting_user_id_payment)
async def process_payment_user_id(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        user_id = int(message.text.strip())
        user = db.get_user(user_id)
        if not user:
            await message.answer("❌ İstifadəçi tapılmadı.")
            await state.clear()
            return
        await state.update_data(target_user_id=user_id)
        await state.set_state(AdminState.waiting_months)
        await message.answer(
            f"✅ İstifadəçi tapıldı: *{user['full_name']}*\n\nNeçə aylıq abunəlik əlavə edilsin? (1, 3, 6 və ya digər):",
            parse_mode="Markdown"
        )
    except ValueError:
        await message.answer("❌ Düzgün ID daxil edin.")
        await state.clear()

@router.message(AdminState.waiting_months)
async def process_payment_months(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        months = int(message.text.strip())
        data = await state.get_data()
        user_id = data["target_user_id"]
        amount = months * SUBSCRIPTION_PRICE
        
        new_end = db.add_subscription(user_id, months, message.from_user.id, amount)
        await state.clear()
        
        # Notify user
        try:
            from aiogram import Bot
            from config import BOT_TOKEN
            bot = Bot(token=BOT_TOKEN)
            await bot.send_message(
                user_id,
                f"🎉 *Abunəliyiniz Aktivləşdirildi!*\n\n"
                f"✅ {months} aylıq abunəlik əlavə olundu.\n"
                f"📅 Bitmə tarixi: *{new_end.strftime('%d.%m.%Y')}*\n\n"
                f"IELTS hazırlığınızda uğurlar! 🚀",
                parse_mode="Markdown"
            )
            await bot.session.close()
        except:
            pass
        
        await message.answer(
            f"✅ *Abunəlik Əlavə Edildi!*\n\n"
            f"İstifadəçi: `{user_id}`\n"
            f"Müddət: {months} ay\n"
            f"Bitmə: {new_end.strftime('%d.%m.%Y')}",
            parse_mode="Markdown",
            reply_markup=kb.admin_keyboard()
        )
    except ValueError:
        await message.answer("❌ Düzgün ay sayı daxil edin.")
        await state.clear()

@router.callback_query(F.data == "admin_ban")
async def cb_admin_ban(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await state.set_state(AdminState.waiting_user_id_ban)
    await call.message.edit_text("🚫 Banlayacağınız istifadəçinin ID-sini göndərin:", parse_mode="Markdown")

@router.message(AdminState.waiting_user_id_ban)
async def process_ban_user(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        user_id = int(message.text.strip())
        db.ban_user(user_id, ban=True)
        await state.clear()
        await message.answer(f"🚫 İstifadəçi `{user_id}` banlandı.", parse_mode="Markdown", reply_markup=kb.admin_keyboard())
    except ValueError:
        await message.answer("❌ Düzgün ID daxil edin.")
        await state.clear()

# /broadcast command
@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    if not is_admin(message.from_user.id):
        return
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        await message.answer("İstifadə: /broadcast [mesaj]")
        return
    
    users = db.get_all_users()
    from aiogram import Bot
    from config import BOT_TOKEN
    bot = Bot(token=BOT_TOKEN)
    
    success = 0
    for u in users:
        try:
            await bot.send_message(u[0], f"📢 *Elan:*\n\n{text}", parse_mode="Markdown")
            success += 1
        except:
            pass
    
    await bot.session.close()
    await message.answer(f"✅ {success}/{len(users)} istifadəçiyə göndərildi.")
