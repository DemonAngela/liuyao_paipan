let currentMethod = 'auto';
let manualYaos = [];
let currentManualIndex = 0;
let manualSessionId = 0;
let specifyYaos = [];

function setStatus(message = '', type = 'info') {
    const status = document.getElementById('app-status');
    status.textContent = message;
    status.className = `app-status ${type}`;
}

async function runAction(button, loadingMessage, successMessage, action) {
    if (button?.disabled) {
        return;
    }
    if (button) {
        button.disabled = true;
        button.setAttribute('aria-busy', 'true');
    }
    setStatus(loadingMessage, 'loading');
    try {
        const outcome = await action();
        if (outcome?.message) {
            setStatus(outcome.message, outcome.type || 'success');
        } else {
            setStatus(successMessage, 'success');
        }
    } catch (error) {
        setStatus(error.message || '操作失败，请稍后重试', 'error');
    } finally {
        if (button) {
            button.disabled = false;
            button.removeAttribute('aria-busy');
        }
    }
}

function postJson(path, payload) {
    return requestJson(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
}

function initQiguaUI() {
    const methods = ['auto', 'manual', 'specify', 'time', 'ganzhi'];
    methods.forEach(method => {
        document.getElementById(`btn-${method}`).addEventListener(
            'click',
            () => switchMethod(method)
        );
    });

    document.getElementById('btn-start-auto').addEventListener(
        'click',
        autoQigua
    );
    document.getElementById('btn-shake').addEventListener(
        'click',
        manualShake
    );
    document.getElementById('btn-reset-manual').addEventListener(
        'click',
        resetManual
    );
    document.getElementById('btn-start-time').addEventListener(
        'click',
        timeQigua
    );
    document.getElementById('btn-submit-specify').addEventListener(
        'click',
        submitSpecify
    );
    document.getElementById('ganzhi-time-input').addEventListener(
        'change',
        loadGanzhiSummary
    );

    initGanzhiCalendar();
    document.getElementById('specify-yao-list').addEventListener(
        'click',
        handleSpecifySelection
    );

    buildSpecifyPanel();
    switchMethod('auto');
}

function switchMethod(method) {
    currentMethod = method;
    document.querySelectorAll('.method-btn').forEach(button => {
        const isActive = button.id === `btn-${method}`;
        button.classList.toggle('active', isActive);
        button.setAttribute('aria-pressed', String(isActive));
    });

    document.getElementById('auto-options').classList.toggle(
        'hidden',
        method !== 'auto'
    );
    document.getElementById('manual-panel').classList.toggle(
        'hidden',
        method !== 'manual'
    );
    document.getElementById('specify-panel').classList.toggle(
        'hidden',
        method !== 'specify'
    );
    document.getElementById('time-options').classList.toggle(
        'hidden',
        method !== 'time'
    );
    document.getElementById('ganzhi-panel').classList.toggle(
        'hidden',
        method !== 'ganzhi'
    );

    setStatus('');
    if (method === 'manual') {
        resetManual();
    }
    if (method === 'specify') {
        buildSpecifyPanel();
    }
    if (method === 'ganzhi') {
        loadGanzhiSummary();
    }
}

async function autoQigua() {
    const button = document.getElementById('btn-start-auto');
    await runAction(button, '正在自动起卦…', '排盘完成', async () => {
        const qiguaData = await requestJson('/api/qigua/auto', {
            method: 'POST'
        });
        return requestPaipan(qiguaData);
    });
}

async function timeQigua() {
    const button = document.getElementById('btn-start-time');
    await runAction(button, '正在按时间起卦…', '排盘完成', async () => {
        const qiguaData = await postJson('/api/qigua/time', {
            method: 'time',
            ...readLocalDateTime('time-input')
        });
        return requestPaipan(qiguaData);
    });
}

async function loadGanzhiSummary() {
    const input = document.getElementById('ganzhi-time-input');
    const hasCustomTime = Boolean(input.value);
    await runAction(
        null,
        hasCustomTime ? '正在查询所选时间…' : '正在查询今日干支…',
        hasCustomTime ? '所选时间历法已更新' : '今日历法已更新',
        async () => {
            const data = hasCustomTime
                ? await postJson(
                    '/api/ganzhi/query',
                    readLocalDateTime('ganzhi-time-input')
                )
                : await requestJson('/api/ganzhi/today');
            document.getElementById('today-ganzhi').textContent = data.ganzhi;
            document.getElementById('today-solar').textContent = data.solar;
            document.getElementById('today-lunar').textContent = data.lunar;
        }
    );
}

function initGanzhiCalendar() {
    const input = document.getElementById('ganzhi-time-input');
    const calendar = document.getElementById('ganzhi-calendar');
    const wrap = input.closest('.ganzhi-picker-wrap');
    const overlay = wrap.querySelector('.ganzhi-picker-overlay');
    const pad = value => String(value).padStart(2, '0');
    const formatDate = (year, month, day) =>
        `${year}-${pad(month + 1)}-${pad(day)}`;
    const now = new Date();
    let viewYear = now.getFullYear();
    let viewMonth = now.getMonth();
    let selectedDate = null;

    function parseInputDate() {
        if (!input.value) {
            return null;
        }
        const parsed = new Date(input.value);
        return Number.isNaN(parsed.getTime()) ? null : parsed;
    }

    function applyInputValue(value) {
        input.value = value;
        input.dispatchEvent(new Event('change'));
    }

    function currentDateKey() {
        if (selectedDate) {
            return selectedDate;
        }
        const parsed = parseInputDate();
        if (parsed) {
            return formatDate(
                parsed.getFullYear(), parsed.getMonth(), parsed.getDate()
            );
        }
        return formatDate(
            now.getFullYear(), now.getMonth(), now.getDate()
        );
    }

    function applySelection() {
        const timePart = document.getElementById('ganzhi-time-part');
        applyInputValue(`${currentDateKey()}T${timePart?.value || '00:00'}`);
    }

    function buildHeader() {
        const header = document.createElement('div');
        header.className = 'ganzhi-cal-header';
        const title = document.createElement('span');
        title.textContent = `${viewYear}年${viewMonth + 1}月`;
        const prevBtn = document.createElement('button');
        prevBtn.type = 'button';
        prevBtn.id = 'ganzhi-cal-prev';
        prevBtn.className = 'ganzhi-cal-nav';
        prevBtn.textContent = '‹';
        prevBtn.setAttribute('aria-label', '上一月');
        const nextBtn = document.createElement('button');
        nextBtn.type = 'button';
        nextBtn.id = 'ganzhi-cal-next';
        nextBtn.className = 'ganzhi-cal-nav';
        nextBtn.textContent = '›';
        nextBtn.setAttribute('aria-label', '下一月');
        header.append(prevBtn, title, nextBtn);
        return header;
    }

    function buildGrid() {
        const today = new Date();
        const todayKey = formatDate(
            today.getFullYear(), today.getMonth(), today.getDate()
        );
        const selectedKey = currentDateKey();
        const grid = document.createElement('div');
        grid.className = 'ganzhi-cal-grid';
        ['一', '二', '三', '四', '五', '六', '日'].forEach(name => {
            const cell = document.createElement('span');
            cell.className = 'ganzhi-cal-weekday';
            cell.textContent = name;
            grid.appendChild(cell);
        });

        const leadDays = (new Date(viewYear, viewMonth, 1).getDay() + 6) % 7;
        const prevMonthDays = new Date(viewYear, viewMonth, 0).getDate();
        const cells = [];
        for (let i = leadDays; i > 0; i -= 1) {
            cells.push({ day: prevMonthDays - i + 1, shift: -1 });
        }
        for (
            let day = 1;
            day <= new Date(viewYear, viewMonth + 1, 0).getDate();
            day += 1
        ) {
            cells.push({ day, shift: 0 });
        }
        let trailing = 1;
        while (cells.length < 42) {
            cells.push({ day: trailing, shift: 1 });
            trailing += 1;
        }

        cells.forEach(cell => {
            const cellDate = new Date(
                viewYear, viewMonth + cell.shift, cell.day
            );
            const key = formatDate(
                cellDate.getFullYear(), cellDate.getMonth(), cellDate.getDate()
            );
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'ganzhi-cal-day';
            btn.textContent = cell.day;
            btn.dataset.date = key;
            btn.setAttribute('aria-label', key);
            if (cell.shift !== 0) {
                btn.classList.add('is-outside');
            }
            if (key === todayKey) {
                btn.classList.add('is-today');
            }
            if (key === selectedKey) {
                btn.classList.add('is-selected');
                btn.setAttribute('aria-pressed', 'true');
            }
            grid.appendChild(btn);
        });
        return grid;
    }

    function buildFooter() {
        const footer = document.createElement('div');
        footer.className = 'ganzhi-cal-footer';
        const timePart = document.createElement('input');
        timePart.type = 'time';
        timePart.id = 'ganzhi-time-part';
        timePart.className = 'ganzhi-cal-time';
        timePart.setAttribute('aria-label', '选择时刻');
        const parsed = parseInputDate();
        timePart.value = parsed
            ? `${pad(parsed.getHours())}:${pad(parsed.getMinutes())}`
            : '00:00';
        const todayBtn = document.createElement('button');
        todayBtn.type = 'button';
        todayBtn.id = 'ganzhi-cal-today';
        todayBtn.className = 'secondary-btn ganzhi-cal-action';
        todayBtn.textContent = '今天';
        const clearBtn = document.createElement('button');
        clearBtn.type = 'button';
        clearBtn.id = 'ganzhi-cal-clear';
        clearBtn.className = 'secondary-btn ganzhi-cal-action';
        clearBtn.textContent = '清空';
        footer.append(timePart, todayBtn, clearBtn);
        return footer;
    }

    function renderCalendar() {
        calendar.replaceChildren(buildHeader(), buildGrid(), buildFooter());
    }

    function shiftMonth(delta) {
        const next = new Date(viewYear, viewMonth + delta, 1);
        viewYear = next.getFullYear();
        viewMonth = next.getMonth();
        renderCalendar();
    }

    function openCalendar() {
        const base = parseInputDate() || new Date();
        viewYear = base.getFullYear();
        viewMonth = base.getMonth();
        renderCalendar();
        calendar.classList.remove('hidden');
        overlay.setAttribute('aria-expanded', 'true');
    }

    function closeCalendar() {
        calendar.classList.add('hidden');
        overlay.setAttribute('aria-expanded', 'false');
    }

    function toggleCalendar() {
        if (calendar.classList.contains('hidden')) {
            openCalendar();
        } else {
            closeCalendar();
        }
    }

    calendar.addEventListener('click', event => {
        const dayBtn = event.target.closest('.ganzhi-cal-day');
        if (dayBtn) {
            selectedDate = dayBtn.dataset.date;
            applySelection();
            renderCalendar();
            return;
        }
        if (event.target.id === 'ganzhi-cal-prev') {
            shiftMonth(-1);
            return;
        }
        if (event.target.id === 'ganzhi-cal-next') {
            shiftMonth(1);
            return;
        }
        if (event.target.id === 'ganzhi-cal-today') {
            const current = new Date();
            selectedDate = formatDate(
                current.getFullYear(), current.getMonth(), current.getDate()
            );
            viewYear = current.getFullYear();
            viewMonth = current.getMonth();
            applyInputValue(
                `${selectedDate}T${pad(current.getHours())}:${
                    pad(current.getMinutes())
                }`
            );
            renderCalendar();
            return;
        }
        if (event.target.id === 'ganzhi-cal-clear') {
            selectedDate = null;
            applyInputValue('');
            renderCalendar();
        }
    });

    calendar.addEventListener('change', event => {
        if (event.target.id === 'ganzhi-time-part') {
            applySelection();
        }
    });

    overlay.addEventListener('click', toggleCalendar);

    document.addEventListener('mousedown', event => {
        if (!calendar.classList.contains('hidden')
            && !wrap.contains(event.target)) {
            closeCalendar();
        }
    });

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape'
            && !calendar.classList.contains('hidden')) {
            closeCalendar();
        }
    });
}

function buildSpecifyPanel() {
    const container = document.getElementById('specify-yao-list');
    const yaoNames = ['上爻', '五爻', '四爻', '三爻', '二爻', '初爻'];
    container.replaceChildren();
    specifyYaos = Array.from(
        { length: 6 },
        () => ({ yinYang: 1, isChanging: false })
    );

    yaoNames.forEach((name, displayIndex) => {
        const actualIndex = 5 - displayIndex;
        const item = document.createElement('div');
        item.className = 'specify-yao-item';
        item.dataset.index = actualIndex;
        item.innerHTML = `
            <span class="yao-label">${name}</span>
            <button type="button" class="yao-value-btn default-selected"
                    data-idx="${actualIndex}" data-type="yang"
                    aria-pressed="true">少阳 ▅▅▅▅▅</button>
            <button type="button" class="yao-value-btn"
                    data-idx="${actualIndex}" data-type="yin"
                    aria-pressed="false">少阴 ▅▅　▅▅</button>
            <button type="button" class="yao-value-btn"
                    data-idx="${actualIndex}" data-type="laoyang"
                    aria-pressed="false">老阳 ○</button>
            <button type="button" class="yao-value-btn"
                    data-idx="${actualIndex}" data-type="laoyin"
                    aria-pressed="false">老阴 ×</button>
        `;
        container.appendChild(item);
    });
}

function handleSpecifySelection(event) {
    const button = event.target.closest('.yao-value-btn');
    if (!button) {
        return;
    }
    const index = Number.parseInt(button.dataset.idx, 10);
    const choices = {
        yang: { yinYang: 1, isChanging: false },
        yin: { yinYang: 0, isChanging: false },
        laoyang: { yinYang: 1, isChanging: true },
        laoyin: { yinYang: 0, isChanging: true }
    };
    const choice = choices[button.dataset.type];
    if (!choice || !Number.isInteger(index) || index < 0 || index > 5) {
        return;
    }
    specifyYaos[index] = choice;

    button.closest('.specify-yao-item')
        .querySelectorAll('.yao-value-btn')
        .forEach(item => {
            const isSelected = item === button;
            item.classList.toggle('default-selected', false);
            item.classList.toggle('active-selected', isSelected);
            item.setAttribute('aria-pressed', String(isSelected));
        });
}

async function submitSpecify() {
    const button = document.getElementById('btn-submit-specify');
    await runAction(button, '正在校验指定卦象…', '排盘完成', async () => {
        const qiguaData = await postJson('/api/qigua/specify', {
            method: 'specify',
            yao_values: specifyYaos.map(yao => yao.yinYang),
            changing_yao: specifyYaos.map(yao => yao.isChanging),
            ...readLocalDateTime('specify-time-input')
        });
        return requestPaipan(qiguaData);
    });
}

async function manualShake() {
    const button = document.getElementById('btn-shake');
    if (currentManualIndex >= 6) {
        setStatus('六爻已完成；如需重摇，请点击“重新开始”。', 'info');
        return;
    }
    const sessionId = manualSessionId;
    await runAction(button, '正在摇卦…', '本爻已完成', async () => {
        const yao = await requestJson('/api/qigua/manual_step', {
            method: 'POST'
        });
        if (sessionId !== manualSessionId || currentMethod !== 'manual') {
            return { message: '本次摇卦已取消。', type: 'info' };
        }
        manualYaos.push(yao);
        currentManualIndex = manualYaos.length;
        updateManualPreview();

        if (currentManualIndex < 6) {
            return {
                message: `已完成第 ${currentManualIndex} 爻。`,
                type: 'success'
            };
        }
        const qiguaData = await postJson(
            '/api/qigua/manual_complete',
            manualYaos
        );
        return await requestPaipan(qiguaData) || {
            message: '排盘完成',
            type: 'success'
        };
    });
}

function resetManual() {
    manualSessionId += 1;
    manualYaos = [];
    currentManualIndex = 0;
    updateManualPreview();
    setStatus('');
}

function updateManualPreview() {
    const names = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻'];
    document.getElementById('current-yao-index').textContent =
        names[currentManualIndex] || '完成';
    document.getElementById('yao-count').textContent = currentManualIndex;
    const preview = document.getElementById('manual-preview');
    preview.replaceChildren(
        ...manualYaos.map((yao, index) => {
            const item = document.createElement('span');
            item.className = 'preview-yao';
            item.textContent = `${names[index]}：${getYinYangSymbol(
                yao.yin_yang,
                yao.is_changing
            )}`;
            return item;
        })
    );
}

async function requestPaipan(qiguaData) {
    const paipanData = await postJson('/api/paipan/', qiguaData);
    return renderPaipan(paipanData);
}

document.addEventListener('DOMContentLoaded', initQiguaUI);
