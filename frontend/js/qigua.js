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
    if (button.disabled) {
        return;
    }
    button.disabled = true;
    button.setAttribute('aria-busy', 'true');
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
        button.disabled = false;
        button.removeAttribute('aria-busy');
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
    const methods = ['auto', 'manual', 'specify', 'time'];
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

    setStatus('');
    if (method === 'manual') {
        resetManual();
    }
    if (method === 'specify') {
        buildSpecifyPanel();
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
