"""
База знаний экспертной системы оценки стоимости веб-проектов.
Содержит факты и правила для принятия решений.
"""

# ============================================================
# ФАКТЫ: параметры проектов и их весовые коэффициенты
# ============================================================

PROJECT_TYPES = {
    "corporate": {"name": "Корпоративный сайт", "base_cost": 150000, "base_days": 30},
    "landing": {"name": "Лендинг", "base_cost": 50000, "base_days": 10},
    "ecommerce": {"name": "Интернет-магазин", "base_cost": 350000, "base_days": 60},
    "crm": {"name": "CRM-система", "base_cost": 800000, "base_days": 120},
    "portal": {"name": "Веб-портал", "base_cost": 600000, "base_days": 90},
    "mobile": {"name": "Мобильное приложение", "base_cost": 500000, "base_days": 75},
}

DESIGN_LEVELS = {
    "template": {"name": "Шаблонный дизайн", "multiplier": 0.8},
    "standard": {"name": "Стандартный дизайн", "multiplier": 1.0},
    "custom": {"name": "Индивидуальный дизайн", "multiplier": 1.4},
    "premium": {"name": "Премиум дизайн (UI/UX)", "multiplier": 1.8},
}

PAGE_RANGES = {
    "small": {"name": "1-5 страниц", "multiplier": 0.7},
    "medium": {"name": "6-15 страниц", "multiplier": 1.0},
    "large": {"name": "16-40 страниц", "multiplier": 1.4},
    "xlarge": {"name": "40+ страниц", "multiplier": 1.8},
}

INTEGRATIONS = {
    "payment": {"name": "Платёжные системы", "cost": 40000, "days": 7},
    "crm_int": {"name": "Интеграция с CRM", "cost": 60000, "days": 10},
    "erp": {"name": "Интеграция с ERP/1С", "cost": 80000, "days": 14},
    "api": {"name": "REST API для внешних систем", "cost": 50000, "days": 10},
    "sms": {"name": "SMS/Email уведомления", "cost": 20000, "days": 4},
    "analytics": {"name": "Аналитика (Яндекс.Метрика, GA)", "cost": 15000, "days": 2},
}

HOSTING_OPTIONS = {
    "shared": {"name": "Виртуальный хостинг", "monthly": 500, "setup": 5000},
    "vps": {"name": "VPS сервер", "monthly": 2000, "setup": 15000},
    "cloud": {"name": "Облако (Yandex Cloud / Cloud.ru)", "monthly": 5000, "setup": 30000},
    "dedicated": {"name": "Выделенный сервер", "monthly": 15000, "setup": 50000},
}

MOBILE_OPTIONS = {
    "none": {"name": "Без мобильной версии", "multiplier": 1.0},
    "adaptive": {"name": "Адаптивная вёрстка", "multiplier": 1.15},
    "pwa": {"name": "PWA (прогрессивное веб-приложение)", "multiplier": 1.3},
    "native": {"name": "Нативное мобильное приложение", "multiplier": 1.8},
}

COMPLEXITY_LEVELS = {
    "low": {"name": "Низкая (типовой проект)", "multiplier": 0.85},
    "medium": {"name": "Средняя (нестандартная логика)", "multiplier": 1.0},
    "high": {"name": "Высокая (сложная бизнес-логика)", "multiplier": 1.3},
    "enterprise": {"name": "Enterprise (масштабируемость, отказоустойчивость)", "multiplier": 1.6},
}


# ============================================================
# ПРАВИЛА: механизм логического вывода (ЕСЛИ-ТО)
# ============================================================

class Rule:
    """Базовый класс правила экспертной системы."""
    def __init__(self, name, condition, action, explanation):
        self.name = name
        self.condition = condition  # функция проверки
        self.action = action        # функция действия
        self.explanation = explanation  # объяснение для пользователя

RULES = [
    Rule(
        name="R1: Корректировка CRM для enterprise",
        condition=lambda facts: facts.get("project_type") == "crm" and facts.get("complexity") == "enterprise",
        action=lambda facts: {"cost_modifier": 1.3, "days_modifier": 1.2},
        explanation="CRM-система уровня Enterprise требует повышенной отказоустойчивости и масштабируемости, что увеличивает стоимость на 30% и сроки на 20%."
    ),
    Rule(
        name="R2: Скидка на лендинг с шаблоном",
        condition=lambda facts: facts.get("project_type") == "landing" and facts.get("design") == "template",
        action=lambda facts: {"cost_modifier": 0.7, "days_modifier": 0.6},
        explanation="Лендинг на шаблонном дизайне — типовое решение, реализуемое быстрее и дешевле стандартного."
    ),
    Rule(
        name="R3: Увеличение при множественных интеграциях",
        condition=lambda facts: len(facts.get("integrations", [])) >= 3,
        action=lambda facts: {"cost_modifier": 1.15, "days_modifier": 1.1},
        explanation="Три и более интеграций усложняют архитектуру и тестирование, увеличивая стоимость на 15%."
    ),
    Rule(
        name="R4: Премиум-дизайн для портала",
        condition=lambda facts: facts.get("project_type") == "portal" and facts.get("design") == "premium",
        action=lambda facts: {"cost_modifier": 1.2, "days_modifier": 1.15},
        explanation="Премиум UI/UX для портала с большим количеством пользователей требует дополнительных исследований и прототипирования."
    ),
    Rule(
        name="R5: Нативное приложение + интернет-магазин",
        condition=lambda facts: facts.get("project_type") == "ecommerce" and facts.get("mobile") == "native",
        action=lambda facts: {"cost_modifier": 1.4, "days_modifier": 1.3},
        explanation="Нативное мобильное приложение для интернет-магазина — фактически отдельный проект, значительно увеличивающий бюджет."
    ),
    Rule(
        name="R6: Облачный хостинг + высокая сложность",
        condition=lambda facts: facts.get("hosting") in ("cloud", "dedicated") and facts.get("complexity") in ("high", "enterprise"),
        action=lambda facts: {"cost_modifier": 1.1, "days_modifier": 1.05},
        explanation="Сложные проекты на облачной инфраструктуре требуют дополнительной настройки DevOps."
    ),
]


def evaluate(facts):
    """
    Механизм логического вывода (прямая цепочка).
    Принимает факты, применяет правила, возвращает оценку.
    """
    # Базовые расчёты
    project = PROJECT_TYPES[facts["project_type"]]
    design = DESIGN_LEVELS[facts["design"]]
    pages = PAGE_RANGES[facts["pages"]]
    mobile = MOBILE_OPTIONS[facts["mobile"]]
    complexity = COMPLEXITY_LEVELS[facts["complexity"]]
    hosting = HOSTING_OPTIONS[facts["hosting"]]

    base_cost = project["base_cost"]
    base_days = project["base_days"]

    # Применяем множители
    cost = base_cost * design["multiplier"] * pages["multiplier"] * mobile["multiplier"] * complexity["multiplier"]
    days = base_days * pages["multiplier"] * complexity["multiplier"]

    # Добавляем интеграции
    integration_cost = 0
    integration_days = 0
    integration_details = []
    for intg_key in facts.get("integrations", []):
        intg = INTEGRATIONS[intg_key]
        integration_cost += intg["cost"]
        integration_days += intg["days"]
        integration_details.append(f"{intg['name']}: +{intg['cost']:,.0f} руб., +{intg['days']} дней")

    cost += integration_cost
    days += integration_days

    # Хостинг
    hosting_setup = hosting["setup"]
    hosting_monthly = hosting["monthly"]
    cost += hosting_setup

    # Применяем правила (прямой вывод)
    applied_rules = []
    total_cost_mod = 1.0
    total_days_mod = 1.0

    for rule in RULES:
        if rule.condition(facts):
            result = rule.action(facts)
            total_cost_mod *= result.get("cost_modifier", 1.0)
            total_days_mod *= result.get("days_modifier", 1.0)
            applied_rules.append({
                "name": rule.name,
                "explanation": rule.explanation,
                "cost_modifier": result.get("cost_modifier", 1.0),
                "days_modifier": result.get("days_modifier", 1.0),
            })

    cost *= total_cost_mod
    days *= total_days_mod

    # Округление
    cost = round(cost / 1000) * 1000  # до тысяч
    days = round(days)

    return {
        "project_type": project["name"],
        "total_cost": cost,
        "total_days": days,
        "cost_breakdown": {
            "base": project["base_cost"],
            "design_multiplier": design["multiplier"],
            "pages_multiplier": pages["multiplier"],
            "mobile_multiplier": mobile["multiplier"],
            "complexity_multiplier": complexity["multiplier"],
            "integrations": integration_cost,
            "hosting_setup": hosting_setup,
            "rules_modifier": total_cost_mod,
        },
        "hosting_monthly": hosting_monthly,
        "integration_details": integration_details,
        "applied_rules": applied_rules,
        "team_recommendation": get_team_recommendation(cost, days),
    }


def get_team_recommendation(cost, days):
    """Рекомендация по составу команды на основе бюджета и сроков."""
    if cost < 100000:
        return "1 fullstack-разработчик"
    elif cost < 300000:
        return "1 backend + 1 frontend разработчик"
    elif cost < 600000:
        return "2 backend + 1 frontend + 1 QA"
    elif cost < 1000000:
        return "2 backend + 2 frontend + 1 DevOps + 1 QA + PM"
    else:
        return "3+ backend + 2 frontend + 1 мобильный + 1 DevOps + 2 QA + PM + аналитик"
