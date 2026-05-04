from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
import database as db
import keyboards as kb

router = Router()

WELCOME_TEXT = """🎓 *IELTS Hazırlıq Botuna Xoş Gəldiniz!*

Bu bot AI texnologiyası ilə sizi IELTS imtahanına hazırlayır:

📖 *Reading* — Akademik mətn anlama tapşırıqları
🎧 *Listening* — Dinləmə + sual cavablandırma  
✍️ *Writing* — AI tərəfindən qiymətləndirilən esselər
🎙️ *Speaking* — Danışıq sualları və qiymətləndirmə

⏰ *{trial_days} günlük pulsuz sınaq* sizinlə başlayır!
Sonra aylıq cəmi *15 AZN* ilə davam edin.

👇 Aşağıdan bölmə seçin:"""

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    is_new = db.register_user(user.id, user.username or "", user.full_name)
    
    from config import TRIAL_DAYS
    status = db.get_access_status(user.id)
    
    if is_new:
        text = WELCOME_TEXT.format(trial_days=TRIAL_DAYS)
        await message.answer(text, parse_mode="Markdown", reply_markup=kb.main_menu())
    else:
        status_text = _format_status(status)
        await message.answer(
            f"👋 Yenidən xoş gəldiniz, *{user.first_name}*!\n\n{status_text}",
            parse_mode="Markdown",
            reply_markup=kb.main_menu()
        )

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(call: CallbackQuery):
    await call.message.edit_text(
        "🏠 *Ana Menyu* — Bölmə seçin:",
        parse_mode="Markdown",
        reply_markup=kb.main_menu()
    )

@router.callback_query(F.data == "my_status")
async def cb_my_status(call: CallbackQuery):
    status = db.get_access_status(call.from_user.id)
    text = f"📊 *Hesab Statusunuz*\n\n{_format_status(status)}"
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.back_to_menu())

def _format_status(status: dict) -> str:
    s = status["status"]
    if s == "subscribed":
        return f"✅ *Aktiv Abunəlik* — {status['days_left']} gün qalıb"
    elif s == "trial":
        return f"🆓 *Sınaq Dövrü* — {status['days_left']} gün qalıb\n\n💡 Davam etmək üçün abunə olun!"
    elif s == "trial_expired":
        return "⏰ *Sınaq Dövrünüz Bitib*\n\n💳 Davam etmək üçün abunə olun — aylıq 10 AZN"
    elif s == "banned":
        return "🚫 Hesabınız bloklanıb. Dəstək üçün admin ilə əlaqə saxlayın."
    return "❓ Status müəyyən edilə bilmədi."

async def check_access(call: CallbackQuery) -> bool:
    """Helper: check if user has access, show paywall if not"""
    if not db.has_access(call.from_user.id):
        status = db.get_access_status(call.from_user.id)
        text = f"🔒 *Giriş Məhdudlaşdırıldı*\n\n{_format_status(status)}\n\n👇 Abunə olmaq üçün:"
        await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.subscription_keyboard())
        return False
    return True
