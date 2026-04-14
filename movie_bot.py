"""
🎬 Heisenberg Bot v3
Фильмы + Сериалы. Комбинированный поиск. 4 языка.

Установка:
    pip install python-telegram-bot requests

Настройка:
    TELEGRAM_TOKEN и TMDB_API_KEY — через переменные окружения (.env или Railway)
"""

import logging
import os
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ─── НАСТРОЙКИ ────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TMDB_API_KEY   = os.environ["TMDB_API_KEY"]
TMDB_BASE      = "https://api.themoviedb.org/3"
TMDB_IMG       = "https://image.tmdb.org/t/p/w500"
DEFAULT_LANG   = "ru"
DEFAULT_MODE   = "movie"   # "movie" | "tv"
# ──────────────────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
#  ПЕРЕВОДЫ
# ═══════════════════════════════════════════════════════════════════════════════

STRINGS: dict[str, dict[str, str]] = {
    "ru": {
        "welcome":          "👋 Привет! Я Heisenberg — помогу найти фильм или сериал.\n\nВыбери способ поиска:",
        "choose_search":    "Выбери способ поиска:",
        "choose_type":      "Что ищем?",
        "choose_genre":     "Выбери жанр:",
        "choose_mood":      "Какое настроение?",
        "choose_decade":    "Выбери эпоху:",
        "choose_keyword":   "Выбери тему:",
        "choose_country":   "Выбери страну:",
        "choose_language":  "Выбери язык интерфейса:",
        "lang_set":         "✅ Язык изменён!",
        "type_set_movie":   "🎬 Ищем фильмы",
        "type_set_tv":      "📺 Ищем сериалы",
        "similar_prompt":   "Напиши название, и я найду похожее:\n_(например: Во все тяжкие, Начало, Игра престолов)_",
        "searching":        "🔍 Ищу «{title}»…",
        "not_found_title":  "Не найдено. Попробуй другое название.",
        "found_similar":    "Нашёл «{title}». Вот похожее:",
        "no_similar":       "Похожее не найдено.",
        "found":            "🎬 Вот что нашёл:",
        "found_country":    "🌍 Лучшее из: {country}",
        "no_results":       "Ничего не найдено. Попробуй другой фильтр.",
        "no_more":          "Больше результатов не найдено.",
        "find_more":        "Найти ещё?",
        "show_more":        "Показать ещё или начать заново?",
        "random_searching": "🎲 Ищу случайный вариант…",
        "random_again":     "Хочешь ещё один?",
        "random_fail":      "Не удалось найти. Попробуй ещё раз.",
        "combo_title":      "🔧 *Комбинированный поиск*\n\nФильтры:\n{filters}\n\nДобавь нужные и нажми «Найти»",
        "combo_no_filter":  "_(не выбраны)_",
        "combo_ready":      "🔎 Ищу по фильтрам…",
        "combo_no_results": "По таким фильтрам ничего не найдено.",
        "btn_random":       "🎲 Случайный",
        "btn_genre":        "🎭 По жанру",
        "btn_mood":         "🎨 По настроению",
        "btn_decade":       "📅 По десятилетию",
        "btn_keyword":      "🔑 По теме",
        "btn_country":      "🌍 По стране",
        "btn_similar":      "🔄 Похожее",
        "btn_combo":        "⚙️ Комбинированный",
        "btn_type":         "🎬 Фильмы / 📺 Сериалы",
        "btn_language":     "🌐 Язык",
        "btn_back":         "◀️ Назад",
        "btn_home":         "◀️ В начало",
        "btn_more":         "🔁 Ещё",
        "btn_random_more":  "🎲 Ещё случайный",
        "btn_search":       "🔍 Найти",
        "btn_clear":        "🗑 Очистить",
        "btn_add_genre":    "+ Жанр",
        "btn_add_mood":     "+ Настроение",
        "btn_add_decade":   "+ Эпоха",
        "btn_add_country":  "+ Страна",
        "btn_add_keyword":  "+ Тема",
        "btn_movies":       "🎬 Фильмы",
        "btn_tv":           "📺 Сериалы",
        "lbl_genre":        "🎭 Жанр",
        "lbl_mood":         "🎨 Настроение",
        "lbl_decade":       "📅 Эпоха",
        "lbl_country":      "🌍 Страна",
        "lbl_keyword":      "🔑 Тема",
        "lbl_type":         "Тип",
        "lbl_type_movie":   "🎬 Фильмы",
        "lbl_type_tv":      "📺 Сериалы",
        "no_desc":          "Описание недоступно.",
        "seasons":          "сезонов",
    },
    "en": {
        "welcome":          "👋 Hi! I'm Heisenberg — I'll help you find a movie or TV show.\n\nChoose a search method:",
        "choose_search":    "Choose a search method:",
        "choose_type":      "What are we looking for?",
        "choose_genre":     "Choose a genre:",
        "choose_mood":      "What mood are you in?",
        "choose_decade":    "Choose a decade:",
        "choose_keyword":   "Choose a topic:",
        "choose_country":   "Choose a country:",
        "choose_language":  "Choose interface language:",
        "lang_set":         "✅ Language changed!",
        "type_set_movie":   "🎬 Searching movies",
        "type_set_tv":      "📺 Searching TV shows",
        "similar_prompt":   "Write a title and I'll find similar ones:\n_(e.g.: Breaking Bad, Inception, Game of Thrones)_",
        "searching":        "🔍 Searching «{title}»…",
        "not_found_title":  "Not found. Try a different title.",
        "found_similar":    "Found «{title}». Here are similar ones:",
        "no_similar":       "No similar results found.",
        "found":            "🎬 Here's what I found:",
        "found_country":    "🌍 Top from: {country}",
        "no_results":       "Nothing found. Try a different filter.",
        "no_more":          "No more results.",
        "find_more":        "Find more?",
        "show_more":        "Show more or start over?",
        "random_searching": "🎲 Finding a random pick…",
        "random_again":     "Want another one?",
        "random_fail":      "Couldn't find anything. Try again.",
        "combo_title":      "🔧 *Combined Search*\n\nFilters:\n{filters}\n\nAdd filters and press «Search»",
        "combo_no_filter":  "_(none selected)_",
        "combo_ready":      "🔎 Searching with filters…",
        "combo_no_results": "No results for these filters.",
        "btn_random":       "🎲 Random",
        "btn_genre":        "🎭 By Genre",
        "btn_mood":         "🎨 By Mood",
        "btn_decade":       "📅 By Decade",
        "btn_keyword":      "🔑 By Topic",
        "btn_country":      "🌍 By Country",
        "btn_similar":      "🔄 Similar",
        "btn_combo":        "⚙️ Combined",
        "btn_type":         "🎬 Movies / 📺 TV Shows",
        "btn_language":     "🌐 Language",
        "btn_back":         "◀️ Back",
        "btn_home":         "◀️ Home",
        "btn_more":         "🔁 More",
        "btn_random_more":  "🎲 Another Random",
        "btn_search":       "🔍 Search",
        "btn_clear":        "🗑 Clear",
        "btn_add_genre":    "+ Genre",
        "btn_add_mood":     "+ Mood",
        "btn_add_decade":   "+ Decade",
        "btn_add_country":  "+ Country",
        "btn_add_keyword":  "+ Topic",
        "btn_movies":       "🎬 Movies",
        "btn_tv":           "📺 TV Shows",
        "lbl_genre":        "🎭 Genre",
        "lbl_mood":         "🎨 Mood",
        "lbl_decade":       "📅 Decade",
        "lbl_country":      "🌍 Country",
        "lbl_keyword":      "🔑 Topic",
        "lbl_type":         "Type",
        "lbl_type_movie":   "🎬 Movies",
        "lbl_type_tv":      "📺 TV Shows",
        "no_desc":          "No description available.",
        "seasons":          "seasons",
    },
    "es": {
        "welcome":          "👋 ¡Hola! Soy Heisenberg — te ayudaré a encontrar una película o serie.\n\nElige un método de búsqueda:",
        "choose_search":    "Elige un método de búsqueda:",
        "choose_type":      "¿Qué buscamos?",
        "choose_genre":     "Elige un género:",
        "choose_mood":      "¿Qué humor tienes?",
        "choose_decade":    "Elige una época:",
        "choose_keyword":   "Elige un tema:",
        "choose_country":   "Elige un país:",
        "choose_language":  "Elige el idioma:",
        "lang_set":         "✅ ¡Idioma cambiado!",
        "type_set_movie":   "🎬 Buscando películas",
        "type_set_tv":      "📺 Buscando series",
        "similar_prompt":   "Escribe un título y encontraré similares:\n_(p.ej.: Breaking Bad, Origen, Juego de Tronos)_",
        "searching":        "🔍 Buscando «{title}»…",
        "not_found_title":  "No encontrado. Prueba otro título.",
        "found_similar":    "Encontré «{title}». Aquí hay similares:",
        "no_similar":       "No se encontraron similares.",
        "found":            "🎬 Esto es lo que encontré:",
        "found_country":    "🌍 Lo mejor de: {country}",
        "no_results":       "Sin resultados. Prueba otro filtro.",
        "no_more":          "No hay más resultados.",
        "find_more":        "¿Buscar más?",
        "show_more":        "¿Mostrar más o empezar de nuevo?",
        "random_searching": "🎲 Buscando algo al azar…",
        "random_again":     "¿Quieres otro?",
        "random_fail":      "No se pudo encontrar. Inténtalo de nuevo.",
        "combo_title":      "🔧 *Búsqueda Combinada*\n\nFiltros:\n{filters}\n\nAgrega filtros y pulsa «Buscar»",
        "combo_no_filter":  "_(ninguno)_",
        "combo_ready":      "🔎 Buscando con filtros…",
        "combo_no_results": "Sin resultados para estos filtros.",
        "btn_random":       "🎲 Aleatorio",
        "btn_genre":        "🎭 Por Género",
        "btn_mood":         "🎨 Por Ánimo",
        "btn_decade":       "📅 Por Época",
        "btn_keyword":      "🔑 Por Tema",
        "btn_country":      "🌍 Por País",
        "btn_similar":      "🔄 Similares",
        "btn_combo":        "⚙️ Combinado",
        "btn_type":         "🎬 Películas / 📺 Series",
        "btn_language":     "🌐 Idioma",
        "btn_back":         "◀️ Volver",
        "btn_home":         "◀️ Inicio",
        "btn_more":         "🔁 Más",
        "btn_random_more":  "🎲 Otro Aleatorio",
        "btn_search":       "🔍 Buscar",
        "btn_clear":        "🗑 Limpiar",
        "btn_add_genre":    "+ Género",
        "btn_add_mood":     "+ Ánimo",
        "btn_add_decade":   "+ Época",
        "btn_add_country":  "+ País",
        "btn_add_keyword":  "+ Tema",
        "btn_movies":       "🎬 Películas",
        "btn_tv":           "📺 Series",
        "lbl_genre":        "🎭 Género",
        "lbl_mood":         "🎨 Ánimo",
        "lbl_decade":       "📅 Época",
        "lbl_country":      "🌍 País",
        "lbl_keyword":      "🔑 Tema",
        "lbl_type":         "Tipo",
        "lbl_type_movie":   "🎬 Películas",
        "lbl_type_tv":      "📺 Series",
        "no_desc":          "Sin descripción.",
        "seasons":          "temporadas",
    },
    "zh": {
        "welcome":          "👋 你好！我是 Heisenberg — 帮你找电影或剧集。\n\n请选择搜索方式：",
        "choose_search":    "请选择搜索方式：",
        "choose_type":      "搜索什么？",
        "choose_genre":     "选择类型：",
        "choose_mood":      "你现在的心情？",
        "choose_decade":    "选择年代：",
        "choose_keyword":   "选择主题：",
        "choose_country":   "选择国家：",
        "choose_language":  "选择界面语言：",
        "lang_set":         "✅ 语言已更改！",
        "type_set_movie":   "🎬 搜索电影",
        "type_set_tv":      "📺 搜索剧集",
        "similar_prompt":   "请输入标题，我来找类似的：\n_(例如：绝命毒师，盗梦空间，权力的游戏)_",
        "searching":        "🔍 正在搜索《{title}》…",
        "not_found_title":  "未找到，请换个名称试试。",
        "found_similar":    "找到了《{title}》，以下是类似作品：",
        "no_similar":       "未找到类似作品。",
        "found":            "🎬 搜索结果：",
        "found_country":    "🌍 来自 {country} 的优秀作品",
        "no_results":       "未找到结果，请尝试其他条件。",
        "no_more":          "没有更多结果了。",
        "find_more":        "再找一些？",
        "show_more":        "显示更多或重新开始？",
        "random_searching": "🎲 正在随机寻找…",
        "random_again":     "还想再来一个？",
        "random_fail":      "无法找到，请再试一次。",
        "combo_title":      "🔧 *组合搜索*\n\n筛选条件：\n{filters}\n\n添加条件后点击「搜索」",
        "combo_no_filter":  "_(未选择)_",
        "combo_ready":      "🔎 按条件搜索中…",
        "combo_no_results": "没有符合条件的结果。",
        "btn_random":       "🎲 随机",
        "btn_genre":        "🎭 按类型",
        "btn_mood":         "🎨 按心情",
        "btn_decade":       "📅 按年代",
        "btn_keyword":      "🔑 按主题",
        "btn_country":      "🌍 按国家",
        "btn_similar":      "🔄 类似作品",
        "btn_combo":        "⚙️ 组合搜索",
        "btn_type":         "🎬 电影 / 📺 剧集",
        "btn_language":     "🌐 语言",
        "btn_back":         "◀️ 返回",
        "btn_home":         "◀️ 主页",
        "btn_more":         "🔁 更多",
        "btn_random_more":  "🎲 再来一个",
        "btn_search":       "🔍 搜索",
        "btn_clear":        "🗑 清除",
        "btn_add_genre":    "+ 类型",
        "btn_add_mood":     "+ 心情",
        "btn_add_decade":   "+ 年代",
        "btn_add_country":  "+ 国家",
        "btn_add_keyword":  "+ 主题",
        "btn_movies":       "🎬 电影",
        "btn_tv":           "📺 剧集",
        "lbl_genre":        "🎭 类型",
        "lbl_mood":         "🎨 心情",
        "lbl_decade":       "📅 年代",
        "lbl_country":      "🌍 国家",
        "lbl_keyword":      "🔑 主题",
        "lbl_type":         "类别",
        "lbl_type_movie":   "🎬 电影",
        "lbl_type_tv":      "📺 剧集",
        "no_desc":          "暂无简介。",
        "seasons":          "季",
    },
}

LANG_NAMES = {"ru": "🇷🇺 Русский", "en": "🇬🇧 English", "es": "🇪🇸 Español", "zh": "🇨🇳 中文"}
TMDB_LANG  = {"ru": "ru-RU", "en": "en-US", "es": "es-ES", "zh": "zh-CN"}


def t(ctx: ContextTypes.DEFAULT_TYPE, key: str) -> str:
    lang = ctx.user_data.get("lang", DEFAULT_LANG)
    return STRINGS.get(lang, STRINGS["ru"]).get(key, key)


def is_tv(ctx: ContextTypes.DEFAULT_TYPE) -> bool:
    return ctx.user_data.get("content_type", DEFAULT_MODE) == "tv"


# ═══════════════════════════════════════════════════════════════════════════════
#  СПРАВОЧНИКИ
# ═══════════════════════════════════════════════════════════════════════════════

# Жанры фильмов и сериалов немного отличаются в TMDb
MOVIE_GENRES = {
    "28": {"ru":"🥊 Боевик","en":"🥊 Action","es":"🥊 Acción","zh":"🥊 动作"},
    "35": {"ru":"😂 Комедия","en":"😂 Comedy","es":"😂 Comedia","zh":"😂 喜剧"},
    "18": {"ru":"🎭 Драма","en":"🎭 Drama","es":"🎭 Drama","zh":"🎭 剧情"},
    "27": {"ru":"👻 Ужасы","en":"👻 Horror","es":"👻 Terror","zh":"👻 恐怖"},
    "10749":{"ru":"💕 Мелодрама","en":"💕 Romance","es":"💕 Romance","zh":"💕 爱情"},
    "878": {"ru":"🚀 Фантастика","en":"🚀 Sci-Fi","es":"🚀 Ciencia F.","zh":"🚀 科幻"},
    "53":  {"ru":"😰 Триллер","en":"😰 Thriller","es":"😰 Suspenso","zh":"😰 惊悚"},
    "16":  {"ru":"🐣 Мультфильм","en":"🐣 Animation","es":"🐣 Animación","zh":"🐣 动画"},
    "12":  {"ru":"🗺️ Приключения","en":"🗺️ Adventure","es":"🗺️ Aventura","zh":"🗺️ 冒险"},
    "80":  {"ru":"🔫 Криминал","en":"🔫 Crime","es":"🔫 Crimen","zh":"🔫 犯罪"},
    "14":  {"ru":"🧙 Фэнтези","en":"🧙 Fantasy","es":"🧙 Fantasía","zh":"🧙 奇幻"},
    "36":  {"ru":"📜 История","en":"📜 History","es":"📜 Historia","zh":"📜 历史"},
}

TV_GENRES = {
    "10759":{"ru":"🥊 Боевик/Приключения","en":"🥊 Action & Adventure","es":"🥊 Acción y Aventura","zh":"🥊 动作冒险"},
    "35":   {"ru":"😂 Комедия","en":"😂 Comedy","es":"😂 Comedia","zh":"😂 喜剧"},
    "18":   {"ru":"🎭 Драма","en":"🎭 Drama","es":"🎭 Drama","zh":"🎭 剧情"},
    "10765":{"ru":"🚀 Фантастика/Фэнтези","en":"🚀 Sci-Fi & Fantasy","es":"🚀 Ciencia F. y Fantasía","zh":"🚀 科幻奇幻"},
    "9648": {"ru":"🔍 Детектив","en":"🔍 Mystery","es":"🔍 Misterio","zh":"🔍 悬疑"},
    "80":   {"ru":"🔫 Криминал","en":"🔫 Crime","es":"🔫 Crimen","zh":"🔫 犯罪"},
    "10768":{"ru":"⚔️ Война/Политика","en":"⚔️ War & Politics","es":"⚔️ Guerra y Política","zh":"⚔️ 战争政治"},
    "16":   {"ru":"🐣 Анимация","en":"🐣 Animation","es":"🐣 Animación","zh":"🐣 动画"},
    "10751":{"ru":"👨‍👩‍👧 Семейный","en":"👨‍👩‍👧 Family","es":"👨‍👩‍👧 Familia","zh":"👨‍👩‍👧 家庭"},
    "10762":{"ru":"🧒 Детский","en":"🧒 Kids","es":"🧒 Niños","zh":"🧒 儿童"},
    "10763":{"ru":"📰 Новости","en":"📰 News","es":"📰 Noticias","zh":"📰 新闻"},
    "10764":{"ru":"🎮 Реалити","en":"🎮 Reality","es":"🎮 Reality","zh":"🎮 真人秀"},
}

MOODS = {
    "fun":      {"ru":"😄 Весёлое","en":"😄 Fun","es":"😄 Divertido","zh":"😄 欢乐",
                 "movie_genres":"35,16","tv_genres":"35,16"},
    "tense":    {"ru":"😰 Напряжённое","en":"😰 Tense","es":"😰 Tenso","zh":"😰 紧张",
                 "movie_genres":"53,27,80","tv_genres":"9648,80,10759"},
    "romantic": {"ru":"💕 Романтичное","en":"💕 Romantic","es":"💕 Romántico","zh":"💕 浪漫",
                 "movie_genres":"10749,35","tv_genres":"35,18"},
    "deep":     {"ru":"🤔 Глубокое","en":"🤔 Thoughtful","es":"🤔 Reflexivo","zh":"🤔 深刻",
                 "movie_genres":"18,36","tv_genres":"18,10768"},
    "epic":     {"ru":"🚀 Захватывающее","en":"🚀 Epic","es":"🚀 Épico","zh":"🚀 史诗",
                 "movie_genres":"28,12,878","tv_genres":"10759,10765,10768"},
    "magical":  {"ru":"✨ Сказочное","en":"✨ Magical","es":"✨ Mágico","zh":"✨ 魔幻",
                 "movie_genres":"14,16,12","tv_genres":"10765,16,10751"},
}

DECADES = {
    "2020":{"ru":"2020-е","en":"2020s","es":"2020s","zh":"2020年代","from":"2020-01-01","to":"2029-12-31"},
    "2010":{"ru":"2010-е","en":"2010s","es":"2010s","zh":"2010年代","from":"2010-01-01","to":"2019-12-31"},
    "2000":{"ru":"2000-е","en":"2000s","es":"2000s","zh":"2000年代","from":"2000-01-01","to":"2009-12-31"},
    "1990":{"ru":"1990-е","en":"1990s","es":"1990s","zh":"1990年代","from":"1990-01-01","to":"1999-12-31"},
    "old": {"ru":"Классика","en":"Classic","es":"Clásico","zh":"经典","from":"1900-01-01","to":"1989-12-31"},
}

KEYWORDS = {
    "spy":       {"ru":"🕵️ Шпионы","en":"🕵️ Spies","es":"🕵️ Espías","zh":"🕵️ 间谍","query":"spy"},
    "space":     {"ru":"🌌 Космос","en":"🌌 Space","es":"🌌 Espacio","zh":"🌌 太空","query":"space"},
    "school":    {"ru":"🏫 Школа","en":"🏫 School","es":"🏫 Escuela","zh":"🏫 学校","query":"school"},
    "war":       {"ru":"⚔️ Война","en":"⚔️ War","es":"⚔️ Guerra","zh":"⚔️ 战争","query":"war"},
    "mafia":     {"ru":"🤵 Мафия","en":"🤵 Mafia","es":"🤵 Mafia","zh":"🤵 黑帮","query":"mafia"},
    "robot":     {"ru":"🤖 Роботы","en":"🤖 Robots","es":"🤖 Robots","zh":"🤖 机器人","query":"robot"},
    "travel":    {"ru":"✈️ Путешествия","en":"✈️ Road Trip","es":"✈️ Viaje","zh":"✈️ 旅行","query":"road trip"},
    "superhero": {"ru":"🦸 Супергерои","en":"🦸 Superheroes","es":"🦸 Superhéroes","zh":"🦸 超级英雄","query":"superhero"},
    "cooking":   {"ru":"🍳 Кулинария","en":"🍳 Cooking","es":"🍳 Cocina","zh":"🍳 烹饪","query":"cooking"},
    "music":     {"ru":"🎵 Музыка","en":"🎵 Music","es":"🎵 Música","zh":"🎵 音乐","query":"musician"},
}

COUNTRIES = {
    "US":{"ru":"🇺🇸 США","en":"🇺🇸 USA","es":"🇺🇸 EE. UU.","zh":"🇺🇸 美国"},
    "GB":{"ru":"🇬🇧 Великобритания","en":"🇬🇧 UK","es":"🇬🇧 Reino Unido","zh":"🇬🇧 英国"},
    "FR":{"ru":"🇫🇷 Франция","en":"🇫🇷 France","es":"🇫🇷 Francia","zh":"🇫🇷 法国"},
    "IT":{"ru":"🇮🇹 Италия","en":"🇮🇹 Italy","es":"🇮🇹 Italia","zh":"🇮🇹 意大利"},
    "DE":{"ru":"🇩🇪 Германия","en":"🇩🇪 Germany","es":"🇩🇪 Alemania","zh":"🇩🇪 德国"},
    "JP":{"ru":"🇯🇵 Япония","en":"🇯🇵 Japan","es":"🇯🇵 Japón","zh":"🇯🇵 日本"},
    "KR":{"ru":"🇰🇷 Южная Корея","en":"🇰🇷 South Korea","es":"🇰🇷 Corea del Sur","zh":"🇰🇷 韩国"},
    "CN":{"ru":"🇨🇳 Китай","en":"🇨🇳 China","es":"🇨🇳 China","zh":"🇨🇳 中国"},
    "IN":{"ru":"🇮🇳 Индия","en":"🇮🇳 India","es":"🇮🇳 India","zh":"🇮🇳 印度"},
    "RU":{"ru":"🇷🇺 Россия","en":"🇷🇺 Russia","es":"🇷🇺 Rusia","zh":"🇷🇺 俄罗斯"},
    "ES":{"ru":"🇪🇸 Испания","en":"🇪🇸 Spain","es":"🇪🇸 España","zh":"🇪🇸 西班牙"},
    "SE":{"ru":"🇸🇪 Швеция","en":"🇸🇪 Sweden","es":"🇸🇪 Suecia","zh":"🇸🇪 瑞典"},
    "MX":{"ru":"🇲🇽 Мексика","en":"🇲🇽 Mexico","es":"🇲🇽 México","zh":"🇲🇽 墨西哥"},
    "IR":{"ru":"🇮🇷 Иран","en":"🇮🇷 Iran","es":"🇮🇷 Irán","zh":"🇮🇷 伊朗"},
}


def label(d: dict, lang: str) -> str:
    return d.get(lang, d.get("en", "?"))


def genres_for(ctx) -> dict:
    return TV_GENRES if is_tv(ctx) else MOVIE_GENRES


# ═══════════════════════════════════════════════════════════════════════════════
#  TMDb ЗАПРОСЫ
# ═══════════════════════════════════════════════════════════════════════════════

def tmdb_get(path: str, params: dict, lang: str = "ru") -> dict:
    params["api_key"]  = TMDB_API_KEY
    params["language"] = TMDB_LANG.get(lang, "ru-RU")
    r = requests.get(f"{TMDB_BASE}{path}", params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def discover(
    content_type: str = "movie",
    lang: str = "ru",
    genre_ids: str = "",
    date_from: str = "",
    date_to: str = "",
    keyword_query: str = "",
    country: str = "",
    page: int = 1,
) -> list[dict]:
    date_field = "primary_release_date" if content_type == "movie" else "first_air_date"
    params: dict = {
        "sort_by":        "vote_average.desc",
        "vote_count.gte": 100,
        "include_adult":  "false",
        "page":           page,
    }
    if genre_ids:
        params["with_genres"] = genre_ids
    if date_from:
        params[f"{date_field}.gte"] = date_from
    if date_to:
        params[f"{date_field}.lte"] = date_to
    if country:
        params["with_origin_country"] = country
    if keyword_query:
        kw = tmdb_get("/search/keyword", {"query": keyword_query}, lang)
        ids = kw.get("results", [])
        if ids:
            params["with_keywords"] = str(ids[0]["id"])
    data = tmdb_get(f"/discover/{content_type}", params, lang)
    return data.get("results", [])[:5]


def random_item(content_type: str = "movie", lang: str = "ru") -> dict | None:
    page = random.randint(1, 20)
    params = {"sort_by": "vote_average.desc", "vote_count.gte": 300,
              "include_adult": "false", "page": page}
    data = tmdb_get(f"/discover/{content_type}", params, lang)
    results = data.get("results", [])
    return random.choice(results) if results else None


def similar_items(item_id: int, content_type: str = "movie", lang: str = "ru") -> list[dict]:
    data = tmdb_get(f"/{content_type}/{item_id}/similar", {}, lang)
    return data.get("results", [])[:5]


def search_items(title: str, content_type: str = "movie", lang: str = "ru") -> list[dict]:
    endpoint = "/search/movie" if content_type == "movie" else "/search/tv"
    data = tmdb_get(endpoint, {"query": title}, lang)
    return data.get("results", [])[:5]


# ═══════════════════════════════════════════════════════════════════════════════
#  ФОРМАТИРОВАНИЕ
# ═══════════════════════════════════════════════════════════════════════════════

def format_item(m: dict, content_type: str = "movie", no_desc: str = "—", seasons_word: str = "seasons") -> tuple[str, str | None]:
    if content_type == "tv":
        title    = m.get("name", "—")
        original = m.get("original_name", "")
        year     = (m.get("first_air_date") or "")[:4]
        seasons  = m.get("number_of_seasons")
        seasons_str = f" · {seasons} {seasons_word}" if seasons else ""
    else:
        title    = m.get("title", "—")
        original = m.get("original_title", "")
        year     = (m.get("release_date") or "")[:4]
        seasons_str = ""

    rating   = m.get("vote_average", 0)
    overview = (m.get("overview") or no_desc)[:200]
    stars    = "⭐" * round(rating / 2)
    poster   = TMDB_IMG + m["poster_path"] if m.get("poster_path") else None
    icon     = "📺" if content_type == "tv" else "🎬"

    text = (
        f"{icon} *{title}*" + (f" ({year})" if year else "") + seasons_str + "\n"
        + (f"_{original}_\n" if original and original != title else "")
        + f"{stars} {rating:.1f}/10\n\n"
        + overview
        + ("…" if len(m.get("overview") or "") > 200 else "")
    )
    return text, poster


# ═══════════════════════════════════════════════════════════════════════════════
#  КЛАВИАТУРЫ
# ═══════════════════════════════════════════════════════════════════════════════

def type_badge(ctx) -> str:
    return "📺" if is_tv(ctx) else "🎬"


def kb_main(ctx) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🎲 {type_badge(ctx)} Случайный" if ctx.user_data.get("lang","ru")=="ru"
                              else t(ctx,"btn_random"), callback_data="random")],
        [InlineKeyboardButton(t(ctx,"btn_genre"),   callback_data="menu_genre"),
         InlineKeyboardButton(t(ctx,"btn_mood"),    callback_data="menu_mood")],
        [InlineKeyboardButton(t(ctx,"btn_decade"),  callback_data="menu_decade"),
         InlineKeyboardButton(t(ctx,"btn_keyword"), callback_data="menu_keyword")],
        [InlineKeyboardButton(t(ctx,"btn_country"), callback_data="menu_country"),
         InlineKeyboardButton(t(ctx,"btn_similar"), callback_data="menu_similar")],
        [InlineKeyboardButton(t(ctx,"btn_combo"),   callback_data="combo_menu")],
        [InlineKeyboardButton(t(ctx,"btn_type"),    callback_data="menu_type"),
         InlineKeyboardButton(t(ctx,"btn_language"),callback_data="menu_lang")],
    ])


def kb_type(ctx) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(ctx,"btn_movies"), callback_data="settype_movie"),
         InlineKeyboardButton(t(ctx,"btn_tv"),     callback_data="settype_tv")],
        [InlineKeyboardButton(t(ctx,"btn_back"),   callback_data="back_main")],
    ])


def kb_back_home(ctx) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t(ctx,"btn_home"), callback_data="back_main"),
        InlineKeyboardButton(t(ctx,"btn_more"), callback_data="more"),
    ]])


def kb_random_again(ctx) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t(ctx,"btn_home"),       callback_data="back_main"),
        InlineKeyboardButton(t(ctx,"btn_random_more"),callback_data="random"),
    ]])


def kb_genres(ctx, back: str = "back_main") -> InlineKeyboardMarkup:
    lang  = ctx.user_data.get("lang", DEFAULT_LANG)
    rows  = []
    items = list(genres_for(ctx).items())
    for i in range(0, len(items), 2):
        row = [InlineKeyboardButton(label(v, lang), callback_data=f"genre_{k}")
               for k, v in items[i:i+2]]
        rows.append(row)
    rows.append([InlineKeyboardButton(t(ctx,"btn_back"), callback_data=back)])
    return InlineKeyboardMarkup(rows)


def kb_moods(ctx, back: str = "back_main") -> InlineKeyboardMarkup:
    lang = ctx.user_data.get("lang", DEFAULT_LANG)
    rows = [[InlineKeyboardButton(label(v, lang), callback_data=f"mood_{k}")]
            for k, v in MOODS.items()]
    rows.append([InlineKeyboardButton(t(ctx,"btn_back"), callback_data=back)])
    return InlineKeyboardMarkup(rows)


def kb_decades(ctx, back: str = "back_main") -> InlineKeyboardMarkup:
    lang = ctx.user_data.get("lang", DEFAULT_LANG)
    rows = [[InlineKeyboardButton(label(v, lang), callback_data=f"decade_{k}")]
            for k, v in DECADES.items()]
    rows.append([InlineKeyboardButton(t(ctx,"btn_back"), callback_data=back)])
    return InlineKeyboardMarkup(rows)


def kb_keywords(ctx, back: str = "back_main") -> InlineKeyboardMarkup:
    lang  = ctx.user_data.get("lang", DEFAULT_LANG)
    rows  = []
    items = list(KEYWORDS.items())
    for i in range(0, len(items), 2):
        row = [InlineKeyboardButton(label(v, lang), callback_data=f"kw_{k}")
               for k, v in items[i:i+2]]
        rows.append(row)
    rows.append([InlineKeyboardButton(t(ctx,"btn_back"), callback_data=back)])
    return InlineKeyboardMarkup(rows)


def kb_countries(ctx, back: str = "back_main") -> InlineKeyboardMarkup:
    lang  = ctx.user_data.get("lang", DEFAULT_LANG)
    rows  = []
    items = list(COUNTRIES.items())
    for i in range(0, len(items), 2):
        row = [InlineKeyboardButton(label(v, lang), callback_data=f"country_{k}")
               for k, v in items[i:i+2]]
        rows.append(row)
    rows.append([InlineKeyboardButton(t(ctx,"btn_back"), callback_data=back)])
    return InlineKeyboardMarkup(rows)


def kb_languages(ctx) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(name, callback_data=f"setlang_{code}")]
            for code, name in LANG_NAMES.items()]
    rows.append([InlineKeyboardButton(t(ctx,"btn_back"), callback_data="back_main")])
    return InlineKeyboardMarkup(rows)


def kb_combo(ctx) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(ctx,"btn_add_genre"),   callback_data="combo_pick_genre"),
         InlineKeyboardButton(t(ctx,"btn_add_mood"),    callback_data="combo_pick_mood")],
        [InlineKeyboardButton(t(ctx,"btn_add_decade"),  callback_data="combo_pick_decade"),
         InlineKeyboardButton(t(ctx,"btn_add_country"), callback_data="combo_pick_country")],
        [InlineKeyboardButton(t(ctx,"btn_add_keyword"), callback_data="combo_pick_keyword")],
        [InlineKeyboardButton(t(ctx,"btn_search"),      callback_data="combo_search"),
         InlineKeyboardButton(t(ctx,"btn_clear"),       callback_data="combo_clear")],
        [InlineKeyboardButton(t(ctx,"btn_home"),        callback_data="back_main")],
    ])


def combo_filters_text(ctx) -> str:
    lang  = ctx.user_data.get("lang", DEFAULT_LANG)
    combo = ctx.user_data.get("combo", {})
    lines = []
    if "genre" in combo:
        g = genres_for(ctx).get(combo["genre"], {})
        lines.append(f"{t(ctx,'lbl_genre')}: {label(g, lang)}")
    if "mood" in combo:
        lines.append(f"{t(ctx,'lbl_mood')}: {label(MOODS.get(combo['mood'],{}), lang)}")
    if "decade" in combo:
        lines.append(f"{t(ctx,'lbl_decade')}: {label(DECADES.get(combo['decade'],{}), lang)}")
    if "country" in combo:
        lines.append(f"{t(ctx,'lbl_country')}: {label(COUNTRIES.get(combo['country'],{}), lang)}")
    if "keyword" in combo:
        lines.append(f"{t(ctx,'lbl_keyword')}: {label(KEYWORDS.get(combo['keyword'],{}), lang)}")
    ctype = t(ctx, "lbl_type_tv") if is_tv(ctx) else t(ctx, "lbl_type_movie")
    lines.append(f"{t(ctx,'lbl_type')}: {ctype}")
    return "\n".join(f"• {line}" for line in lines) if lines else t(ctx,"combo_no_filter")


# ═══════════════════════════════════════════════════════════════════════════════
#  ХЕНДЛЕРЫ
# ═══════════════════════════════════════════════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if "lang"         not in ctx.user_data: ctx.user_data["lang"]         = DEFAULT_LANG
    if "content_type" not in ctx.user_data: ctx.user_data["content_type"] = DEFAULT_MODE
    ctx.user_data.pop("mode",  None)
    ctx.user_data.pop("combo", None)
    await update.message.reply_text(t(ctx,"welcome"), reply_markup=kb_main(ctx))


async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    await q.answer()
    data = q.data
    lang = ctx.user_data.get("lang", DEFAULT_LANG)
    ct   = ctx.user_data.get("content_type", DEFAULT_MODE)

    # ── Язык ──
    if data == "menu_lang":
        await q.edit_message_text(t(ctx,"choose_language"), reply_markup=kb_languages(ctx))
        return
    if data.startswith("setlang_"):
        ctx.user_data["lang"] = data[8:]
        await q.edit_message_text(t(ctx,"lang_set"), reply_markup=kb_main(ctx))
        return

    # ── Тип контента ──
    if data == "menu_type":
        await q.edit_message_text(t(ctx,"choose_type"), reply_markup=kb_type(ctx))
        return
    if data == "settype_movie":
        ctx.user_data["content_type"] = "movie"
        await q.edit_message_text(t(ctx,"type_set_movie"), reply_markup=kb_main(ctx))
        return
    if data == "settype_tv":
        ctx.user_data["content_type"] = "tv"
        await q.edit_message_text(t(ctx,"type_set_tv"), reply_markup=kb_main(ctx))
        return

    # ── Случайный ──
    if data == "random":
        await q.edit_message_text(t(ctx,"random_searching"))
        item = random_item(ct, lang)
        if item:
            text, poster = format_item(item, ct, t(ctx,"no_desc"), t(ctx,"seasons"))
            if poster:
                await q.message.reply_photo(photo=poster, caption=text, parse_mode="Markdown")
            else:
                await q.message.reply_text(text, parse_mode="Markdown")
            await q.message.reply_text(t(ctx,"random_again"), reply_markup=kb_random_again(ctx))
        else:
            await q.edit_message_text(t(ctx,"random_fail"), reply_markup=kb_main(ctx))
        return

    # ── Навигация ──
    if data == "back_main":
        ctx.user_data.pop("mode",  None)
        ctx.user_data.pop("combo", None)
        await q.edit_message_text(t(ctx,"choose_search"), reply_markup=kb_main(ctx))
        return
    if data == "menu_genre":
        await q.edit_message_text(t(ctx,"choose_genre"),   reply_markup=kb_genres(ctx))
        return
    if data == "menu_mood":
        await q.edit_message_text(t(ctx,"choose_mood"),    reply_markup=kb_moods(ctx))
        return
    if data == "menu_decade":
        await q.edit_message_text(t(ctx,"choose_decade"),  reply_markup=kb_decades(ctx))
        return
    if data == "menu_keyword":
        await q.edit_message_text(t(ctx,"choose_keyword"), reply_markup=kb_keywords(ctx))
        return
    if data == "menu_country":
        await q.edit_message_text(t(ctx,"choose_country"), reply_markup=kb_countries(ctx))
        return
    if data == "menu_similar":
        ctx.user_data["mode"] = "similar_input"
        await q.edit_message_text(
            t(ctx,"similar_prompt"), parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(t(ctx,"btn_back"), callback_data="back_main")
            ]]),
        )
        return

    # ── Простой поиск ──
    if data.startswith("genre_"):
        gid = data[6:]
        ctx.user_data.update({"mode":"genre","genre_id":gid,"page":1})
        await send_results(q, discover(ct, lang, genre_ids=gid), ctx)
        return
    if data.startswith("mood_"):
        key  = data[5:]
        gkey = "tv_genres" if ct == "tv" else "movie_genres"
        gids = MOODS[key][gkey]
        ctx.user_data.update({"mode":"mood","mood_key":key,"page":1})
        await send_results(q, discover(ct, lang, genre_ids=gids), ctx)
        return
    if data.startswith("decade_"):
        key = data[7:]
        d   = DECADES[key]
        ctx.user_data.update({"mode":"decade","decade_key":key,"page":1})
        await send_results(q, discover(ct, lang, date_from=d["from"], date_to=d["to"]), ctx)
        return
    if data.startswith("kw_"):
        key   = data[3:]
        query = KEYWORDS[key]["query"]
        ctx.user_data.update({"mode":"keyword","kw_key":key,"page":1})
        await send_results(q, discover(ct, lang, keyword_query=query), ctx)
        return
    if data.startswith("country_"):
        code = data[8:]
        ctx.user_data.update({"mode":"country","country_code":code,"page":1})
        cname  = label(COUNTRIES.get(code,{}), lang)
        header = t(ctx,"found_country").format(country=cname)
        await send_results(q, discover(ct, lang, country=code), ctx, header=header)
        return

    # ── Ещё ──
    if data == "more":
        mode = ctx.user_data.get("mode")
        ctx.user_data["page"] = ctx.user_data.get("page", 1) + 1
        page = ctx.user_data["page"]
        items = []
        if   mode == "genre":   items = discover(ct, lang, genre_ids=ctx.user_data["genre_id"], page=page)
        elif mode == "mood":
            gkey  = "tv_genres" if ct == "tv" else "movie_genres"
            items = discover(ct, lang, genre_ids=MOODS[ctx.user_data["mood_key"]][gkey], page=page)
        elif mode == "decade":
            d = DECADES[ctx.user_data["decade_key"]]
            items = discover(ct, lang, date_from=d["from"], date_to=d["to"], page=page)
        elif mode == "keyword": items = discover(ct, lang, keyword_query=KEYWORDS[ctx.user_data["kw_key"]]["query"], page=page)
        elif mode == "country": items = discover(ct, lang, country=ctx.user_data["country_code"], page=page)
        elif mode == "combo":   items = run_combo_search(ctx, page=page)

        if items:
            await send_results(q, items, ctx)
        else:
            await q.edit_message_text(t(ctx,"no_more"), reply_markup=kb_back_home(ctx))
        return

    # ── Комбо ──
    if data == "combo_menu":
        if "combo" not in ctx.user_data: ctx.user_data["combo"] = {}
        await show_combo_menu(q, ctx)
        return
    if data == "combo_clear":
        ctx.user_data["combo"] = {}
        await show_combo_menu(q, ctx)
        return
    if data == "combo_pick_genre":
        await q.edit_message_text(t(ctx,"choose_genre"),   reply_markup=kb_genres(ctx,   back="combo_menu"))
        return
    if data == "combo_pick_mood":
        await q.edit_message_text(t(ctx,"choose_mood"),    reply_markup=kb_moods(ctx,    back="combo_menu"))
        return
    if data == "combo_pick_decade":
        await q.edit_message_text(t(ctx,"choose_decade"),  reply_markup=kb_decades(ctx,  back="combo_menu"))
        return
    if data == "combo_pick_country":
        await q.edit_message_text(t(ctx,"choose_country"), reply_markup=kb_countries(ctx,back="combo_menu"))
        return
    if data == "combo_pick_keyword":
        await q.edit_message_text(t(ctx,"choose_keyword"), reply_markup=kb_keywords(ctx, back="combo_menu"))
        return

    combo = ctx.user_data.get("combo")
    if combo is not None:
        if data.startswith("genre_"):   combo["genre"]   = data[6:];  ctx.user_data["combo"] = combo; await show_combo_menu(q, ctx); return
        if data.startswith("mood_"):    combo["mood"]    = data[5:];  ctx.user_data["combo"] = combo; await show_combo_menu(q, ctx); return
        if data.startswith("decade_"):  combo["decade"]  = data[7:];  ctx.user_data["combo"] = combo; await show_combo_menu(q, ctx); return
        if data.startswith("country_"): combo["country"] = data[8:];  ctx.user_data["combo"] = combo; await show_combo_menu(q, ctx); return
        if data.startswith("kw_"):      combo["keyword"] = data[3:];  ctx.user_data["combo"] = combo; await show_combo_menu(q, ctx); return

    if data == "combo_search":
        await q.edit_message_text(t(ctx,"combo_ready"))
        ctx.user_data.update({"mode":"combo","page":1})
        items = run_combo_search(ctx, page=1)
        if items:
            await send_results(q, items, ctx)
        else:
            await q.edit_message_text(
                t(ctx,"combo_no_results"),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(t(ctx,"btn_back"), callback_data="combo_menu")
                ]]),
            )
        return


async def show_combo_menu(q, ctx):
    text = t(ctx,"combo_title").format(filters=combo_filters_text(ctx))
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb_combo(ctx))


def run_combo_search(ctx, page: int = 1) -> list[dict]:
    combo = ctx.user_data.get("combo", {})
    lang  = ctx.user_data.get("lang", DEFAULT_LANG)
    ct    = ctx.user_data.get("content_type", DEFAULT_MODE)
    gkey  = "tv_genres" if ct == "tv" else "movie_genres"

    genre_ids = combo.get("genre", "")
    if not genre_ids and "mood" in combo:
        genre_ids = MOODS[combo["mood"]][gkey]

    d_from = d_to = ""
    if "decade" in combo:
        d = DECADES[combo["decade"]]
        d_from, d_to = d["from"], d["to"]

    return discover(
        ct, lang,
        genre_ids=genre_ids,
        date_from=d_from,
        date_to=d_to,
        keyword_query=KEYWORDS[combo["keyword"]]["query"] if "keyword" in combo else "",
        country=combo.get("country", ""),
        page=page,
    )


async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    mode = ctx.user_data.get("mode")
    lang = ctx.user_data.get("lang", DEFAULT_LANG)
    ct   = ctx.user_data.get("content_type", DEFAULT_MODE)

    if mode == "similar_input":
        title = update.message.text.strip()
        await update.message.reply_text(t(ctx,"searching").format(title=title))
        results = search_items(title, ct, lang)
        if not results:
            await update.message.reply_text(t(ctx,"not_found_title"), reply_markup=kb_main(ctx))
            return
        item    = results[0]
        name    = item.get("title") or item.get("name", "?")
        similar = similar_items(item["id"], ct, lang)
        ctx.user_data["mode"] = "done"
        if similar:
            await update.message.reply_text(t(ctx,"found_similar").format(title=name))
            for m in similar:
                text, poster = format_item(m, ct, t(ctx,"no_desc"), t(ctx,"seasons"))
                if poster:
                    await update.message.reply_photo(photo=poster, caption=text, parse_mode="Markdown")
                else:
                    await update.message.reply_text(text, parse_mode="Markdown")
            await update.message.reply_text(t(ctx,"find_more"), reply_markup=kb_main(ctx))
        else:
            await update.message.reply_text(t(ctx,"no_similar"), reply_markup=kb_main(ctx))
    else:
        await update.message.reply_text(t(ctx,"choose_search"), reply_markup=kb_main(ctx))


async def send_results(q, items: list[dict], ctx, header: str = ""):
    ct = ctx.user_data.get("content_type", DEFAULT_MODE)
    if not header:
        header = t(ctx,"found")
    if not items:
        await q.edit_message_text(t(ctx,"no_results"), reply_markup=kb_back_home(ctx))
        return
    await q.edit_message_text(header)
    for m in items:
        text, poster = format_item(m, ct, t(ctx,"no_desc"), t(ctx,"seasons"))
        if poster:
            await q.message.reply_photo(photo=poster, caption=text, parse_mode="Markdown")
        else:
            await q.message.reply_text(text, parse_mode="Markdown")
    await q.message.reply_text(t(ctx,"show_more"), reply_markup=kb_back_home(ctx))


# ═══════════════════════════════════════════════════════════════════════════════
#  ЗАПУСК
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    log.info("Heisenberg Bot запущен.")
    app.run_polling()


if __name__ == "__main__":
    main()