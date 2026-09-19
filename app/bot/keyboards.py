from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def keyboard(rows: list[list[tuple[str, str]]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, callback_data=data) for text, data in row] for row in rows])


MAIN_MENU = keyboard([
    [("🎯 Начать собеседование", "menu:interview")],
    [("📄 Подготовка по вакансии", "menu:vacancy"), ("🧠 Частые вопросы", "menu:faq")],
    [("💬 HR-собеседование", "quick:hr"), ("🛠 Профессиональное", "quick:professional")],
    [("🔥 Стресс-собеседование", "quick:stress")],
    [("📊 Мои результаты", "menu:results"), ("📈 Мой прогресс", "menu:progress")],
    [("📚 Работа над ошибками", "menu:mistakes"), ("⚙️ Настройки", "menu:settings")],
    [("💎 Премиум", "menu:premium")],
])
LEVELS = keyboard([[('Стажёр', 'level:intern'), ('Junior', 'level:junior')], [('Middle', 'level:middle'), ('Senior', 'level:senior')], [('Lead', 'level:lead')]])
VACANCY = keyboard([[('📄 Вставить вакансию', 'vacancy:paste'), ('⏭ Пропустить', 'vacancy:skip')]])
RESUME = keyboard([[('✏️ Вставить текст', 'resume:paste'), ('📎 Загрузить файл', 'resume:file')], [('⏭ Пропустить', 'resume:skip')]])
INTERVIEW_TYPES = keyboard([[('🎯 Полное', 'type:full'), ('📝 Тренировка', 'type:training')], [('📄 По вакансии', 'type:vacancy'), ('💬 HR', 'type:hr')], [('🛠 Профессиональное', 'type:professional'), ('🔥 Стресс', 'type:stress')], [('🧩 Кейсы', 'type:case'), ('⭐ Поведенческое', 'type:behavioral')], [('❌ Отмена', 'cancel')]])
DIFFICULTIES = keyboard([[('🟢 Лёгкая', 'difficulty:easy'), ('🟡 Средняя', 'difficulty:medium')], [('🔴 Сложная', 'difficulty:hard'), ('🔥 Экспертная', 'difficulty:expert')]])
DURATIONS = keyboard([[('⚡ 5', 'duration:5'), ('🎯 10', 'duration:10')], [('🔥 20', 'duration:20'), ('🏆 30', 'duration:30')]])
LANGUAGES = keyboard([[('🇷🇺 Русский', 'language:ru'), ('🇬🇧 Английский', 'language:en')]])

