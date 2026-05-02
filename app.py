"""
Экспертная система оценки стоимости веб-проектов
Прототип для производственной практики
Университет «Синергия» (synergy.ru)

Запуск: python3 app.py
Откроется: http://localhost:5001
"""

from flask import Flask, render_template_string, request, jsonify
from knowledge_base import (
    PROJECT_TYPES, DESIGN_LEVELS, PAGE_RANGES,
    INTEGRATIONS, HOSTING_OPTIONS, MOBILE_OPTIONS,
    COMPLEXITY_LEVELS, evaluate
)

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Экспертная система оценки веб-проектов</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a; color: #e5e5e5; min-height: 100vh;
        }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }

        header {
            text-align: center; padding: 40px 0 30px;
            border-bottom: 1px solid #222;
            margin-bottom: 30px;
        }
        header h1 { font-size: 28px; color: #FFD60A; margin-bottom: 8px; }
        header p { color: #8e8e93; font-size: 14px; }
        header .badge {
            display: inline-block; background: #1c1c1e; border: 1px solid #333;
            padding: 4px 12px; border-radius: 12px; font-size: 12px; color: #FFD60A;
            margin-top: 10px;
        }

        .step { display: none; }
        .step.active { display: block; }
        .step h2 { font-size: 20px; margin-bottom: 6px; color: #fff; }
        .step .step-desc { color: #8e8e93; font-size: 14px; margin-bottom: 20px; }
        .step-counter {
            font-size: 12px; color: #636366; text-transform: uppercase;
            letter-spacing: 1px; margin-bottom: 12px;
        }

        .options { display: grid; gap: 10px; }
        .option-card {
            background: #1c1c1e; border: 2px solid transparent; border-radius: 12px;
            padding: 16px 18px; cursor: pointer; transition: all 0.2s;
        }
        .option-card:hover { border-color: #333; background: #222; }
        .option-card.selected { border-color: #FFD60A; background: #1a1800; }
        .option-card .name { font-size: 16px; font-weight: 500; }
        .option-card .detail { font-size: 13px; color: #8e8e93; margin-top: 4px; }

        .checkbox-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .checkbox-card {
            background: #1c1c1e; border: 2px solid transparent; border-radius: 10px;
            padding: 12px 14px; cursor: pointer; transition: all 0.2s;
        }
        .checkbox-card:hover { border-color: #333; }
        .checkbox-card.selected { border-color: #FFD60A; background: #1a1800; }
        .checkbox-card .name { font-size: 14px; }
        .checkbox-card .cost { font-size: 12px; color: #FFD60A; margin-top: 2px; }

        .nav-buttons {
            display: flex; justify-content: space-between; margin-top: 24px; gap: 12px;
        }
        .btn {
            padding: 12px 28px; border-radius: 10px; border: none; cursor: pointer;
            font-size: 15px; font-weight: 600; transition: all 0.2s;
        }
        .btn-back { background: #2c2c2e; color: #e5e5e5; }
        .btn-back:hover { background: #3a3a3c; }
        .btn-next { background: #FFD60A; color: #000; margin-left: auto; }
        .btn-next:hover { background: #ffe04a; }
        .btn-next:disabled { background: #333; color: #666; cursor: not-allowed; }

        /* Results */
        .results { animation: fadeIn 0.5s; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; } }

        .result-hero {
            background: linear-gradient(135deg, #1a1800 0%, #0d0d00 100%);
            border: 1px solid #FFD60A33; border-radius: 16px;
            padding: 32px; text-align: center; margin-bottom: 24px;
        }
        .result-hero .cost {
            font-size: 42px; font-weight: 700; color: #FFD60A;
            margin-bottom: 4px;
        }
        .result-hero .days { font-size: 18px; color: #e5e5e5; }
        .result-hero .team { font-size: 14px; color: #8e8e93; margin-top: 12px; }

        .section-card {
            background: #1c1c1e; border-radius: 12px; padding: 20px;
            margin-bottom: 16px;
        }
        .section-card h3 {
            font-size: 16px; color: #FFD60A; margin-bottom: 12px;
            padding-bottom: 8px; border-bottom: 1px solid #2c2c2e;
        }
        .detail-row {
            display: flex; justify-content: space-between; padding: 6px 0;
            font-size: 14px; border-bottom: 1px solid #1a1a1a;
        }
        .detail-row:last-child { border-bottom: none; }
        .detail-row .label { color: #8e8e93; }
        .detail-row .value { color: #e5e5e5; font-weight: 500; }

        .rule-card {
            background: #111; border-left: 3px solid #FFD60A;
            padding: 12px 16px; margin-bottom: 8px; border-radius: 0 8px 8px 0;
        }
        .rule-card .rule-name { font-size: 13px; color: #FFD60A; font-weight: 600; margin-bottom: 4px; }
        .rule-card .rule-text { font-size: 13px; color: #aaa; line-height: 1.5; }

        .btn-restart {
            display: block; width: 100%; padding: 14px;
            background: #2c2c2e; color: #FFD60A; border: 1px solid #FFD60A33;
            border-radius: 10px; font-size: 15px; font-weight: 600;
            cursor: pointer; text-align: center; margin-top: 20px;
        }
        .btn-restart:hover { background: #1a1800; }

        .progress-bar {
            height: 3px; background: #1c1c1e; border-radius: 2px;
            margin-bottom: 24px; overflow: hidden;
        }
        .progress-fill {
            height: 100%; background: #FFD60A; border-radius: 2px;
            transition: width 0.3s;
        }

        footer { text-align: center; padding: 30px 0; color: #636366; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Экспертная система</h1>
            <p>Оценка стоимости и сроков разработки веб-проектов</p>
            <span class="badge">Knowledge-Based System</span>
        </header>

        <div class="progress-bar"><div class="progress-fill" id="progress" style="width: 0%"></div></div>

        <form id="expertForm">
            <!-- Step 1: Project Type -->
            <div class="step active" data-step="1">
                <div class="step-counter">Шаг 1 из 6</div>
                <h2>Тип проекта</h2>
                <p class="step-desc">Выберите тип разрабатываемого продукта</p>
                <div class="options" id="projectTypes"></div>
                <div class="nav-buttons">
                    <div></div>
                    <button type="button" class="btn btn-next" onclick="nextStep()" disabled>Далее</button>
                </div>
            </div>

            <!-- Step 2: Design -->
            <div class="step" data-step="2">
                <div class="step-counter">Шаг 2 из 6</div>
                <h2>Уровень дизайна</h2>
                <p class="step-desc">Определите требования к визуальному оформлению</p>
                <div class="options" id="designLevels"></div>
                <div class="nav-buttons">
                    <button type="button" class="btn btn-back" onclick="prevStep()">Назад</button>
                    <button type="button" class="btn btn-next" onclick="nextStep()" disabled>Далее</button>
                </div>
            </div>

            <!-- Step 3: Pages -->
            <div class="step" data-step="3">
                <div class="step-counter">Шаг 3 из 6</div>
                <h2>Объём проекта</h2>
                <p class="step-desc">Количество уникальных страниц или экранов</p>
                <div class="options" id="pageRanges"></div>
                <div class="nav-buttons">
                    <button type="button" class="btn btn-back" onclick="prevStep()">Назад</button>
                    <button type="button" class="btn btn-next" onclick="nextStep()" disabled>Далее</button>
                </div>
            </div>

            <!-- Step 4: Complexity + Mobile -->
            <div class="step" data-step="4">
                <div class="step-counter">Шаг 4 из 6</div>
                <h2>Сложность и мобильная версия</h2>
                <p class="step-desc">Оцените техническую сложность проекта</p>
                <h3 style="font-size:15px; color:#8e8e93; margin: 16px 0 8px;">Сложность:</h3>
                <div class="options" id="complexityLevels"></div>
                <h3 style="font-size:15px; color:#8e8e93; margin: 16px 0 8px;">Мобильная версия:</h3>
                <div class="options" id="mobileOptions"></div>
                <div class="nav-buttons">
                    <button type="button" class="btn btn-back" onclick="prevStep()">Назад</button>
                    <button type="button" class="btn btn-next" onclick="nextStep()" disabled>Далее</button>
                </div>
            </div>

            <!-- Step 5: Integrations -->
            <div class="step" data-step="5">
                <div class="step-counter">Шаг 5 из 6</div>
                <h2>Интеграции</h2>
                <p class="step-desc">Выберите необходимые интеграции (можно несколько)</p>
                <div class="checkbox-grid" id="integrations"></div>
                <div class="nav-buttons">
                    <button type="button" class="btn btn-back" onclick="prevStep()">Назад</button>
                    <button type="button" class="btn btn-next" onclick="nextStep()">Далее</button>
                </div>
            </div>

            <!-- Step 6: Hosting -->
            <div class="step" data-step="6">
                <div class="step-counter">Шаг 6 из 6</div>
                <h2>Хостинг</h2>
                <p class="step-desc">Выберите тип размещения проекта</p>
                <div class="options" id="hostingOptions"></div>
                <div class="nav-buttons">
                    <button type="button" class="btn btn-back" onclick="prevStep()">Назад</button>
                    <button type="button" class="btn btn-next" onclick="submitForm()" disabled>Рассчитать стоимость</button>
                </div>
            </div>
        </form>

        <!-- Results -->
        <div class="step results" data-step="7" id="resultsSection"></div>

        <footer>
            Экспертная система оценки стоимости веб-проектов, 2026<br>
            Прототип разработан в рамках производственной практики (Университет «Синергия»)
        </footer>
    </div>

    <script>
        const data = {{ data | tojson }};
        let currentStep = 1;
        let selections = { integrations: [] };

        function renderOptions(containerId, options, field) {
            const container = document.getElementById(containerId);
            container.innerHTML = '';
            for (const [key, val] of Object.entries(options)) {
                const card = document.createElement('div');
                card.className = 'option-card';
                card.dataset.value = key;
                let detail = '';
                if (val.base_cost) detail = `от ${val.base_cost.toLocaleString('ru-RU')} руб., ~${val.base_days} дней`;
                else if (val.multiplier !== undefined) detail = val.multiplier === 1 ? 'Базовый' : `x${val.multiplier}`;
                else if (val.monthly !== undefined) detail = `${val.monthly.toLocaleString('ru-RU')} руб./мес`;
                card.innerHTML = `<div class="name">${val.name}</div><div class="detail">${detail}</div>`;
                card.onclick = () => selectOption(containerId, key, field, card);
                container.appendChild(card);
            }
        }

        function renderCheckboxes(containerId, options) {
            const container = document.getElementById(containerId);
            container.innerHTML = '';
            for (const [key, val] of Object.entries(options)) {
                const card = document.createElement('div');
                card.className = 'checkbox-card';
                card.dataset.value = key;
                card.innerHTML = `<div class="name">${val.name}</div><div class="cost">+${val.cost.toLocaleString('ru-RU')} руб.</div>`;
                card.onclick = () => toggleCheckbox(key, card);
                container.appendChild(card);
            }
        }

        function selectOption(containerId, value, field, card) {
            document.querySelectorAll(`#${containerId} .option-card`).forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            selections[field] = value;
            updateNextButton();
        }

        function toggleCheckbox(key, card) {
            card.classList.toggle('selected');
            if (selections.integrations.includes(key)) {
                selections.integrations = selections.integrations.filter(k => k !== key);
            } else {
                selections.integrations.push(key);
            }
        }

        function updateNextButton() {
            const step = document.querySelector(`.step[data-step="${currentStep}"]`);
            const btn = step.querySelector('.btn-next');
            if (!btn) return;
            if (currentStep === 4) {
                btn.disabled = !selections.complexity || !selections.mobile;
            } else if (currentStep === 5) {
                btn.disabled = false;
            } else {
                const fields = { 1: 'project_type', 2: 'design', 3: 'pages', 6: 'hosting' };
                btn.disabled = !selections[fields[currentStep]];
            }
        }

        function nextStep() {
            document.querySelector(`.step[data-step="${currentStep}"]`).classList.remove('active');
            currentStep++;
            document.querySelector(`.step[data-step="${currentStep}"]`).classList.add('active');
            document.getElementById('progress').style.width = ((currentStep - 1) / 6 * 100) + '%';
            updateNextButton();
        }

        function prevStep() {
            document.querySelector(`.step[data-step="${currentStep}"]`).classList.remove('active');
            currentStep--;
            document.querySelector(`.step[data-step="${currentStep}"]`).classList.add('active');
            document.getElementById('progress').style.width = ((currentStep - 1) / 6 * 100) + '%';
        }

        async function submitForm() {
            const res = await fetch('/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(selections),
            });
            const result = await res.json();
            showResults(result);
        }

        function showResults(r) {
            document.querySelector(`.step[data-step="${currentStep}"]`).classList.remove('active');
            currentStep = 7;
            document.getElementById('progress').style.width = '100%';

            const rulesHtml = r.applied_rules.length > 0
                ? r.applied_rules.map(rule => `
                    <div class="rule-card">
                        <div class="rule-name">${rule.name}</div>
                        <div class="rule-text">${rule.explanation}</div>
                    </div>
                `).join('')
                : '<p style="color:#636366">Специальные правила не были применены.</p>';

            const integrationsHtml = r.integration_details.length > 0
                ? r.integration_details.map(d => `<div class="detail-row"><span class="label">${d.split(':')[0]}</span><span class="value">${d.split(':')[1]}</span></div>`).join('')
                : '<p style="color:#636366;font-size:13px">Интеграции не выбраны</p>';

            document.getElementById('resultsSection').innerHTML = `
                <div class="result-hero">
                    <div class="cost">${r.total_cost.toLocaleString('ru-RU')} руб.</div>
                    <div class="days">Срок реализации: ~${r.total_days} рабочих дней</div>
                    <div class="team">Рекомендуемый состав: ${r.team_recommendation}</div>
                </div>

                <div class="section-card">
                    <h3>Детализация расчёта</h3>
                    <div class="detail-row"><span class="label">Тип проекта</span><span class="value">${r.project_type}</span></div>
                    <div class="detail-row"><span class="label">Базовая стоимость</span><span class="value">${r.cost_breakdown.base.toLocaleString('ru-RU')} руб.</span></div>
                    <div class="detail-row"><span class="label">Множитель дизайна</span><span class="value">x${r.cost_breakdown.design_multiplier}</span></div>
                    <div class="detail-row"><span class="label">Множитель объёма</span><span class="value">x${r.cost_breakdown.pages_multiplier}</span></div>
                    <div class="detail-row"><span class="label">Множитель мобильной версии</span><span class="value">x${r.cost_breakdown.mobile_multiplier}</span></div>
                    <div class="detail-row"><span class="label">Множитель сложности</span><span class="value">x${r.cost_breakdown.complexity_multiplier}</span></div>
                    <div class="detail-row"><span class="label">Интеграции</span><span class="value">+${r.cost_breakdown.integrations.toLocaleString('ru-RU')} руб.</span></div>
                    <div class="detail-row"><span class="label">Настройка хостинга</span><span class="value">+${r.cost_breakdown.hosting_setup.toLocaleString('ru-RU')} руб.</span></div>
                    <div class="detail-row"><span class="label">Модификатор правил</span><span class="value">x${r.cost_breakdown.rules_modifier.toFixed(2)}</span></div>
                    <div class="detail-row"><span class="label">Хостинг (ежемесячно)</span><span class="value">${r.hosting_monthly.toLocaleString('ru-RU')} руб./мес</span></div>
                </div>

                ${r.integration_details.length > 0 ? `
                <div class="section-card">
                    <h3>Интеграции</h3>
                    ${integrationsHtml}
                </div>` : ''}

                <div class="section-card">
                    <h3>Применённые правила (объяснение решения)</h3>
                    ${rulesHtml}
                </div>

                <button class="btn-restart" onclick="location.reload()">Новый расчёт</button>
            `;
            document.getElementById('resultsSection').classList.add('active');
        }

        // Initialize
        renderOptions('projectTypes', data.project_types, 'project_type');
        renderOptions('designLevels', data.design_levels, 'design');
        renderOptions('pageRanges', data.page_ranges, 'pages');
        renderOptions('complexityLevels', data.complexity_levels, 'complexity');
        renderOptions('mobileOptions', data.mobile_options, 'mobile');
        renderOptions('hostingOptions', data.hosting_options, 'hosting');
        renderCheckboxes('integrations', data.integrations);
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    data = {
        "project_types": PROJECT_TYPES,
        "design_levels": DESIGN_LEVELS,
        "page_ranges": PAGE_RANGES,
        "integrations": INTEGRATIONS,
        "hosting_options": HOSTING_OPTIONS,
        "mobile_options": MOBILE_OPTIONS,
        "complexity_levels": COMPLEXITY_LEVELS,
    }
    return render_template_string(HTML_TEMPLATE, data=data)


@app.route('/evaluate', methods=['POST'])
def evaluate_route():
    facts = request.json
    result = evaluate(facts)
    return jsonify(result)


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  Экспертная система оценки стоимости веб-проектов")
    print("  Прототип производственной практики (Университет Синергия)")
    print("=" * 50)
    print("\n  Откройте в браузере: http://localhost:5001\n")
    app.run(debug=True, port=5001)
