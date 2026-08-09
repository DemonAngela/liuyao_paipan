// 全局状态
let currentMethod = 'auto';
let manualYaos = [];
let currentManualIndex = 0;
let specifyYaos = [];

function initQiguaUI() {
    document.getElementById('btn-auto').addEventListener('click', () => switchMethod('auto'));
    document.getElementById('btn-manual').addEventListener('click', () => switchMethod('manual'));
    document.getElementById('btn-specify').addEventListener('click', () => switchMethod('specify'));
    document.getElementById('btn-time').addEventListener('click', () => switchMethod('time'));

    document.getElementById('btn-start-auto').addEventListener('click', autoQigua);
    document.getElementById('btn-shake').addEventListener('click', manualShake);
    document.getElementById('btn-reset-manual').addEventListener('click', resetManual);
    document.getElementById('btn-start-time').addEventListener('click', timeQigua);
    document.getElementById('btn-submit-specify').addEventListener('click', submitSpecify);

    buildSpecifyPanel();
    switchMethod('auto');
}

async function fetchJson(url, options = {}) {
    const resp = await fetch(url, options);
    const text = await resp.text();
    let data = null;

    if (text) {
        try {
            data = JSON.parse(text);
        } catch (_) {
            data = null;
        }
    }

    if (!resp.ok) {
        const detail = data && data.detail ? data.detail : (text || `HTTP ${resp.status}`);
        throw new Error(detail);
    }

    return data;
}

function switchMethod(method) {
    currentMethod = method;
    document.querySelectorAll('.method-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`btn-${method}`).classList.add('active');

    document.getElementById('auto-options').classList.toggle('hidden', method !== 'auto');
    document.getElementById('manual-panel').classList.toggle('hidden', method !== 'manual');
    document.getElementById('specify-panel').classList.toggle('hidden', method !== 'specify');
    document.getElementById('time-options').classList.toggle('hidden', method !== 'time');

    if (method === 'manual') resetManual();
    if (method === 'specify') buildSpecifyPanel();
}

async function autoQigua() {
    try {
        const data = await fetchJson(`${API_BASE}/api/qigua/auto`, { method: 'POST' });
        await requestPaipan(data);
    } catch (e) {
        alert('起卦失败：' + e.message);
    }
}

function readTimeInput(elementId) {
    const value = document.getElementById(elementId).value;
    if (!value) return {};

    const dt = new Date(value);
    return {
        year: dt.getFullYear(),
        month: dt.getMonth() + 1,
        day: dt.getDate(),
        hour: dt.getHours()
    };
}

async function timeQigua() {
    try {
        const data = await fetchJson(`${API_BASE}/api/qigua/time`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ method: 'time', ...readTimeInput('time-input') })
        });
        await requestPaipan(data);
    } catch (e) {
        alert('时间起卦失败：' + e.message);
    }
}

// ========== 手工指定 ==========
function buildSpecifyPanel() {
    const container = document.getElementById('specify-yao-list');
    const yaoNames = ['上爻', '五爻', '四爻', '三爻', '二爻', '初爻'];
    container.innerHTML = '';

    specifyYaos = new Array(6).fill(null).map(() => ({ yinYang: 1, isChanging: false }));

    yaoNames.forEach((name, displayIdx) => {
        const actualIdx = 5 - displayIdx;
        const div = document.createElement('div');
        div.className = 'specify-yao-item';
        div.dataset.index = actualIdx;
        div.innerHTML = `
            <span class="yao-label">${name}</span>
            <button class="yao-value-btn" data-idx="${actualIdx}" data-type="yang">少阳 ▅▅▅▅▅</button>
            <button class="yao-value-btn" data-idx="${actualIdx}" data-type="yin">少阴 ▅▅　▅▅</button>
            <button class="yao-value-btn" data-idx="${actualIdx}" data-type="laoyang">老阳 ○</button>
            <button class="yao-value-btn" data-idx="${actualIdx}" data-type="laoyin">老阴 ×</button>
        `;
        container.appendChild(div);
    });

    container.querySelectorAll('.specify-yao-item').forEach(item => {
        const yangBtn = item.querySelector('.yao-value-btn[data-type="yang"]');
        if (yangBtn) yangBtn.classList.add('default-selected');
    });

    // 赋值 onclick 会替换旧处理器，避免每次切换面板时重复绑定。
    container.onclick = (e) => {
        const btn = e.target.closest('.yao-value-btn');
        if (!btn) return;

        const idx = parseInt(btn.dataset.idx, 10);
        const type = btn.dataset.type;

        if (type === 'yang') specifyYaos[idx] = { yinYang: 1, isChanging: false };
        else if (type === 'yin') specifyYaos[idx] = { yinYang: 0, isChanging: false };
        else if (type === 'laoyang') specifyYaos[idx] = { yinYang: 1, isChanging: true };
        else if (type === 'laoyin') specifyYaos[idx] = { yinYang: 0, isChanging: true };

        const parentItem = btn.closest('.specify-yao-item');
        parentItem.querySelectorAll('.yao-value-btn').forEach(b => {
            b.classList.remove('default-selected', 'active-selected');
        });
        btn.classList.add('active-selected');
    };
}

async function submitSpecify() {
    try {
        const data = await fetchJson(`${API_BASE}/api/qigua/specify`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                method: 'specify',
                yao_values: specifyYaos.map(y => y.yinYang),
                changing_yao: specifyYaos.map(y => y.isChanging),
                ...readTimeInput('specify-time-input')
            })
        });
        await requestPaipan(data);
    } catch (e) {
        alert('指定起卦失败：' + e.message);
    }
}

// ========== 手动摇卦 ==========
async function manualShake() {
    if (currentManualIndex >= 6) {
        alert('已完成六爻，点击“重新开始”可重摇');
        return;
    }

    try {
        const data = await fetchJson(`${API_BASE}/api/qigua/manual_step`, { method: 'POST' });
        manualYaos[currentManualIndex] = data;
        currentManualIndex++;
        updateManualPreview();

        if (currentManualIndex === 6) {
            const completed = await fetchJson(`${API_BASE}/api/qigua/manual_complete`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(manualYaos)
            });
            await requestPaipan(completed);
        }
    } catch (e) {
        alert('手动摇卦失败：' + e.message);
    }
}

function resetManual() {
    manualYaos = [];
    currentManualIndex = 0;
    updateManualPreview();
}

function updateManualPreview() {
    document.getElementById('current-yao-index').innerText =
        ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻'][currentManualIndex] || '完成';
    document.getElementById('yao-count').innerText = currentManualIndex;
    const previewDiv = document.getElementById('manual-preview');
    previewDiv.innerHTML = manualYaos.map((y, i) => {
        const sym = getYinYangSymbol(y.yin_yang, y.is_changing);
        return `<span class="preview-yao">${['初', '二', '三', '四', '五', '上'][i]}爻: ${sym}</span>`;
    }).join('');
}

async function requestPaipan(qiguaData) {
    try {
        const paipanData = await fetchJson(`${API_BASE}/api/paipan/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(qiguaData)
        });
        await renderPaipan(paipanData);
    } catch (e) {
        alert('排盘失败：' + e.message);
    }
}
