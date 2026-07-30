let currentPaipanData = null;
let currentYongShen = null;
let tooltipTimer = null;
const tooltip = document.getElementById('yaoci-tooltip');

const DIZHI_WUXING_MAP = {
    '子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火',
    '午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'
};

function getDizhiWithWuxing(dizhi) {
    return dizhi + DIZHI_WUXING_MAP[dizhi];
}

async function renderPaipan(data) {
    currentPaipanData = data;

    // 天干地支信息
    const ganzhiStr = `${data.gan_zhi.year}年 ${data.gan_zhi.month}月 ${data.gan_zhi.day}日 ${data.gan_zhi.hour}时`;
    const xunkongStr = data.xunkong.join('、');
    const infoHtml = `${ganzhiStr} (${xunkongStr}空)`;

    let ganzhiDiv = document.querySelector('.ganzhi-info');
    if (!ganzhiDiv) {
        ganzhiDiv = document.createElement('div');
        ganzhiDiv.className = 'ganzhi-info';
    }
    ganzhiDiv.textContent = infoHtml;
    const headerRow = document.getElementById('header-row');
    if (headerRow && !headerRow.contains(ganzhiDiv)) {
        headerRow.insertBefore(ganzhiDiv, headerRow.firstChild);
    }

    document.getElementById('time-info')?.remove();
    document.getElementById('xunkong-info')?.style.setProperty('display', 'none');

    document.getElementById('ben-gua-name').innerText = data.ben_gua_name;
    document.getElementById('bian-gua-name').innerText = data.bian_gua_name || '—';

    // 辅助函数：为卦名添加特殊标记
    function appendSpecialMark(guaElement, attr) {
        if (!attr) return;
        const markSpan = document.createElement('span');
        markSpan.style.fontSize = '0.7rem';
        markSpan.style.marginLeft = '8px';
        markSpan.style.padding = '2px 8px';
        markSpan.style.borderRadius = '12px';
        markSpan.style.fontWeight = 'normal';
        if (attr === '六冲') markSpan.style.backgroundColor = '#e8d5b0';
        else if (attr === '六合') markSpan.style.backgroundColor = '#c8d6a6';
        else markSpan.style.backgroundColor = '#d4c5b0';
        markSpan.innerText = attr;
        guaElement.appendChild(markSpan);
    }

    const benGuaElement = document.getElementById('ben-gua-name');
    const bianGuaElement = document.getElementById('bian-gua-name');
    appendSpecialMark(benGuaElement, data.special_attr);
    appendSpecialMark(bianGuaElement, data.bian_special_attr);

    const tbody = document.getElementById('yao-tbody');
    const yaoNames = ['初', '二', '三', '四', '五', '上'];
    const reversedYaos = [...data.yao_list].reverse();

    tbody.innerHTML = '';
    reversedYaos.forEach((yao, idx) => {
        const pos = yao.position;
        const isShi = pos === data.shi_yao;
        const isYing = pos === data.ying_yao;
        const rowClass = isShi ? 'shi-yao' : (isYing ? 'ying-yao' : '');

        const tr = document.createElement('tr');
        tr.className = rowClass;
        tr.dataset.yaoPos = pos;   // 添加用于高亮的属性

        // 1. 爻位
        const tdPos = document.createElement('td');
        tdPos.innerText = yaoNames[pos-1];
        tr.appendChild(tdPos);

        // 2. 六神
        const tdShen = document.createElement('td');
        tdShen.innerText = yao.liushen;
        tr.appendChild(tdShen);

        // 3. 伏神
        const tdFushen = document.createElement('td');
        tdFushen.innerText = yao.fushen || '—';
        tr.appendChild(tdFushen);

        // 4. 本卦（悬停显示本卦爻辞）
        const tdBen = document.createElement('td');
        const benDizhiFull = getDizhiWithWuxing(yao.dizhi);
        const benYaoSymbol = yao.yin_yang === 1 ? '▅▅▅▅▅' : '▅▅　▅▅';   // 必须在使用前声明
        tdBen.innerText = `${yao.liuqin} ${benDizhiFull} ${benYaoSymbol}`;
        tdBen.addEventListener('mouseenter', (e) => {
            const benGuaId = getGuaIdByName(data.ben_gua_name);
            if (benGuaId) handleCellHover(e, benGuaId, pos);
        });
        tdBen.addEventListener('mouseleave', hideTooltip);
        tr.appendChild(tdBen);

            // 5. 状态列
        const tdMark = document.createElement('td');
        tdMark.style.whiteSpace = 'nowrap';

        let htmlParts = [];

        // 世应（加粗）
        if (isShi) htmlParts.push('<span style="font-weight:bold;">世</span>');
        if (isYing) htmlParts.push('<span style="font-weight:bold;">应</span>');

        // 旬空（红色小字）
        if (yao.is_kong) {
            htmlParts.push('<span class="kong-sign">(空)</span>');
        }

        // 日月关系（按优先级：值 > 临 > 合 > 生 > 克，冲合并由暗动/日破/月破体现）
        // 日建部分：若存在暗动或日破，优先显示，不再显示日克
        if (yao.ri_zhi) htmlParts.push('值日');
        else if (yao.is_andong) htmlParts.push('暗动');
        else if (yao.is_ripo) htmlParts.push('日破');
        else if (yao.ri_lin) htmlParts.push('临日');
        else if (yao.ri_he) htmlParts.push('日合');
        else if (yao.ri_sheng) htmlParts.push('日生');
        else if (yao.ri_ke) htmlParts.push('日克');
        // 日冲已由暗动或日破表示，不单独显示

        // 月建部分：月破优先显示
        if (yao.yue_zhi) htmlParts.push('值月');
        else if (yao.is_yuepo) htmlParts.push('月破');
        else if (yao.yue_lin) htmlParts.push('临月');
        else if (yao.yue_he) htmlParts.push('月合');
        else if (yao.yue_sheng) htmlParts.push('月生');
        else if (yao.yue_ke) htmlParts.push('月克');
        // 月冲即月破，统一由月破表示

        // 动爻符号
        if (yao.is_changing) {
            const moveMark = yao.yin_yang === 1 ? '○' : '×';
            htmlParts.push(moveMark + '→');
        }

        tdMark.innerHTML = htmlParts.join(' ');
        tr.appendChild(tdMark);

        // 6. 变卦（悬停显示变卦爻辞）
        const tdBian = document.createElement('td');
        if (yao.biangua_info) {
            const bianInfo = yao.biangua_info;
            const bianDizhiFull = getDizhiWithWuxing(bianInfo.dizhi);
            const bianYaoSymbol = bianInfo.yin_yang === 1 ? '▅▅▅▅▅' : '▅▅　▅▅';   // 在使用前声明
            tdBian.innerText = `${bianInfo.liuqin} ${bianDizhiFull} ${bianYaoSymbol}`;
            if (yao.is_changing) tdBian.style.fontWeight = 'bold';
        } else {
            tdBian.innerText = '—';
        }
        if (data.bian_gua_name) {
            tdBian.addEventListener('mouseenter', (e) => {
                const bianGuaId = getGuaIdByName(data.bian_gua_name);
                if (bianGuaId) handleCellHover(e, bianGuaId, pos);
            });
            tdBian.addEventListener('mouseleave', hideTooltip);
        }
        tr.appendChild(tdBian);

        // 7. 关系列
        const tdRel = document.createElement('td');
        let relationText = yao.shengke || '';
        if (yao.is_changing && yao.biangua_info?.is_kong) {
            const kongSpan = document.createElement('span');
            kongSpan.className = 'kong-sign';
            kongSpan.innerText = '(空)';
            if (relationText) {
                const textSpan = document.createElement('span');
                textSpan.innerText = relationText + ' ';
                tdRel.appendChild(textSpan);
            }
            tdRel.appendChild(kongSpan);
        } else {
            tdRel.innerText = relationText;
        }

        if (relationText) {
            const span = document.createElement('span');
            span.innerText = relationText;
            if (relationText.includes('回头生') || relationText.includes('生')) {
                span.className = 'shengke-sheng';
            } else if (relationText.includes('回头克') || relationText.includes('克')) {
                span.className = 'shengke-ke';
            } else if (relationText.includes('化合') || relationText.includes('合')) {
                span.className = 'shengke-he';
            } else if (relationText.includes('化冲') || relationText.includes('冲')) {
                span.className = 'shengke-chong';
            }
            tdRel.innerHTML = '';
            tdRel.appendChild(span);
            if (yao.is_changing && yao.biangua_info?.is_kong) {
                const kongSpan = document.createElement('span');
                kongSpan.className = 'kong-sign';
                kongSpan.innerText = ' (空)';
                tdRel.appendChild(kongSpan);
            }
        }
        tr.appendChild(tdRel);

        tbody.appendChild(tr);
    });

    // 渲染全局关系面板（三合局、六合六冲等）
    renderRelationsPanel(data.relations);

    await loadGuaci(data.ben_gua_name, data.bian_gua_name);
    document.getElementById('result-section').style.display = 'block';
}

function handleCellHover(e, guaId, pos) {
    clearTimeout(tooltipTimer);
    tooltipTimer = setTimeout(async () => {
        try {
            const resp = await fetch(`${API_BASE}/api/yaoci/${guaId}/${pos}`);
            const data = await resp.json();
            showTooltip(e.clientX, e.clientY, data.yao_ci);
        } catch (error) {
            showTooltip(e.clientX, e.clientY, '暂无爻辞');
        }
    }, 600);
}

async function loadGuaci(benName, bianName) {
    const benId = getGuaIdByName(benName);
    if (benId) {
        try {
            const resp = await fetch(`${API_BASE}/api/guaci/${benId}`);
            const gua = await resp.json();
            document.getElementById('ben-gua-name-ci').innerText = gua.name;
            document.getElementById('ben-gua-ci').innerText = gua.gua_ci;
            document.getElementById('ben-gua-xiang').innerText = gua.xiang_ci;
        } catch(e) {}
    }
    if (bianName) {
        const bianId = getGuaIdByName(bianName);
        if (bianId) {
            try {
                const resp = await fetch(`${API_BASE}/api/guaci/${bianId}`);
                const gua = await resp.json();
                document.getElementById('bian-gua-name-ci').innerText = gua.name;
                document.getElementById('bian-gua-ci').innerText = gua.gua_ci;
                document.getElementById('bian-gua-xiang').innerText = gua.xiang_ci;
                document.getElementById('bian-guaci-container').style.display = 'block';
            } catch(e) {}
        }
    } else {
        document.getElementById('bian-guaci-container').style.display = 'none';
    }
}

function showTooltip(x, y, text) {
    tooltip.innerText = text;
    tooltip.style.left = (x + 15) + 'px';
    tooltip.style.top = (y + 15) + 'px';
    tooltip.classList.remove('hidden');
}

function hideTooltip() {
    clearTimeout(tooltipTimer);
    tooltip.classList.add('hidden');
}

function renderRelationsPanel(relations) {
    const panel = document.getElementById('relations-panel');
    if (!panel) return;

    // 辅助函数：将爻位数字转换为中文
    function posToChinese(pos) {
        const map = {1: '初', 2: '二', 3: '三', 4: '四', 5: '五', 6: '上'};
        return map[pos] || pos;
    }

        // 三合局固定顺序
    const SANHE_ORDER = {
        '水': ['申', '子', '辰'],
        '金': ['巳', '酉', '丑'],
        '火': ['寅', '午', '戌'],
        '木': ['亥', '卯', '未']
    };

    // 1. 三合局
    const sanheDiv = document.getElementById('sanhe-content');
    if (relations.sanhe && relations.sanhe.length > 0) {
        const sanheText = relations.sanhe.map(s => {
            const order = SANHE_ORDER[s.wuxing];
            if (!order) return '';
            const items = s.items;
            // 按照 order 顺序重新排列 items
            const sorted = [];
            for (const zhi of order) {
                const item = items.find(it => it.dizhi === zhi);
                if (item) sorted.push(item);
            }
            if (sorted.length !== 3) {
                // 容错回退
                return `${s.wuxing}局（${items.map(it => {
                    const posLabel = it.is_bian ? `[${posToChinese(it.src_pos)}动]` : posToChinese(it.pos);
                    return posLabel + it.dizhi;
                }).join('')}）`;
            }
            const labels = sorted.map(it => {
                if (it.is_bian) return `[${posToChinese(it.src_pos)}动]`;
                return posToChinese(it.pos);
            });
            const zhis = sorted.map(it => it.dizhi).join('');
             return `<span class="relation-entry">${s.wuxing}局（${labels.join('')}${zhis}）</span>`;
        }).join('；');
        sanheDiv.innerHTML = `<span style="font-weight:500;">三合局：</span>${sanheText}`;
    } else {
        sanheDiv.innerHTML = '<span style="font-weight:500;">三合局：</span>无';
    }

    // 2. 六合与六冲（含爻位）
    const liuheDiv = document.getElementById('liuhe-liuchong-content');
    let parts = [];
    if (relations.liuhe && relations.liuhe.length > 0) {
        const heItems = relations.liuhe.map(item => {
            // item 格式: [地支1, 地支2, 爻位1, 爻位2]
            const zhi1 = item[0], zhi2 = item[1], pos1 = item[2], pos2 = item[3];
            return `<span class="relation-entry">${zhi1}${zhi2}合（${posToChinese(pos1)}${posToChinese(pos2)}）</span>`;
        });
        parts.push('六合：' + heItems.join('、'));
    }
    if (relations.liuchong && relations.liuchong.length > 0) {
        const chongItems = relations.liuchong.map(item => {
            const zhi1 = item[0], zhi2 = item[1], pos1 = item[2], pos2 = item[3];
            return `<span class="relation-entry">${zhi1}冲${zhi2}（${posToChinese(pos1)}${posToChinese(pos2)}）</span>`;
        });
        parts.push('六冲：' + chongItems.join('、'));
    }
    liuheDiv.innerHTML = parts.length > 0 ? parts.join('；') : '<span style="font-weight:500;">六合六冲：</span>无';

    // 3. 生旺墓绝
    const swmjDiv = document.getElementById('shengwangmujue-content');
    if (relations.shengwangmujue_details && relations.shengwangmujue_details.length > 0) {
        swmjDiv.innerHTML = '<span style="font-weight:500;">生旺墓绝：</span>' +
            relations.shengwangmujue_details.map(d => `<span class="relation-entry">${d}</span>`).join('；');
    } else {
        swmjDiv.innerHTML = '<span style="font-weight:500;">生旺墓绝：</span>无';
    }

    panel.style.display = 'block';

    // 显示用神选择器并绑定事件
    const yongshenSelector = document.getElementById('yongshen-selector');
    if (yongshenSelector) {
        yongshenSelector.style.display = 'flex';
        // 移除之前的激活状态
        yongshenSelector.querySelectorAll('.yongshen-btn').forEach(btn => btn.classList.remove('active'));
        // 绑定点击事件（只绑定一次，但可每次渲染时清理并重新绑定，简单起见使用事件委托）
        if (!yongshenSelector._bound) {
            yongshenSelector.addEventListener('click', (e) => {
                const btn = e.target.closest('.yongshen-btn');
                if (!btn) return;
                const yongshen = btn.dataset.yongshen;
                // 更新激活样式
                yongshenSelector.querySelectorAll('.yongshen-btn').forEach(b => b.classList.remove('active'));
                if (yongshen) btn.classList.add('active');
                else {
                    // 清除按钮高亮空
                    const clearBtn = yongshenSelector.querySelector('.yongshen-clear');
                    if (clearBtn) clearBtn.classList.add('active');
                }
                currentYongShen = yongshen || null;
                // 应用高亮
                applyYongshenHighlight(currentPaipanData);
            });
            yongshenSelector._bound = true;
        }
    }

}

function applyYongshenHighlight(data) {
    // 移除原有高亮行
    document.querySelectorAll('.yongshen-highlight').forEach(tr => tr.classList.remove('yongshen-highlight'));
    // 移除关系高亮
    document.querySelectorAll('.relation-highlight').forEach(el => el.classList.remove('relation-highlight'));

    if (!currentYongShen) return;

    // 获取用神所在的地支集合（可能多个爻）
    const targetDizhiSet = new Set();
    data.yao_list.forEach(yao => {
        if (yao.liuqin === currentYongShen) {
            targetDizhiSet.add(yao.dizhi);
            // 高亮行
            const row = document.querySelector(`tr[data-yao-pos="${yao.position}"]`);
            if (row) row.classList.add('yongshen-highlight');
        }
    });

    if (targetDizhiSet.size === 0) return;

    // 高亮全局关系面板中涉及这些地支的条目
    // 三合局条目
    // 高亮全局关系面板中涉及这些地支的条目
    const highlightEntries = (containerId) => {
        const container = document.getElementById(containerId);
        if (!container) return;
        const entries = container.querySelectorAll('.relation-entry');
        entries.forEach(entry => {
            if (Array.from(targetDizhiSet).some(dz => entry.textContent.includes(dz))) {
                entry.classList.add('relation-highlight');
            }
        });
    };
    highlightEntries('sanhe-content');
    highlightEntries('liuhe-liuchong-content');
    highlightEntries('shengwangmujue-content');
    // 六合六冲条目
    const liuheDiv = document.getElementById('liuhe-liuchong-content');
    if (liuheDiv) {
        const spans = liuheDiv.querySelectorAll('span');
        spans.forEach(span => {
            if (Array.from(targetDizhiSet).some(dz => span.textContent.includes(dz))) {
                span.classList.add('relation-highlight');
            }
        });
    }
    // 生旺墓绝条目（如果已实现）
    const swmjDiv = document.getElementById('shengwangmujue-content');
    if (swmjDiv) {
        const spans = swmjDiv.querySelectorAll('span');
        spans.forEach(span => {
            if (Array.from(targetDizhiSet).some(dz => span.textContent.includes(dz))) {
                span.classList.add('relation-highlight');
            }
        });
    }
}