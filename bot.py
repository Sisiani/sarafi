import logging
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      KeyboardButton)
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler, MessageHandler,
                          filters, ContextTypes)

# ================= CONFIG =================
TOKEN = "8311865694:AAHrQDLSJcFKOztBj8X2PtMafk7U7AML0Uo"
ADMIN_ID = 7374971382  # آیدی عددی خودت به عنوان ادمین اصلی
GROUP_ID = -1003086390705
CHANNEL_LINK = "https://t.me/NEURANAcademy"

EXCHANGE_LINKS = {
    "XT": "https://www.xtfarsi.net/en/accounts/register?ref=1133",
    "TOOBIT": "https://www.toobit.com/t/lpOdP4",
    "OURBIT": "https://www.ourbit.com/register?inviteCode=S3ZCNR",
    "BITUNIX": "https://www.bitunix.com/register?vipCode=hajamin"
}

# ================= LOGGER =================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================= HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("⚡️ عضویت در Neuran academy 💰")],
        [KeyboardButton("💳 دریافت اشتراک"), KeyboardButton("🚀 دریافت بونس ویژه")],
        [KeyboardButton("📊 مشخصات حساب"), KeyboardButton("🛠 پشتیبانی")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("به ربات Neuran Academy خوش آمدید 🚀", reply_markup=reply_markup)

# دکمه پشتیبانی
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("برای پشتیبانی به این آیدی پیام دهید: @AIireza_1383")

# دریافت اشتراک
async def buy_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(name, url=link)] for name, link in EXCHANGE_LINKS.items()
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("لطفا یکی از صرافی‌ها را انتخاب کنید:", reply_markup=reply_markup)

# بعد از انتخاب صرافی
async def after_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    context.user_data["exchange"] = choice

    keyboard = [
        [KeyboardButton("از قبل حساب دارم"), KeyboardButton("ساخت حساب ندارم")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await query.message.reply_text("آیا از قبل در این صرافی حساب دارید یا خیر؟", reply_markup=reply_markup)

# کاربر حساب دارد
async def has_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    exchange = context.user_data.get("exchange", "صرافی")
    await update.message.reply_text(
        f"لطفا UID {exchange} خود را وارد کنید تا ادمین تایید کند و عضویت در کانال VIP برای شما آزاد شود."
    )
    context.user_data["waiting_for_uid"] = True

# گرفتن UID
async def get_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_for_uid"):
        uid = update.message.text
        tg_user = update.message.from_user
        msg = f"درخواست جدید ✅\nUID: {uid}\nیوزر: @{tg_user.username or tg_user.id}"
        await context.bot.send_message(GROUP_ID, msg)
        context.user_data["waiting_for_uid"] = False
        await update.message.reply_text("UID شما برای بررسی به ادمین ارسال شد. منتظر تایید باشید.")

# ادمین تایید می‌کند
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and "UID:" in update.message.reply_to_message.text:
        if update.message.text.strip() == "تایید":
            lines = update.message.reply_to_message.text.split("\n")
            user_line = [l for l in lines if l.startswith("یوزر")][0]
            username = user_line.replace("یوزر: ", "").strip()

            text = "تبریک 🎉 حساب شما توسط ادمین تایید شد. اکنون میتوانید به کانال VIP بپیوندید 🚀"
            button = InlineKeyboardMarkup([[InlineKeyboardButton("پیوستن به کانال", url=CHANNEL_LINK)]])

            if username.startswith("@"):  # کاربر یوزرنیم دارد
                await context.bot.send_message(username, text, reply_markup=button)

# پشتیبانی فقط ادمین -> ارسال پیام همگانی
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    msg = update.message.text.replace("/broadcast", "").strip()
    if not msg:
        await update.message.reply_text("لطفا متن پیام را وارد کنید.")
        return
    users = context.application.user_data.keys()
    for uid in users:
        try:
            await context.bot.send_message(uid, msg)
        except:
            pass
    await update.message.reply_text("پیام برای همه ارسال شد ✅")

# ================= MAIN =================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("🛠 پشتیبانی"), support))
    app.add_handler(MessageHandler(filters.Regex("💳 دریافت اشتراک"), buy_subscription))
    app.add_handler(MessageHandler(filters.Regex("از قبل حساب دارم"), has_account))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_uid))
    app.add_handler(MessageHandler(filters.Regex("^تایید$"), approve))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(after_exchange))

    app.run_polling()

if __name__ == "__main__":
    main()
