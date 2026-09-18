#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ربات قرآن کریم - ترجمه مکارم شیرازی
دقیقاً مطابق درخواست کاربر
"""

import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)
from telegram.constants import ParseMode
import asyncio

# ==================== تنظیمات ====================
BOT_TOKEN = "8857942493:AAFM5iJ0Ua3sCKfLLR1m_X0WJZ2Fj_pogv8"

ARABIC_EDITION = "quran-uthmani"
PERSIAN_EDITION = "fa.makarem"  # دقیقاً ترجمه مکارم شیرازی (همان PDF)

# ==================== لیست کامل سوره‌ها ====================
SURAHS = [
    (1, "الفاتحه", 7), (2, "البقره", 286), (3, "آل عمران", 200), (4, "النساء", 176),
    (5, "المائده", 120), (6, "الانعام", 165), (7, "الاعراف", 206), (8, "الانفال", 75),
    (9, "التوبه", 129), (10, "یونس", 109), (11, "هود", 123), (12, "یوسف", 111),
    (13, "الرعد", 43), (14, "ابراهیم", 52), (15, "الحجر", 99), (16, "النحل", 128),
    (17, "الاسراء", 111), (18, "الکهف", 110), (19, "مریم", 98), (20, "طه", 135),
    (21, "الانبیاء", 112), (22, "الحج", 78), (23, "المؤمنون", 118), (24, "النور", 64),
    (25, "الفرقان", 77), (26, "الشعراء", 227), (27, "النمل", 93), (28, "القصص", 88),
    (29, "العنکبوت", 69), (30, "الروم", 60), (31, "لقمان", 34), (32, "السجده", 30),
    (33, "الاحزاب", 73), (34, "سبأ", 54), (35, "فاطر", 45), (36, "یس", 83),
    (37, "الصافات", 182), (38, "ص", 88), (39, "الزمر", 75), (40, "غافر", 85),
    (41, "فصلت", 54), (42, "الشوری", 53), (43, "الزخرف", 89), (44, "الدخان", 59),
    (45, "الجاثیه", 37), (46, "الاحقاف", 35), (47, "محمد", 38), (48, "الفتح", 29),
    (49, "الحجرات", 18), (50, "ق", 45), (51, "الذاریات", 60), (52, "الطور", 49),
    (53, "النجم", 62), (54, "القمر", 55), (55, "الرحمن", 78), (56, "الواقعه", 96),
    (57, "الحدید", 29), (58, "المجادله", 22), (59, "الحشر", 24), (60, "الممتحنه", 13),
    (61, "الصف", 14), (62, "الجمعة", 11), (63, "المنافقون", 11), (64, "التغابن", 18),
    (65, "الطلاق", 12), (66, "التحریم", 12), (67, "الملک", 30), (68, "القلم", 52),
    (69, "الحاقه", 52), (70, "المعارج", 44), (71, "نوح", 28), (72, "الجن", 28),
    (73, "المزمل", 20), (74, "المدثر", 56), (75, "القیامه", 40), (76, "الانسان", 31),
    (77, "المرسلات", 50), (78, "النبأ", 40), (79, "النازعات", 46), (80, "عبس", 42),
    (81, "التکویر", 29), (82, "الانفطار", 19), (83, "المطففین", 36), (84, "الانشقاق", 25),
    (85, "البروج", 22), (86, "الطارق", 17), (87, "الأعلی", 19), (88, "الغاشیه", 26),
    (89, "الفجر", 30), (90, "البلد", 20), (91, "الشمس", 15), (92, "اللیل", 21),
    (93, "الضحی", 11), (94, "الشرح", 8), (95, "التین", 8), (96, "العلق", 19),
    (97, "القدر", 5), (98, "البینه", 8), (99, "الزلزله", 8), (100, "العادیات", 11),
    (101, "القارعه", 11), (102, "التکاثر", 8), (103, "العصر", 3), (104, "الهمزه", 9),
    (105, "الفیل", 5), (106, "قریش", 4), (107, "الماعون", 7), (108, "الکوثر", 3),
    (109, "الکافرون", 6), (110, "النصر", 3), (111, "المسد", 5), (112, "الاخلاص", 4),
    (113, "الفلق", 5), (114, "الناس", 6)
]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== توابع دریافت داده ====================
def get_ayah(surah: int, ayah: int, edition: str) -> str:
    url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/{edition}"
    try:
        r = requests.get(url, timeout=12)
        data = r.json()
        if data.get("code") == 200:
            return data["data"]["text"].strip()
        return "⚠️ خطا در دریافت آیه"
    except Exception as e:
        logger.error(f"get_ayah error: {e}")
        return "⚠️ خطا در ارتباط با سرور"

def get_full_surah(surah: int, edition: str) -> list:
    url = f"https://api.alquran.cloud/v1/surah/{surah}/{edition}"
    try:
        r = requests.get(url, timeout=20)
        data = r.json()
        if data.get("code") == 200:
            return data["data"]["ayahs"]
        return []
    except Exception as e:
        logger.error(f"get_full_surah error: {e}")
        return []

def get_tafsir(surah: int, ayah: int) -> str:
    """تفسیر ابن کثیر (نسخه انگلیسی - قابل تعویض با نسخه فارسی اگر موجود باشد)"""
    url = f"https://cdn.jsdelivr.net/gh/spa5k/tafsir_api@main/tafsir/en-tafsir-ibn-kathir/{surah}/{ayah}.json"
    try:
        r = requests.get(url, timeout=12)
        if r.status_code == 200:
            data = r.json()
            text = data.get("text", "")
            if text:
                return text[:3800]
        return "تفسیر برای این آیه در حال حاضر در دسترس نیست."
    except:
        return "تفسیر در دسترس نیست."

# ==================== کیبوردها ====================
def surah_list_kb(page: int = 0):
    per_page = 20
    start = page * per_page
    end = min(start + per_page, 114)
    buttons = []
    for num, name, count in SURAHS[start:end]:
        buttons.append([
            InlineKeyboardButton(
                f"{num}. {name} ({count} آیه)",
                callback_data=f"s_{num}"
            )
        ])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ قبلی", callback_data=f"p_{page-1}"))
    if end < 114:
        nav.append(InlineKeyboardButton("بعدی ▶️", callback_data=f"p_{page+1}"))
    if nav:
        buttons.append(nav)
    return InlineKeyboardMarkup(buttons)

def surah_menu_kb(surah: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 متن عربی کامل", callback_data=f"ar_{surah}")],
        [InlineKeyboardButton("🇮🇷 ترجمه فارسی کامل (مکارم)", callback_data=f"fa_{surah}")],
        [InlineKeyboardButton("📜 عربی + ترجمه با هم", callback_data=f"full_{surah}")],
        [InlineKeyboardButton("🔢 انتخاب آیه خاص", callback_data=f"sel_{surah}")],
        [InlineKeyboardButton("📚 تفسیر", callback_data=f"tfs_{surah}")],
        [InlineKeyboardButton("🔙 بازگشت به لیست سوره‌ها", callback_data="p_0")]
    ])

def ayah_nav_kb(surah: int, ayah: int, total: int):
    buttons = []
    row = []
    if ayah > 1:
        row.append(InlineKeyboardButton("◀️ قبلی", callback_data=f"a_{surah}_{ayah-1}"))
    if ayah < total:
        row.append(InlineKeyboardButton("بعدی ▶️", callback_data=f"a_{surah}_{ayah+1}"))
    if row:
        buttons.append(row)
    buttons.append([
        InlineKeyboardButton("📚 تفسیر این آیه", callback_data=f"t_{surah}_{ayah}"),
        InlineKeyboardButton("🔙 منوی سوره", callback_data=f"s_{surah}")
    ])
    return InlineKeyboardMarkup(buttons)

def ayah_select_kb(surah: int, start: int = 1):
    total = next(s[2] for s in SURAHS if s[0] == surah)
    buttons = []
    row = []
    end = min(start + 29, total)
    for i in range(start, end + 1):
        row.append(InlineKeyboardButton(str(i), callback_data=f"a_{surah}_{i}"))
        if len(row) == 5:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    nav = []
    if start > 1:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"selmore_{surah}_{max(1, start-30)}"))
    if end < total:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"selmore_{surah}_{end+1}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton("🔙 بازگشت", callback_data=f"s_{surah}")])
    return InlineKeyboardMarkup(buttons)

# ==================== ارسال متن بلند ====================
async def send_long_text(query, text: str, reply_markup=None, max_len=3800):
    """پیام‌های خیلی بلند را به چند پیام تقسیم می‌کند"""
    if len(text) <= max_len:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        return

    parts = []
    while text:
        if len(text) <= max_len:
            parts.append(text)
            break
        split_at = text.rfind("\n\n", 0, max_len)
        if split_at == -1:
            split_at = max_len
        parts.append(text[:split_at])
        text = text[split_at:].lstrip()

    # پیام اول با کیبورد
    await query.edit_message_text(parts[0], reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    # بقیه پیام‌ها
    for part in parts[1:]:
        await query.message.reply_text(part, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(0.3)

# ==================== هندلرها ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "﷽\n\n"
        "سلام علیکم\n"
        "به ربات **قرآن کریم** با ترجمه آیت‌الله مکارم شیرازی خوش آمدید.\n\n"
        "تمام ۱۱۴ سوره آماده است.\n"
        "سوره مورد نظر خود را انتخاب کنید:"
    )
    await update.message.reply_text(text, reply_markup=surah_list_kb(0), parse_mode=ParseMode.MARKDOWN)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ---------- صفحه‌بندی لیست سوره‌ها ----------
    if data.startswith("p_"):
        page = int(data.split("_")[1])
        await query.edit_message_text(
            "سوره مورد نظر را انتخاب کنید:",
            reply_markup=surah_list_kb(page)
        )
        return

    # ---------- انتخاب سوره ----------
    if data.startswith("s_"):
        surah = int(data.split("_")[1])
        name = next(s[1] for s in SURAHS if s[0] == surah)
        count = next(s[2] for s in SURAHS if s[0] == surah)
        await query.edit_message_text(
            f"📖 سوره **{name}**\nتعداد آیات: {count}\n\nچه کاری می‌خواهید انجام دهید؟",
            reply_markup=surah_menu_kb(surah),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # ---------- متن عربی کامل ----------
    if data.startswith("ar_"):
        surah = int(data.split("_")[1])
        ayahs = get_full_surah(surah, ARABIC_EDITION)
        if not ayahs:
            await query.edit_message_text("⚠️ خطا در دریافت داده. لطفاً دوباره تلاش کنید.")
            return
        text = f"📖 **متن عربی سوره {surah}**\n\n"
        for a in ayahs:
            text += f"**{a['numberInSurah']}.** {a['text']}\n\n"
        await send_long_text(query, text, reply_markup=surah_menu_kb(surah))
        return

    # ---------- ترجمه فارسی کامل ----------
    if data.startswith("fa_"):
        surah = int(data.split("_")[1])
        ayahs = get_full_surah(surah, PERSIAN_EDITION)
        if not ayahs:
            await query.edit_message_text("⚠️ خطا در دریافت داده.")
            return
        text = f"🇮🇷 **ترجمه فارسی (مکارم شیرازی) - سوره {surah}**\n\n"
        for a in ayahs:
            text += f"**{a['numberInSurah']}.** {a['text']}\n\n"
        await send_long_text(query, text, reply_markup=surah_menu_kb(surah))
        return

    # ---------- عربی + ترجمه ----------
    if data.startswith("full_"):
        surah = int(data.split("_")[1])
        ar = get_full_surah(surah, ARABIC_EDITION)
        fa = get_full_surah(surah, PERSIAN_EDITION)
        if not ar or not fa:
            await query.edit_message_text("⚠️ خطا در دریافت داده.")
            return
        text = f"📜 **سوره {surah} - عربی + ترجمه**\n\n"
        for a, f in zip(ar, fa):
            text += f"**{a['numberInSurah']}**\n{a['text']}\n\n_{f['text']}_\n\n────────────\n\n"
        await send_long_text(query, text, reply_markup=surah_menu_kb(surah))
        return

    # ---------- انتخاب آیه ----------
    if data.startswith("sel_"):
        surah = int(data.split("_")[1])
        await query.edit_message_text(
            f"آیه مورد نظر از سوره {surah} را انتخاب کنید:",
            reply_markup=ayah_select_kb(surah, 1)
        )
        return

    if data.startswith("selmore_"):
        parts = data.split("_")
        surah = int(parts[1])
        start = int(parts[2])
        await query.edit_message_text(
            f"آیات از شماره {start}:",
            reply_markup=ayah_select_kb(surah, start)
        )
        return

    # ---------- نمایش یک آیه ----------
    if data.startswith("a_"):
        parts = data.split("_")
        surah = int(parts[1])
        ayah = int(parts[2])
        total = next(s[2] for s in SURAHS if s[0] == surah)

        ar = get_ayah(surah, ayah, ARABIC_EDITION)
        fa = get_ayah(surah, ayah, PERSIAN_EDITION)

        text = (
            f"📖 **سوره {surah} — آیه {ayah}**\n\n"
            f"**عربی:**\n{ar}\n\n"
            f"**ترجمه (مکارم):**\n{fa}"
        )
        await query.edit_message_text(
            text,
            reply_markup=ayah_nav_kb(surah, ayah, total),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # ---------- تفسیر ----------
    if data.startswith("tfs_"):
        surah = int(data.split("_")[1])
        # تفسیر آیه اول به عنوان نمونه
        tafsir = get_tafsir(surah, 1)
        text = f"📚 **تفسیر سوره {surah}** (نمونه آیه ۱):\n\n{tafsir}"
        await send_long_text(query, text, reply_markup=surah_menu_kb(surah))
        return

    if data.startswith("t_"):
        parts = data.split("_")
        surah = int(parts[1])
        ayah = int(parts[2])
        total = next(s[2] for s in SURAHS if s[0] == surah)
        tafsir = get_tafsir(surah, ayah)
        text = f"📚 **تفسیر سوره {surah} آیه {ayah}:**\n\n{tafsir}"
        await send_long_text(query, text, reply_markup=ayah_nav_kb(surah, ayah, total))
        return

# ==================== اجرا ====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("✅ ربات قرآن کریم آماده است و در حال اجرا...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()