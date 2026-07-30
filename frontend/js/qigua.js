// 全局状态
let currentMethod = 'auto';
let manualYaos = [];
let currentManualIndex = 0;
let specifyYaos = [];

function initQiguaUI() {
    document.getElementById('btn-auto').addEventListener('click', ()=>switchMethod('auto'));
    document.getElementById('btn-manual').addEventListener('click', ()=>switchMethod('manual'));
    document.getElementById('btn-specify').addEventListener('click', ()=>switchMethod('specify'));
    document.getElementById('btn-time').addEventListener('click', ()=>switchMethod('time'));

    document.getElementById('btn-start-auto').addEventListener('click', autoQigua);
    document.getElementById('btn-shake').addEventListener('click', manualShake);
    document.getElementById('btn-reset-manual').addEventListener('click', resetManual);
    document.getElementById('btn-start-time').addEventListener('click', timeQigua);

    buildSpecifyPanel();
    document.getElementById('btn-submit-specify').addEventListener('click', submitSpecify);

    switchMethod('auto');
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
    if (method === 'specify') buildSpecifyPanel();   // 每次切换回手工指定时重建，重置为默认棕色高亮
}

async function autoQigua() {
    try {
        const resp = await fetch(`${API_BASE}/api/qigua/auto`, { method: 'POST' });
        const data = await resp.json();
        await requestPaipan(data);
    } catch (e) {
        alert('起卦失败：' + e.message);
    }
}

async function timeQigua() {
    const timeInput = document.getElementById('time-input').value;
    let year, month, day, hour;
    if (timeInput) {
        const dt = new Date(timeInput);
        year = dt.getFullYear();
        month = dt.getMonth() + 1;
        day = dt.getDate();
        hour = dt.getHours();
    } else {
        const now = new Date();
        year = now.getFullYear();
        month = now.getMonth() + 1;
        day = now.getDate();
        hour = now.getHours();
    }
    try {
        const resp = await fetch(`${API_BASE}/api/qigua/time`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ method:'time', year, month, day, hour })
        });
        const data = await resp.json();
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

    // 初始化内部数据：默认全为阳静
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

    // 初始化：所有行的“阳”按钮添加默认棕色高亮
    const items = container.querySelectorAll('.specify-yao-item');
    items.forEach(item => {
        const yangBtn = item.querySelector('.yao-value-btn[data-type="yang"]');
        if (yangBtn) yangBtn.classList.add('default-selected');
    });

    // 事件监听
    container.addEventListener('click', (e) => {
        const btn = e.target.closest('.yao-value-btn');
        if (!btn) return;
        const idx = parseInt(btn.dataset.idx);
        const type = btn.dataset.type;

        // 更新内部数据
        if (type === 'yang') specifyYaos[idx] = { yinYang: 1, isChanging: false };
        else if (type === 'yin') specifyYaos[idx] = { yinYang: 0, isChanging: false };
        else if (type === 'laoyang') specifyYaos[idx] = { yinYang: 1, isChanging: true };
        else if (type === 'laoyin') specifyYaos[idx] = { yinYang: 0, isChanging: true };

        // 清除该行所有按钮的高亮类，并为当前按钮添加主动高亮
        const parentItem = btn.closest('.specify-yao-item');
        const allBtns = parentItem.querySelectorAll('.yao-value-btn');
        allBtns.forEach(b => {
            b.classList.remove('default-selected', 'active-selected');
        });
        btn.classList.add('active-selected');
    });
}

function submitSpecify() {
    const yaoList = specifyYaos.map(y => y.yinYang);
    const changing = specifyYaos.map(y => y.isChanging);

    const timeInput = document.getElementById('specify-time-input').value;
    let year, month, day, hour;
    if (timeInput) {
        const dt = new Date(timeInput);
        year = dt.getFullYear();
        month = dt.getMonth() + 1;
        day = dt.getDate();
        hour = dt.getHours();
    } else {
        const now = new Date();
        year = now.getFullYear();
        month = now.getMonth() + 1;
        day = now.getDate();
        hour = now.getHours();
    }

    requestPaipan({
        yao_list: yaoList,
        changing_yao: changing,
        timestamp: { year, month, day, hour }
    });
}

// ========== 手动摇卦 ==========
function manualShake() {
    if (currentManualIndex >= 6) {
        alert('已完成六爻，点击“重新开始”可重摇');
        return;
    }
    fetch(`${API_BASE}/api/qigua/manual_step`, { method: 'POST' })
        .then(r=>r.json())
        .then(data => {
            manualYaos[currentManualIndex] = data;
            currentManualIndex++;
            updateManualPreview();
            if (currentManualIndex === 6) {
                const yaoList = manualYaos.map(y=>y.yin_yang);
                const changing = manualYaos.map(y=>y.is_changing);
                const now = new Date();
                requestPaipan({
                    yao_list: yaoList,
                    changing_yao: changing,
                    timestamp: { year: now.getFullYear(), month: now.getMonth()+1, day: now.getDate(), hour: now.getHours() }
                });
            }
        });
}

function resetManual() {
    manualYaos = [];
    currentManualIndex = 0;
    updateManualPreview();
}

function updateManualPreview() {
    document.getElementById('current-yao-index').innerText =
        ['初爻','二爻','三爻','四爻','五爻','上爻'][currentManualIndex] || '完成';
    document.getElementById('yao-count').innerText = currentManualIndex;
    const previewDiv = document.getElementById('manual-preview');
    previewDiv.innerHTML = manualYaos.map((y, i) => {
        const sym = getYinYangSymbol(y.yin_yang, y.is_changing);
        return `<span class="preview-yao">${['初','二','三','四','五','上'][i]}爻: ${sym}</span>`;
    }).join('');
}

async function requestPaipan(qiguaData) {
    try {
        const resp = await fetch(`${API_BASE}/api/paipan/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(qiguaData)
        });
        if (!resp.ok) throw new Error(await resp.text());
        const paipanData = await resp.json();
        renderPaipan(paipanData);
    } catch (e) {
        alert('排盘失败：' + e.message);
    }
}