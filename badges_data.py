# -*- coding: utf-8 -*-
"""
بيانات ومحرك الأوسمة والإنجازات الشاملة للتطبيق (220+ وسام مرتبة من الأسهل للأصعب)
مع التزام تام بالقيم والأخلاق الإسلامية وتفادي أية ألفاظ غير مناسبة.
"""

ALL_BADGES = [
    # ─────────────────────────────────────────────────────────────────────────
    # 🎓 1. قسم التعلم والتركيز (45 وسام) - مرتبة حسب الدقائق من 5 إلى 30,000
    # ─────────────────────────────────────────────────────────────────────────
    {"id": "b_learn_1",  "cat": "learn", "title": "🌱 البداية المباركة",       "desc": "إنجاز 5 دقائق تعلم",               "pts": 10,  "learn_day": 5},
    {"id": "b_learn_2",  "cat": "learn", "title": "⏱️ 10 دقائق انضباط",       "desc": "إنجاز 10 دقائق تعلم",              "pts": 15,  "learn_day": 10},
    {"id": "b_learn_3",  "cat": "learn", "title": "🎓 طالب العلم",             "desc": "إنجاز 15 دقيقة تعلم",              "pts": 20,  "learn_day": 15},
    {"id": "b_learn_4",  "cat": "learn", "title": "📖 صديق الكتاب",            "desc": "إنجاز 20 دقيقة تعلم",              "pts": 25,  "learn_day": 20},
    {"id": "b_learn_5",  "cat": "learn", "title": "🧠 التركيز العالي",          "desc": "إنجاز 30 دقيقة تعلم في يوم واحد",  "pts": 35,  "learn_day": 30},
    {"id": "b_learn_6",  "cat": "learn", "title": "⚡ شوط الإنجاز",            "desc": "إنجاز 45 دقيقة تعلم في يوم واحد",  "pts": 50,  "learn_day": 45},
    {"id": "b_learn_7",  "cat": "learn", "title": "🚀 ساعة كاملة من العلم",    "desc": "إنجاز 60 دقيقة (ساعة) في يوم واحد","pts": 70,  "learn_day": 60},
    {"id": "b_learn_8",  "cat": "learn", "title": "💡 عقلية مستنيرة",         "desc": "إنجاز 90 دقيقة تعلم في يوم واحد",  "pts": 100, "learn_day": 90},
    {"id": "b_learn_9",  "cat": "learn", "title": "📚 الباحث المجتهد",        "desc": "إنجاز 120 دقيقة (ساعتان) يومياً",  "pts": 130, "learn_day": 120},
    {"id": "b_learn_10", "cat": "learn", "title": "🔥 طاقة التعلم",            "desc": "إنجاز 150 دقيقة تعلم في يوم واحد", "pts": 160, "learn_day": 150},
    {"id": "b_learn_11", "cat": "learn", "title": "🏛️ ركن المعرفة",           "desc": "إنجاز 180 دقيقة (3 ساعات) يومياً", "pts": 200, "learn_day": 180},
    {"id": "b_learn_12", "cat": "learn", "title": "🌟 شغف التعلم",            "desc": "إنجاز 240 دقيقة (4 ساعات) يومياً", "pts": 250, "learn_day": 240},
    {"id": "b_learn_13", "cat": "learn", "title": "🎯 عملاق التركيز",         "desc": "إنجاز 300 دقيقة تعلم إجمالاً",     "pts": 300, "learn_total": 300},
    {"id": "b_learn_14", "cat": "learn", "title": "🏆 قاهر الكسل",            "desc": "إنجاز 360 دقيقة (6 ساعات) إجمالاً","pts": 350, "learn_total": 360},
    {"id": "b_learn_15", "cat": "learn", "title": "💎 جوهرة الاجتهاد",        "desc": "إنجاز 420 دقيقة تعلم إجمالاً",     "pts": 400, "learn_total": 420},
    {"id": "b_learn_16", "cat": "learn", "title": "🌌 أسطورة الصبر",          "desc": "إنجاز 480 دقيقة (8 ساعات) إجمالاً","pts": 450, "learn_total": 480},
    {"id": "b_learn_17", "cat": "learn", "title": "👑 ملك التعلم",            "desc": "إنجاز 600 دقيقة (10 ساعات) إجمالاً","pts": 550, "learn_total": 600},
    {"id": "b_learn_18", "cat": "learn", "title": "🛡️ درع العلم",             "desc": "إنجاز 720 دقيقة (12 ساعة) إجمالاً","pts": 650, "learn_total": 720},
    {"id": "b_learn_19", "cat": "learn", "title": "⚔️ فارس المعرفة",          "desc": "إنجاز 900 دقيقة (15 ساعة) إجمالاً","pts": 800, "learn_total": 900},
    {"id": "b_learn_20", "cat": "learn", "title": "✨ منار الحكمة",           "desc": "إنجاز 1080 دقيقة (18 ساعة) إجمالاً","pts": 950, "learn_total": 1080},
    {"id": "b_learn_21", "cat": "learn", "title": "🎓 شعلة الفكر",            "desc": "إنجاز 1200 دقيقة (20 ساعة) إجمالاً","pts": 1100,"learn_total": 1200},
    {"id": "b_learn_22", "cat": "learn", "title": "🌟 رائد الاجتهاد",         "desc": "إنجاز 1500 دقيقة (25 ساعة) إجمالاً","pts": 1300,"learn_total": 1500},
    {"id": "b_learn_23", "cat": "learn", "title": "📚 صاحب الهمة العالية",    "desc": "إنجاز 1800 دقيقة (30 ساعة) إجمالاً","pts": 1500,"learn_total": 1800},
    {"id": "b_learn_24", "cat": "learn", "title": "💡 قنديل المعرفة",         "desc": "إنجاز 2100 دقيقة (35 ساعة) إجمالاً","pts": 1750,"learn_total": 2100},
    {"id": "b_learn_25", "cat": "learn", "title": "🚀 سفير الإنجاز",          "desc": "إنجاز 2400 دقيقة (40 ساعة) إجمالاً","pts": 2000,"learn_total": 2400},
    {"id": "b_learn_26", "cat": "learn", "title": "🔥 منارة الاجتهاد",        "desc": "إنجاز 2700 دقيقة (45 ساعة) إجمالاً","pts": 2250,"learn_total": 2700},
    {"id": "b_learn_27", "cat": "learn", "title": "🏛️ صرح العلم",             "desc": "إنجاز 3000 دقيقة (50 ساعة) إجمالاً","pts": 2500,"learn_total": 3000},
    {"id": "b_learn_28", "cat": "learn", "title": "💎 درة الفهم",             "desc": "إنجاز 3600 دقيقة (60 ساعة) إجمالاً","pts": 3000,"learn_total": 3600},
    {"id": "b_learn_29", "cat": "learn", "title": "🌌 عقلية العلماء",        "desc": "إنجاز 4200 دقيقة (70 ساعة) إجمالاً","pts": 3500,"learn_total": 4200},
    {"id": "b_learn_30", "cat": "learn", "title": "👑 تاج المتعلمين",         "desc": "إنجاز 4800 دقيقة (80 ساعة) إجمالاً","pts": 4000,"learn_total": 4800},
    {"id": "b_learn_31", "cat": "learn", "title": "✨ نور البصيرة",           "desc": "إنجاز 5400 دقيقة (90 ساعة) إجمالاً","pts": 4500,"learn_total": 5400},
    {"id": "b_learn_32", "cat": "learn", "title": "🏆 مائة ساعة علم",         "desc": "إنجاز 6000 دقيقة (100 ساعة) إجمالاً","pts": 5000,"learn_total": 6000},
    {"id": "b_learn_33", "cat": "learn", "title": "🌟 قمة المجد المعرفي",     "desc": "إنجاز 7200 دقيقة (120 ساعة) إجمالاً","pts": 6000,"learn_total": 7200},
    {"id": "b_learn_34", "cat": "learn", "title": "📖 حارس الحكمة",           "desc": "إنجاز 8400 دقيقة (140 ساعة) إجمالاً","pts": 7000,"learn_total": 8400},
    {"id": "b_learn_35", "cat": "learn", "title": "⚡ طاقة الفكر",            "desc": "إنجاز 9600 دقيقة (160 ساعة) إجمالاً","pts": 8000,"learn_total": 9600},
    {"id": "b_learn_36", "cat": "learn", "title": "🎯 قدوة الإنجاز",          "desc": "إنجاز 10800 دقيقة (180 ساعة) إجمالاً","pts": 9000,"learn_total": 10800},
    {"id": "b_learn_37", "cat": "learn", "title": "💎 مائتا ساعة تركيز",     "desc": "إنجاز 12000 دقيقة (200 ساعة) إجمالاً","pts": 10000,"learn_total": 12000},
    {"id": "b_learn_38", "cat": "learn", "title": "🌌 أسطورة الفهم",          "desc": "إنجاز 13500 دقيقة (225 ساعة) إجمالاً","pts": 11500,"learn_total": 13500},
    {"id": "b_learn_39", "cat": "learn", "title": "👑 سيد العزيمة",           "desc": "إنجاز 15000 دقيقة (250 ساعة) إجمالاً","pts": 13000,"learn_total": 15000},
    {"id": "b_learn_40", "cat": "learn", "title": "✨ قمة الحكمة",            "desc": "إنجاز 16500 دقيقة (275 ساعة) إجمالاً","pts": 15000,"learn_total": 16500},
    {"id": "b_learn_41", "cat": "learn", "title": "🏆 ثلاثمائة ساعة علم",     "desc": "إنجاز 18000 دقيقة (300 ساعة) إجمالاً","pts": 17000,"learn_total": 18000},
    {"id": "b_learn_42", "cat": "learn", "title": "🌟 كوكب المعرفة",         "desc": "إنجاز 19500 دقيقة (325 ساعة) إجمالاً","pts": 19000,"learn_total": 19500},
    {"id": "b_learn_43", "cat": "learn", "title": "⚔️ قاهر التشتت",           "desc": "إنجاز 21000 دقيقة (350 ساعة) إجمالاً","pts": 21000,"learn_total": 21000},
    {"id": "b_learn_44", "cat": "learn", "title": "💎 أسطورة العلم الأبدية",  "desc": "إنجاز 24000 دقيقة (400 ساعة) إجمالاً","pts": 25000,"learn_total": 24000},
    {"id": "b_learn_45", "cat": "learn", "title": "👑 القمة المطلقة للتركيز",  "desc": "إنجاز 30000 دقيقة (500 ساعة) إجمالاً","pts": 35000,"learn_total": 30000},

    # ─────────────────────────────────────────────────────────────────────────
    # 🔥 2. قسم الستريك والتتابع (30 وسام) - مرتبة من يوم واحد إلى 365 يوماً
    # ─────────────────────────────────────────────────────────────────────────
    {"id": "b_streak_1",  "cat": "streak", "title": "🌱 الشرارة الأولى",       "desc": "الالتزام بيوم واحد متتالي",        "pts": 15,  "streak_min": 1},
    {"id": "b_streak_2",  "cat": "streak", "title": "🔥 خطوتان ثابتتان",       "desc": "الالتزام بيومين متتاليين",         "pts": 25,  "streak_min": 2},
    {"id": "b_streak_3",  "cat": "streak", "title": "⚡ شعلة الالتزام",        "desc": "الالتزام بـ 3 أيام متتالية",       "pts": 40,  "streak_min": 3},
    {"id": "b_streak_4",  "cat": "streak", "title": "📖 أربعة أيام انضباط",    "desc": "الالتزام بـ 4 أيام متتالية",       "pts": 55,  "streak_min": 4},
    {"id": "b_streak_5",  "cat": "streak", "title": "🎯 تتابع مستمر",          "desc": "الالتزام بـ 5 أيام متتالية",       "pts": 70,  "streak_min": 5},
    {"id": "b_streak_6",  "cat": "streak", "title": "💪 ستة أيام قوة",         "desc": "الالتزام بـ 6 أيام متتالية",       "pts": 90,  "streak_min": 6},
    {"id": "b_streak_7",  "cat": "streak", "title": "🏆 أسبوع كامل من الانضباط","desc": "الالتزام بـ 7 أيام (أسبوع) متتالية", "pts": 120, "streak_min": 7},
    {"id": "b_streak_8",  "cat": "streak", "title": "🚀 انطلاقة الأسبوع الثاني","desc": "الالتزام بـ 8 أيام متتالية",       "pts": 140, "streak_min": 8},
    {"id": "b_streak_9",  "cat": "streak", "title": "✨ تسعة أيام استقامة",     "desc": "الالتزام بـ 9 أيام متتالية",       "pts": 160, "streak_min": 9},
    {"id": "b_streak_10", "cat": "streak", "title": "🔥 عشرة أيام نارية",       "desc": "الالتزام بـ 10 أيام متتالية",      "pts": 200, "streak_min": 10},
    {"id": "b_streak_11", "cat": "streak", "title": "💡 عزيمة متواصلة",        "desc": "الالتزام بـ 12 يوماً متتالياً",    "pts": 250, "streak_min": 12},
    {"id": "b_streak_12", "cat": "streak", "title": "🌟 أسبوعان من الإنجاز",    "desc": "الالتزام بـ 14 يوماً (أسبوعين)",   "pts": 300, "streak_min": 14},
    {"id": "b_streak_13", "cat": "streak", "title": "📚 تتابع صلب",            "desc": "الالتزام بـ 16 يوماً متتالياً",    "pts": 350, "streak_min": 16},
    {"id": "b_streak_14", "cat": "streak", "title": "💎 جوهرة الالتزام",       "desc": "الالتزام بـ 18 يوماً متتالياً",    "pts": 400, "streak_min": 18},
    {"id": "b_streak_15", "cat": "streak", "title": "⚡ عشرون يوماً قوة",       "desc": "الالتزام بـ 20 يوماً متتالياً",    "pts": 500, "streak_min": 20},
    {"id": "b_streak_16", "cat": "streak", "title": "🏛️ ثلاثة أسابيع انضباط",   "desc": "الالتزام بـ 21 يوماً بلا انقطاع",  "pts": 600, "streak_min": 21},
    {"id": "b_streak_17", "cat": "streak", "title": "🔥 ربع مائة يوم",          "desc": "الالتزام بـ 25 يوماً متتالياً",    "pts": 750, "streak_min": 25},
    {"id": "b_streak_18", "cat": "streak", "title": "👑 شهر كامل من الانضباط", "desc": "الالتزام بـ 30 يوماً متتالياً",    "pts": 1000,"streak_min": 30},
    {"id": "b_streak_19", "cat": "streak", "title": "🚀 استمرار أسطوري",       "desc": "الالتزام بـ 35 يوماً متتالياً",    "pts": 1200,"streak_min": 35},
    {"id": "b_streak_20", "cat": "streak", "title": "✨ أربعون يوماً من الصبر", "desc": "الالتزام بـ 40 يوماً متتالياً",    "pts": 1500,"streak_min": 40},
    {"id": "b_streak_21", "cat": "streak", "title": "🎯 شهر ونصف من النقاء",   "desc": "الالتزام بـ 45 يوماً متتالياً",    "pts": 1800,"streak_min": 45},
    {"id": "b_streak_22", "cat": "streak", "title": "🏆 خمسون يوماً متتالية",   "desc": "الالتزام بـ 50 يوماً متتالياً",    "pts": 2200,"streak_min": 50},
    {"id": "b_streak_23", "cat": "streak", "title": "💎 شهران من الاستقامة",    "desc": "الالتزام بـ 60 يوماً (شهرين)",     "pts": 3000,"streak_min": 60},
    {"id": "b_streak_24", "cat": "streak", "title": "🌌 قاهر التسويف",          "desc": "الالتزام بـ 75 يوماً متتالياً",    "pts": 4000,"streak_min": 75},
    {"id": "b_streak_25", "cat": "streak", "title": "👑 ثلاثة أشهر أسطورية",   "desc": "الالتزام بـ 90 يوماً متتالياً",    "pts": 5000,"streak_min": 90},
    {"id": "b_streak_26", "cat": "streak", "title": "🌟 أربعة أشهر من التتابع", "desc": "الالتزام بـ 120 يوماً متتالياً",   "pts": 7000,"streak_min": 120},
    {"id": "b_streak_27", "cat": "streak", "title": "⚔️ فارس الاستمرارية",      "desc": "الالتزام بـ 150 يوماً متتالياً",   "pts": 9000,"streak_min": 150},
    {"id": "b_streak_28", "cat": "streak", "title": "🏆 نصف عام من الإنجاز",    "desc": "الالتزام بـ 180 يوماً (6 أشهر)",   "pts": 12000,"streak_min": 180},
    {"id": "b_streak_29", "cat": "streak", "title": "💎 تسعة أشهر استقامة",     "desc": "الالتزام بـ 270 يوماً متتالياً",   "pts": 18000,"streak_min": 270},
    {"id": "b_streak_30", "cat": "streak", "title": "👑 عام كامل من النجاح",   "desc": "الالتزام بـ 365 يوماً (سنة كاملة)","pts": 25000,"streak_min": 365},

    # ─────────────────────────────────────────────────────────────────────────
    # 💧 3. قسم شرب الماء والصحة (30 وسام) - مرتبة من كوب واحد إلى 2000 كوب
    # ─────────────────────────────────────────────────────────────────────────
    {"id": "b_water_1",  "cat": "water", "title": "💧 أول كوب ماء",           "desc": "شرب كوب ماء واحد",                 "pts": 10,  "water_min": 1},
    {"id": "b_water_2",  "cat": "water", "title": "🌱 قطرة الانتعاش",         "desc": "شرب 3 أكواب ماء في يوم واحد",      "pts": 20,  "water_min": 3},
    {"id": "b_water_3",  "cat": "water", "title": "🚿 المنتعش الصحي",           "desc": "شرب 6 أكواب ماء في يوم واحد",      "pts": 35,  "water_min": 6},
    {"id": "b_water_4",  "cat": "water", "title": "🌊 رواء الجسد",             "desc": "شرب 10 أكواب ماء إجمالاً",         "pts": 50,  "water_total": 10},
    {"id": "b_water_5",  "cat": "water", "title": "💡 عادة صحية",             "desc": "شرب 15 كوب ماء إجمالاً",         "pts": 70,  "water_total": 15},
    {"id": "b_water_6",  "cat": "water", "title": "💪 حيوية ونشاط",            "desc": "شرب 20 كوب ماء إجمالاً",         "pts": 90,  "water_total": 20},
    {"id": "b_water_7",  "cat": "water", "title": "🎯 ثلاثون كوباً",          "desc": "شرب 30 كوب ماء إجمالاً",         "pts": 120, "water_total": 30},
    {"id": "b_water_8",  "cat": "water", "title": "✨ نبع الصحة",             "desc": "شرب 40 كوب ماء إجمالاً",         "pts": 150, "water_total": 40},
    {"id": "b_water_9",  "cat": "water", "title": "🚀 خمسون كوباً",           "desc": "شرب 50 كوب ماء إجمالاً",         "pts": 200, "water_total": 50},
    {"id": "b_water_10", "cat": "water", "title": "🍃 طاقة الانتعاش",         "desc": "شرب 65 كوب ماء إجمالاً",         "pts": 250, "water_total": 65},
    {"id": "b_water_11", "cat": "water", "title": "💎 صافي الهيدرات",        "desc": "شرب 80 كوب ماء إجمالاً",         "pts": 300, "water_total": 80},
    {"id": "b_water_12", "cat": "water", "title": "🏆 مائة كوب ماء",          "desc": "شرب 100 كوب ماء إجمالاً",        "pts": 400, "water_total": 100},
    {"id": "b_water_13", "cat": "water", "title": "🌟 رواء تام",              "desc": "شرب 125 كوب ماء إجمالاً",        "pts": 500, "water_total": 125},
    {"id": "b_water_14", "cat": "water", "title": "💧 نبع النقاء",            "desc": "شرب 150 كوب ماء إجمالاً",        "pts": 600, "water_total": 150},
    {"id": "b_water_15", "cat": "water", "title": "🌊 غيث الصحة",             "desc": "شرب 175 كوب ماء إجمالاً",        "pts": 700, "water_total": 175},
    {"id": "b_water_16", "cat": "water", "title": "👑 مائتان كوب ماء",        "desc": "شرب 200 كوب ماء إجمالاً",        "pts": 850, "water_total": 200},
    {"id": "b_water_17", "cat": "water", "title": "🏛️ صرح الانتعاش",         "desc": "شرب 250 كوب ماء إجمالاً",        "pts": 1000,"water_total": 250},
    {"id": "b_water_18", "cat": "water", "title": "✨ ثلاثمائة كوب",          "desc": "شرب 300 كوب ماء إجمالاً",        "pts": 1200,"water_total": 300},
    {"id": "b_water_19", "cat": "water", "title": "🎯 محيط الصحة",          "desc": "شرب 350 كوب ماء إجمالاً",        "pts": 1400,"water_total": 350},
    {"id": "b_water_20", "cat": "water", "title": "🚀 أربعمائة كوب",          "desc": "شرب 400 كوب ماء إجمالاً",        "pts": 1600,"water_total": 400},
    {"id": "b_water_21", "cat": "water", "title": "💎 بركة الماء",            "desc": "شرب 450 كوب ماء إجمالاً",        "pts": 1800,"water_total": 450},
    {"id": "b_water_22", "cat": "water", "title": "🏆 خمسمائة كوب ماء",       "desc": "شرب 500 كوب ماء إجمالاً",        "pts": 2200,"water_total": 500},
    {"id": "b_water_23", "cat": "water", "title": "🌟 شلال الصحة",            "desc": "شرب 600 كوب ماء إجمالاً",        "pts": 2600,"water_total": 600},
    {"id": "b_water_24", "cat": "water", "title": "💧 بحيرة الترطيب",         "desc": "شرب 700 كوب ماء إجمالاً",        "pts": 3000,"water_total": 700},
    {"id": "b_water_25", "cat": "water", "title": "🌌 ثمانمائة كوب",          "desc": "شرب 800 كوب ماء إجمالاً",        "pts": 3500,"water_total": 800},
    {"id": "b_water_26", "cat": "water", "title": "✨ نهج الصحة الأبدي",      "desc": "شرب 900 كوب ماء إجمالاً",        "pts": 4000,"water_total": 900},
    {"id": "b_water_27", "cat": "water", "title": "👑 ألف كوب ماء صحي",       "desc": "شرب 1000 كوب ماء إجمالاً",       "pts": 5000,"water_total": 1000},
    {"id": "b_water_28", "cat": "water", "title": "🏆 1250 كوباً صحياً",       "desc": "شرب 1250 كوب ماء إجمالاً",       "pts": 6500,"water_total": 1250},
    {"id": "b_water_29", "cat": "water", "title": "💎 1500 كوب ماء",          "desc": "شرب 1500 كوب ماء إجمالاً",       "pts": 8000,"water_total": 1500},
    {"id": "b_water_30", "cat": "water", "title": "👑 ألفا كوب ماء (سيد الصحة)","desc": "شرب 2000 كوب ماء إجمالاً",       "pts": 11000,"water_total": 2000},

    # ─────────────────────────────────────────────────────────────────────────
    # 🏋️ 4. قسم الرياضة والتمارين (35 وسام) - مرتبة من 5 ضغطات إلى 10,000 ضغطة
    # ─────────────────────────────────────────────────────────────────────────
    {"id": "b_pushups_1",  "cat": "pushups", "title": "🏋️ أول 5 ضغطات",        "desc": "إنجاز 5 ضغطات في جلسة واحدة",     "pts": 15,  "pushups_min": 5},
    {"id": "b_pushups_2",  "cat": "pushups", "title": "💪 بداية القوة",        "desc": "إنجاز 10 ضغطات في جلسة واحدة",    "pts": 25,  "pushups_min": 10},
    {"id": "b_pushups_3",  "cat": "pushups", "title": "⚡ نشاط البدن",         "desc": "إنجاز 15 ضغطة في جلسة واحدة",    "pts": 35,  "pushups_min": 15},
    {"id": "b_pushups_4",  "cat": "pushups", "title": "🎯 عضلات مشدودة",       "desc": "إنجاز 20 ضغطة في جلسة واحدة",    "pts": 50,  "pushups_min": 20},
    {"id": "b_pushups_5",  "cat": "pushups", "title": "🚀 ثلاثون ضغطة",        "desc": "إنجاز 30 ضغطة في جلسة واحدة",    "pts": 70,  "pushups_min": 30},
    {"id": "b_pushups_6",  "cat": "pushups", "title": "🔥 طاقة رياضية",        "desc": "إنجاز 40 ضغطة إجمالاً",           "pts": 90,  "pushups_total": 40},
    {"id": "b_pushups_7",  "cat": "pushups", "title": "🏆 خمسون ضغطة",        "desc": "إنجاز 50 ضغطة إجمالاً",           "pts": 120, "pushups_total": 50},
    {"id": "b_pushups_8",  "cat": "pushups", "title": "✨ لياقة تزداد",        "desc": "إنجاز 65 ضغطة إجمالاً",           "pts": 150, "pushups_total": 65},
    {"id": "b_pushups_9",  "cat": "pushups", "title": "💡 صلابة البدن",        "desc": "إنجاز 80 ضغطة إجمالاً",           "pts": 180, "pushups_total": 80},
    {"id": "b_pushups_10", "cat": "pushups", "title": "💎 مائة ضغطة إجمالاً",   "desc": "إنجاز 100 ضغطة إجمالاً",          "pts": 220, "pushups_total": 100},
    {"id": "b_pushups_11", "cat": "pushups", "title": "🥊 مقاتل النشاط",       "desc": "إنجاز 125 ضغطة إجمالاً",          "pts": 270, "pushups_total": 125},
    {"id": "b_pushups_12", "cat": "pushups", "title": "🌟 150 ضغطة رياضية",     "desc": "إنجاز 150 ضغطة إجمالاً",          "pts": 320, "pushups_total": 150},
    {"id": "b_pushups_13", "cat": "pushups", "title": "💪 قوة من حديد",        "desc": "إنجاز 175 ضغطة إجمالاً",          "pts": 380, "pushups_total": 175},
    {"id": "b_pushups_14", "cat": "pushups", "title": "🏆 مائتان ضغطة",        "desc": "إنجاز 200 ضغطة إجمالاً",          "pts": 450, "pushups_total": 200},
    {"id": "b_pushups_15", "cat": "pushups", "title": "🎯 أسد اللياقة",        "desc": "إنجاز 250 ضغطة إجمالاً",          "pts": 550, "pushups_total": 250},
    {"id": "b_pushups_16", "cat": "pushups", "title": "⚡ ثلاثمائة ضغطة",       "desc": "إنجاز 300 ضغطة إجمالاً",          "pts": 650, "pushups_total": 300},
    {"id": "b_pushups_17", "cat": "pushups", "title": "🚀 عزيمة رياضية",       "desc": "إنجاز 350 ضغطة إجمالاً",          "pts": 750, "pushups_total": 350},
    {"id": "b_pushups_18", "cat": "pushups", "title": "✨ أربعمائة ضغطة",       "desc": "إنجاز 400 ضغطة إجمالاً",          "pts": 850, "pushups_total": 400},
    {"id": "b_pushups_19", "cat": "pushups", "title": "💎 لياقة بدنية عالية",   "desc": "إنجاز 450 ضغطة إجمالاً",          "pts": 950, "pushups_total": 450},
    {"id": "b_pushups_20", "cat": "pushups", "title": "👑 خمسمائة ضغطة",       "desc": "إنجاز 500 ضغطة إجمالاً",          "pts": 1100,"pushups_total": 500},
    {"id": "b_pushups_21", "cat": "pushups", "title": "🥊 بطل القوة والبدن",    "desc": "إنجاز 600 ضغطة إجمالاً",          "pts": 1300,"pushups_total": 600},
    {"id": "b_pushups_22", "cat": "pushups", "title": "🌟 سبعمائة ضغطة",       "desc": "إنجاز 700 ضغطة إجمالاً",          "pts": 1500,"pushups_total": 700},
    {"id": "b_pushups_23", "cat": "pushups", "title": "⚡ ثمانمائة ضغطة",       "desc": "إنجاز 800 ضغطة إجمالاً",          "pts": 1800,"pushups_total": 800},
    {"id": "b_pushups_24", "cat": "pushups", "title": "🔥 تسعمائة ضغطة",       "desc": "إنجاز 900 ضغطة إجمالاً",          "pts": 2100,"pushups_total": 900},
    {"id": "b_pushups_25", "cat": "pushups", "title": "🏆 ألف ضغطة رياضية",     "desc": "إنجاز 1000 ضغطة إجمالاً",         "pts": 2500,"pushups_total": 1000},
    {"id": "b_pushups_26", "cat": "pushups", "title": "💎 1250 ضغطة",          "desc": "إنجاز 1250 ضغطة إجمالاً",         "pts": 3000,"pushups_total": 1250},
    {"id": "b_pushups_27", "cat": "pushups", "title": "👑 عملاق اللياقة",      "desc": "إنجاز 1500 ضغطة إجمالاً",         "pts": 3600,"pushups_total": 1500},
    {"id": "b_pushups_28", "cat": "pushups", "title": "🌌 ألفا ضغطة",           "desc": "إنجاز 2000 ضغطة إجمالاً",         "pts": 4500,"pushups_total": 2000},
    {"id": "b_pushups_29", "cat": "pushups", "title": "⚔️ فارس اللياقة البدنية","desc": "إنجاز 2500 ضغطة إجمالاً",         "pts": 5500,"pushups_total": 2500},
    {"id": "b_pushups_30", "cat": "pushups", "title": "🏆 ثلاثة آلاف ضغطة",     "desc": "إنجاز 3000 ضغطة إجمالاً",         "pts": 6500,"pushups_total": 3000},
    {"id": "b_pushups_31", "cat": "pushups", "title": "💎 أربعة آلاف ضغطة",    "desc": "إنجاز 4000 ضغطة إجمالاً",         "pts": 8500,"pushups_total": 4000},
    {"id": "b_pushups_32", "cat": "pushups", "title": "👑 خمسة آلاف ضغطة",     "desc": "إنجاز 5000 ضغطة إجمالاً",         "pts": 11000,"pushups_total": 5000},
    {"id": "b_pushups_33", "cat": "pushups", "title": "🌟 6500 ضغطة رياضية",    "desc": "إنجاز 6500 ضغطة إجمالاً",         "pts": 14000,"pushups_total": 6500},
    {"id": "b_pushups_34", "cat": "pushups", "title": "⚡ ثمانية آلاف ضغطة",    "desc": "إنجاز 8000 ضغطة إجمالاً",         "pts": 18000,"pushups_total": 8000},
    {"id": "b_pushups_35", "cat": "pushups", "title": "👑 عشرة آلاف ضغطة (أسطورة البدن)","desc": "إنجاز 10000 ضغطة إجمالاً","pts": 25000,"pushups_total": 10000},

    # ─────────────────────────────────────────────────────────────────────────
    # 📿 5. قسم العبادة والصلوات والأذكار (30 وسام) - مرتبة من صلاة واحدة إلى 2000
    # ─────────────────────────────────────────────────────────────────────────
    {"id": "b_prayer_1",  "cat": "prayer", "title": "🕌 الصلاة الأولى",        "desc": "أداء أول صلاة أو ذِكر مبارك",       "pts": 15,  "prayer_total": 1},
    {"id": "b_prayer_2",  "cat": "prayer", "title": "✨ حافظ الصلاة",         "desc": "أداء 3 صلوات أو أذكار",            "pts": 25,  "prayer_total": 3},
    {"id": "b_prayer_3",  "cat": "prayer", "title": "☀️ صلوات اليوم الكاملة",  "desc": "أداء 5 صلوات مباركة",              "pts": 40,  "prayer_total": 5},
    {"id": "b_prayer_4",  "cat": "prayer", "title": "📿 عشر صلوات وأذكار",     "desc": "أداء 10 صلوات أو أذكار",           "pts": 60,  "prayer_total": 10},
    {"id": "b_prayer_5",  "cat": "prayer", "title": "🌙 طمأنينة القلب",       "desc": "أداء 15 صلاة أو ذِكراً",           "pts": 80,  "prayer_total": 15},
    {"id": "b_prayer_6",  "cat": "prayer", "title": "💡 منار الإيمان",        "desc": "أداء 20 صلاة مباركة",              "pts": 100, "prayer_total": 20},
    {"id": "b_prayer_7",  "cat": "prayer", "title": "🤲 دعاء وذكر",            "desc": "أداء 25 صلاة أو ذِكراً",           "pts": 125, "prayer_total": 25},
    {"id": "b_prayer_8",  "cat": "prayer", "title": "🎯 ثلاثون صلاة مباركة",   "desc": "أداء 30 صلاة أو ذِكراً",           "pts": 150, "prayer_total": 30},
    {"id": "b_prayer_9",  "cat": "prayer", "title": "🚀 أربعون صلاة",          "desc": "أداء 40 صلاة أو ذِكراً",           "pts": 180, "prayer_total": 40},
    {"id": "b_prayer_10", "cat": "prayer", "title": "🏆 خمسون صلاة مباركة",    "desc": "أداء 50 صلاة أو ذِكراً إجمالاً",   "pts": 220, "prayer_total": 50},
    {"id": "b_prayer_11", "cat": "prayer", "title": "🍃 صلة بالخالق",         "desc": "أداء 65 صلاة أو ذِكراً",           "pts": 270, "prayer_total": 65},
    {"id": "b_prayer_12", "cat": "prayer", "title": "✨ ثمانون ذِكراً وصلاة",   "desc": "أداء 80 صلاة أو ذِكراً",           "pts": 330, "prayer_total": 80},
    {"id": "b_prayer_13", "cat": "prayer", "title": "💎 مائة صلاة مباركة",     "desc": "أداء 100 صلاة أو ذِكراً إجمالاً",  "pts": 400, "prayer_total": 100},
    {"id": "b_prayer_14", "cat": "prayer", "title": "🌟 خشوع وطمأنينة",       "desc": "أداء 125 صلاة أو ذِكراً",          "pts": 480, "prayer_total": 125},
    {"id": "b_prayer_15", "cat": "prayer", "title": "🕌 حارس الصلوات",        "desc": "أداء 150 صلاة أو ذِكراً",          "pts": 580, "prayer_total": 150},
    {"id": "b_prayer_16", "cat": "prayer", "title": "📿 ذكر دائم واستقامة",    "desc": "أداء 175 صلاة أو ذِكراً",          "pts": 680, "prayer_total": 175},
    {"id": "b_prayer_17", "cat": "prayer", "title": "👑 مائتان صلاة مباركة",    "desc": "أداء 200 صلاة أو ذِكراً إجمالاً",  "pts": 800, "prayer_total": 200},
    {"id": "b_prayer_18", "cat": "prayer", "title": "✨ 250 صلاة وذِكر",        "desc": "أداء 250 صلاة أو ذِكراً",          "pts": 1000,"prayer_total": 250},
    {"id": "b_prayer_19", "cat": "prayer", "title": "🎯 ثلاثمائة صلاة",       "desc": "أداء 300 صلاة أو ذِكراً",          "pts": 1200,"prayer_total": 300},
    {"id": "b_prayer_20", "cat": "prayer", "title": "🚀 350 صلاة مباركة",      "desc": "أداء 350 صلاة أو ذِكراً",          "pts": 1400,"prayer_total": 350},
    {"id": "b_prayer_21", "cat": "prayer", "title": "💎 أربعمائة صلاة وذِكر",   "desc": "أداء 400 صلاة أو ذِكراً",          "pts": 1600,"prayer_total": 400},
    {"id": "b_prayer_22", "cat": "prayer", "title": "🏆 خمسمائة صلاة مباركة",   "desc": "أداء 500 صلاة أو ذِكراً إجمالاً",  "pts": 2000,"prayer_total": 500},
    {"id": "b_prayer_23", "cat": "prayer", "title": "🌟 ستماثية صلاة وذِكر",    "desc": "أداء 600 صلاة أو ذِكراً",          "pts": 2500,"prayer_total": 600},
    {"id": "b_prayer_24", "cat": "prayer", "title": "🕌 سبعمائة صلاة مباركة",   "desc": "أداء 700 صلاة أو ذِكراً",          "pts": 3000,"prayer_total": 700},
    {"id": "b_prayer_25", "cat": "prayer", "title": "📿 ثمانمائة صلاة وذِكر",   "desc": "أداء 800 صلاة أو ذِكراً",          "pts": 3600,"prayer_total": 800},
    {"id": "b_prayer_26", "cat": "prayer", "title": "✨ تسعمائة صلاة",        "desc": "أداء 900 صلاة أو ذِكراً",          "pts": 4200,"prayer_total": 900},
    {"id": "b_prayer_27", "cat": "prayer", "title": "👑 ألف صلاة مباركة",      "desc": "أداء 1000 صلاة أو ذِكراً إجمالاً", "pts": 5000,"prayer_total": 1000},
    {"id": "b_prayer_28", "cat": "prayer", "title": "🏆 1250 صلاة وذِكر",       "desc": "أداء 1250 صلاة أو ذِكراً",         "pts": 6500,"prayer_total": 1250},
    {"id": "b_prayer_29", "cat": "prayer", "title": "💎 1500 صلاة مباركة",     "desc": "أداء 1500 صلاة أو ذِكراً",         "pts": 8000,"prayer_total": 1500},
    {"id": "b_prayer_30", "cat": "prayer", "title": "👑 ألفا صلاة وذِكر (نور الإيمان)","desc": "أداء 2000 صلاة أو ذِكراً","pts": 11000,"prayer_total": 2000},

    # ─────────────────────────────────────────────────────────────────────────
    # 📋 6. قسم المهام والتنظيم (30 وسام) - مرتبة من مهمة واحدة إلى 1500 مهمة
    # ─────────────────────────────────────────────────────────────────────────
    {"id": "b_tasks_1",  "cat": "tasks", "title": "📝 أول مهمة مكتملة",       "desc": "إكمال مهمة يومية واحدة",           "pts": 10,  "tasks_done": 1},
    {"id": "b_tasks_2",  "cat": "tasks", "title": "✅ تنظيم اليوم",            "desc": "إكمال 3 مهام يومية",               "pts": 20,  "tasks_done": 3},
    {"id": "b_tasks_3",  "cat": "tasks", "title": "🎯 منجز اليوم",            "desc": "إكمال 5 مهام في يوم واحد",         "pts": 35,  "tasks_done": 5},
    {"id": "b_tasks_4",  "cat": "tasks", "title": "⚡ إنجاز سريع",            "desc": "إكمال 8 مهام إجمالاً",             "pts": 50,  "tasks_total": 8},
    {"id": "b_tasks_5",  "cat": "tasks", "title": "🚀 عشر مهام مكتملة",       "desc": "إكمال 10 مهام إجمالاً",            "pts": 70,  "tasks_total": 10},
    {"id": "b_tasks_6",  "cat": "tasks", "title": "💡 تنظيم مستمر",           "desc": "إكمال 15 مهمة إجمالاً",            "pts": 90,  "tasks_total": 15},
    {"id": "b_tasks_7",  "cat": "tasks", "title": "📋 عشرون مهمة",            "desc": "إكمال 20 مهمة إجمالاً",            "pts": 120, "tasks_total": 20},
    {"id": "b_tasks_8",  "cat": "tasks", "title": "✨ منجز الأهداف",          "desc": "إكمال 25 مهمة إجمالاً",            "pts": 150, "tasks_total": 25},
    {"id": "b_tasks_9",  "cat": "tasks", "title": "🏆 ثلاثون مهمة مكتملة",    "desc": "إكمال 30 مهمة إجمالاً",            "pts": 180, "tasks_total": 30},
    {"id": "b_tasks_10", "cat": "tasks", "title": "💎 أربعون مهمة",           "desc": "إكمال 40 مهمة إجمالاً",            "pts": 220, "tasks_total": 40},
    {"id": "b_tasks_11", "cat": "tasks", "title": "🎯 خمسون مهمة مكتملة",    "desc": "إكمال 50 مهمة إجمالاً",            "pts": 270, "tasks_total": 50},
    {"id": "b_tasks_12", "cat": "tasks", "title": "🚀 ستون مهمة",            "desc": "إكمال 60 مهمة إجمالاً",            "pts": 320, "tasks_total": 60},
    {"id": "b_tasks_13", "cat": "tasks", "title": "✨ آلة التنظيم",           "desc": "إكمال 80 مهمة إجمالاً",            "pts": 400, "tasks_total": 80},
    {"id": "b_tasks_14", "cat": "tasks", "title": "👑 مائة مهمة إجمالاً",        "desc": "إكمال 100 مهمة إجمالاً",           "pts": 500, "tasks_total": 100},
    {"id": "b_tasks_15", "cat": "tasks", "title": "📋 125 مهمة مكتملة",        "desc": "إكمال 125 مهمة إجمالاً",           "pts": 600, "tasks_total": 125},
    {"id": "b_tasks_16", "cat": "tasks", "title": "💎 قاهر المهام",           "desc": "إكمال 150 مهمة إجمالاً",           "pts": 750, "tasks_total": 150},
    {"id": "b_tasks_17", "cat": "tasks", "title": "🌟 175 مهمة",               "desc": "إكمال 175 مهمة إجمالاً",           "pts": 900, "tasks_total": 175},
    {"id": "b_tasks_18", "cat": "tasks", "title": "🏆 مائتان مهمة مكتملة",    "desc": "إكمال 200 مهمة إجمالاً",           "pts": 1000,"tasks_total": 200},
    {"id": "b_tasks_19", "cat": "tasks", "title": "🎯 قناص الأهداف",          "desc": "إكمال 250 مهمة إجمالاً",           "pts": 1250,"tasks_total": 250},
    {"id": "b_tasks_20", "cat": "tasks", "title": "⚡ ثلاثمائة مهمة",       "desc": "إكمال 300 مهمة إجمالاً",           "pts": 1500,"tasks_total": 300},
    {"id": "b_tasks_21", "cat": "tasks", "title": "🚀 350 مهمة مكتملة",        "desc": "إكمال 350 مهمة إجمالاً",           "pts": 1750,"tasks_total": 350},
    {"id": "b_tasks_22", "cat": "tasks", "title": "✨ أربعمائة مهمة",          "desc": "إكمال 400 مهمة إجمالاً",           "pts": 2000,"tasks_total": 400},
    {"id": "b_tasks_23", "cat": "tasks", "title": "💎 خبير التنظيم",           "desc": "إكمال 450 مهمة إجمالاً",           "pts": 2300,"tasks_total": 450},
    {"id": "b_tasks_24", "cat": "tasks", "title": "👑 خمسمائة مهمة مكتملة",    "desc": "إكمال 500 مهمة إجمالاً",           "pts": 2700,"tasks_total": 500},
    {"id": "b_tasks_25", "cat": "tasks", "title": "🏆 ستماثية مهمة",           "desc": "إكمال 600 مهمة إجمالاً",           "pts": 3300,"tasks_total": 600},
    {"id": "b_tasks_26", "cat": "tasks", "title": "🌟 سبعمائة مهمة",          "desc": "إكمال 700 مهمة إجمالاً",           "pts": 4000,"tasks_total": 700},
    {"id": "b_tasks_27", "cat": "tasks", "title": "⚡ ثمانمائة مهمة",          "desc": "إكمال 800 مهمة إجمالاً",           "pts": 4800,"tasks_total": 800},
    {"id": "b_tasks_28", "cat": "tasks", "title": "💎 تسعمائة مهمة",          "desc": "إكمال 900 مهمة إجمالاً",           "pts": 5600,"tasks_total": 900},
    {"id": "b_tasks_29", "cat": "tasks", "title": "👑 ألف مهمة مكتملة",        "desc": "إكمال 1000 مهمة إجمالاً",          "pts": 7000,"tasks_total": 1000},
    {"id": "b_tasks_30", "cat": "tasks", "title": "👑 1500 مهمة (ملك الإنجاز)","desc": "إكمال 1500 مهمة إجمالاً",          "pts": 10000,"tasks_total": 1500},

    # ─────────────────────────────────────────────────────────────────────────
    # ⚡ 7. قسم النقاط والإنجاز الشامل (20 وسام) - مرتبة من 100 إلى 500,000 نقطة
    # ─────────────────────────────────────────────────────────────────────────
    {"id": "b_score_1",  "cat": "score", "title": "🌱 أول 100 نقطة",          "desc": "جمع 100 نقطة خبرة",               "pts": 0,   "score_min": 100},
    {"id": "b_score_2",  "cat": "score", "title": "⚡ ثلاثمائة نقطة",          "desc": "جمع 300 نقطة خبرة",               "pts": 0,   "score_min": 300},
    {"id": "b_score_3",  "cat": "score", "title": "🎯 خمسمائة نقطة",          "desc": "جمع 500 نقطة خبرة",               "pts": 0,   "score_min": 500},
    {"id": "b_score_4",  "cat": "score", "title": "🚀 ألف نقطة إجمالاً",       "desc": "جمع 1000 نقطة خبرة",              "pts": 0,   "score_min": 1000},
    {"id": "b_score_5",  "cat": "score", "title": "💡 ألفان نقطة",            "desc": "جمع 2000 نقطة خبرة",              "pts": 0,   "score_min": 2000},
    {"id": "b_score_6",  "cat": "score", "title": "✨ 3500 نقطة",             "desc": "جمع 3500 نقطة خبرة",              "pts": 0,   "score_min": 3500},
    {"id": "b_score_7",  "cat": "score", "title": "🏆 خمسة آلاف نقطة",         "desc": "جمع 5000 نقطة خبرة",              "pts": 0,   "score_min": 5000},
    {"id": "b_score_8",  "cat": "score", "title": "💎 سبعة آلاف وخمسمائة",     "desc": "جمع 7500 نقطة خبرة",              "pts": 0,   "score_min": 7500},
    {"id": "b_score_9",  "cat": "score", "title": "👑 عشرة آلاف نقطة",         "desc": "جمع 10000 نقطة خبرة",             "pts": 0,   "score_min": 10000},
    {"id": "b_score_10", "cat": "score", "title": "🌟 خمسة عشر ألف نقطة",     "desc": "جمع 15000 نقطة خبرة",             "pts": 0,   "score_min": 15000},
    {"id": "b_score_11", "cat": "score", "title": "⚡ عشرون ألف نقطة",        "desc": "جمع 20000 نقطة خبرة",             "pts": 0,   "score_min": 20000},
    {"id": "b_score_12", "cat": "score", "title": "🚀 ثلاثون ألف نقطة",       "desc": "جمع 30000 نقطة خبرة",             "pts": 0,   "score_min": 30000},
    {"id": "b_score_13", "cat": "score", "title": "💎 أربعون ألف نقطة",       "desc": "جمع 40000 نقطة خبرة",             "pts": 0,   "score_min": 40000},
    {"id": "b_score_14", "cat": "score", "title": "👑 خمسون ألف نقطة",        "desc": "جمع 50000 نقطة خبرة",             "pts": 0,   "score_min": 50000},
    {"id": "b_score_15", "cat": "score", "title": "🏆 سبعون ألف نقطة",        "desc": "جمع 75000 نقطة خبرة",             "pts": 0,   "score_min": 75000},
    {"id": "b_score_16", "cat": "score", "title": "🌌 مائة ألف نقطة",         "desc": "جمع 100000 نقطة خبرة",            "pts": 0,   "score_min": 100000},
    {"id": "b_score_17", "cat": "score", "title": "✨ 150,000 نقطة",          "desc": "جمع 150000 نقطة خبرة",            "pts": 0,   "score_min": 150000},
    {"id": "b_score_18", "cat": "score", "title": "💎 200,000 نقطة",          "desc": "جمع 200000 نقطة خبرة",            "pts": 0,   "score_min": 200000},
    {"id": "b_score_19", "cat": "score", "title": "👑 300,000 نقطة",          "desc": "جمع 300000 نقطة خبرة",            "pts": 0,   "score_min": 300000},
    {"id": "b_score_20", "cat": "score", "title": "👑 نصف مليون نقطة (القمة)","desc": "جمع 500000 نقطة (قمة المجد والإنتاجية)","pts": 0,"score_min": 500000},
]


def get_badge_progress_info(badge, current_stats):
    """
    تستخرج النسبة المئوية والتقدم الحالي والمطلوب والوحدة والمتبقي لكل وسام.
    """
    target = 0
    curr = 0
    unit = ""

    if "learn_day" in badge:
        target = badge["learn_day"]
        curr = current_stats.get("l_min", 0)
        unit = "دقيقة"
    elif "learn_total" in badge:
        target = badge["learn_total"]
        curr = current_stats.get("l_total", 0)
        unit = "دقيقة"
    elif "streak_min" in badge:
        target = badge["streak_min"]
        curr = current_stats.get("streak_days", 0)
        unit = "يوم"
    elif "water_min" in badge:
        target = badge["water_min"]
        curr = current_stats.get("w_cnt", 0)
        unit = "كوب"
    elif "water_total" in badge:
        target = badge["water_total"]
        curr = current_stats.get("w_total", 0)
        unit = "كوب"
    elif "pushups_min" in badge:
        target = badge["pushups_min"]
        curr = current_stats.get("p_cnt", 0)
        unit = "ضغطة"
    elif "pushups_total" in badge:
        target = badge["pushups_total"]
        curr = current_stats.get("p_total", 0)
        unit = "ضغطة"
    elif "prayer_total" in badge:
        target = badge["prayer_total"]
        curr = current_stats.get("prayer_total", 0)
        unit = "صلاة/ذِكر"
    elif "tasks_done" in badge:
        target = badge["tasks_done"]
        curr = current_stats.get("t_done", 0)
        unit = "مهمة"
    elif "tasks_total" in badge:
        target = badge["tasks_total"]
        curr = current_stats.get("t_total", 0)
        unit = "مهمة"
    elif "score_min" in badge:
        target = badge["score_min"]
        curr = current_stats.get("score", 0)
        unit = "نقطة"

    pct = min(100, int((curr / target) * 100)) if target > 0 else 100
    rem = max(0, target - curr)
    return curr, target, unit, pct, rem
