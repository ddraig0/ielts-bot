from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
import keyboards as kb
from config import ADMIN_IDS, SUBSCRIPTION_PRICE

router = Router()

PAYMENT_INFO = """💳 *Ödəniş Məlumatları*

Ödəniş üsulları:
• 🏦 Bank köçürməsi: AZ00 AZIB 0000 0000 0000 0000 00
• 📱 M10: +994 50 000 00 00
• 💰 Kapital Bank: +994 55 000 00 00

*Qeyd:* Ödəniş zamanı Telegram istifadəçi adınızı (@username) şərh kimi qeyd edin.

Ödəniş etdikdən sonra ekran görüntüsünü adminə göndərin:
👤 @your_admin_username

✅ Admin 24 saat ərzində abunəliyi aktivləşdirəcək."""

@router.callback_query(F.data == "subscription_info")
async def cb_subscription_info(call: CallbackQuery):
    status = db.get_access_status(call.from_user.id)
    s = status["status"]
    
    if s == "subscribed":
        text = (
            f"✅ *Aktiv Abunəliyiniz Var*\n\n"
            f"📅 {status['days_left']} gün qalıb\n\n"
            f"Uzatmaq istəyirsinizsə, ödəniş edin — mövcud abunəliyinizin üzərinə əlavə olunacaq."
        )
    elif s == "trial":
        text = f"🆓 *Sınaq Dövrünüz:* {status['days_left']} gün qalıb\n\nSınaq bitdikdən sonra davam etmək üçün abunə olun:"
    else:
        text = "💳 *Abunəlik Planları*\n\nBütün bölmələrə tam giriş:"
    
    await call.message.edit_text(
        text + f"\n\n💰 1 ay — {SUBSCRIPTION_PRICE} AZN\n💰 3 ay — 40 AZN\n💰 6 ay — 70 AZN",
        parse_mode="Markdown",
        reply_markup=kb.subscription_keyboard()
    )

@router.callback_query(F.data.startswith("pay_"))
async def cb_pay(call: CallbackQuery):
    plan = call.data.replace("pay_", "")
    
    if plan == "1month":
        amount = SUBSCRIPTION_PRICE
        months = 1
        label = "1 ay"
    elif plan == "3months":
        amount = 40
        months = 3
        label = "3 ay"
    else:
        amount = 70
        months = 6
        label = "6 ay"
    
    text = (
        f"💳 *{label} — {amount} AZN*\n\n"
        f"{PAYMENT_INFO}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 Ödəniş detallarınız:\n"
        f"• Məbləğ: *{amount} AZN*\n"
        f"• Müddət: *{months} ay*\n"
        f"• İstifadəçi ID: `{call.from_user.id}`"
    )
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.back_to_menu())
