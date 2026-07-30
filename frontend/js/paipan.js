let currentPaipanData = null;
let currentYongShen = null;
let tooltipTimer = null;
const tooltip = document.getElementById('yaoci-tooltip');

const DIZHI_WUXING_MAP = {
    '子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火',
    '午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'
};
const POSITION_NAMES = {1: '初', 2: '二', 3: '三', 4: '四', 5: '五', 6: '上'};
const ROLE_ROW_CLASS = {
    '用神': 'yongshen-highlight',
    '元神': 'yuanshen-highlight',
    '忌神': 'jishen-highlight',
    '仇神': 'choushen-highlight'
};

function getDizhiWithWuxing(dizhi) {
    return dizhi + DIZHI_WUXING_MAP[dizhi];
}

function statusTone(label) {
    if (/(破|克|冲|空|墓|绝|退|反吟)/.test(label)) return 'warning';
    if (/(生|扶|值|旺|进|暗动)/.test(label)) return 'support';
    return '';
}

function legacyStatusRelations(yao, prefix) {
    const isDay = prefix === '日';
    const values = [];
    const add = (condition, label) => {
        if (condition && !values.includes(label)) values.push(label);
    };
    add(isDay ? yao.ri_zhi : yao.yue_zhi, `值${prefix}`);
    add(isDay ? yao.ri_lin : yao.yue_lin, `${prefix}扶`);
    add(isDay ? yao.ri_he : yao.yue_he, `${prefix}合`);
    add(isDay ? yao.ri_chong : yao.yue_chong, `${prefix}冲`);
    add(isDay ? yao.ri_sheng : yao.yue_sheng, `${prefix}生`);
    add(isDay ? yao.ri_ke : yao.yue_ke, `${prefix}克`);
    if (isDay) {
        add(yao.is_andong, '暗动');
        add(yao.is_ripo, '日破');
    } else {
        add(yao.is_yuepo, '月破');
    }
    return values;
}

function normalizedStatusLabels(labels, prefix) {
    return (labels || []).map(label => {
        if (label === `值${prefix}`) return '值';
        if (label.startsWith(prefix)) return label.slice(1);
        return label;
    });
}

function formatStatusText(labels, prefix) {
    const normalized = normalizedStatusLabels(labels, prefix);
    return normalized.length ? normalized.join('·') : '—';
}

function appendStatusRow(container, prefix, labels) {
    const row = document.createElement('div');
    row.className = 'status-row';
    const source = document.createElement('span');
    source.className = 'status-source';
    source.textContent = prefix;
    const values = document.createElement('span');
    values.className = 'status-values';
    const normalized = normalizedStatusLabels(labels, prefix);
    if (!normalized.length) normalized.push('—');
    normalized.forEach(label => {
        const token = document.createElement('span');
        token.className = `status-token ${statusTone(label)}`.trim();
        token.textContent = label;
        values.appendChild(token);
    });
    row.append(source, values);
    container.appendChild(row);
}

function renderYaoStatus(cell, yao, isShi, isYing) {
    const container = document.createElement('div');
    container.className = 'status-lines';
    const meta = document.createElement('div');
    meta.className = 'status-meta';

    const addMeta = (text, className) => {
        const span = document.createElement('span');
        span.className = className;
        span.textContent = text;
        meta.appendChild(span);
    };
    if (isShi) addMeta('世', 'status-role');
    if (isYing) addMeta('应', 'status-role');
    if (yao.is_kong) addMeta('旬空', 'kong-sign');
    if (yao.is_changing) {
        addMeta(yao.yin_yang === 1 ? '○→' : '×→', 'status-move');
    }
    if (meta.childElementCount) container.appendChild(meta);

    const dayRelations = yao.day_relations?.length
        ? yao.day_relations
        : legacyStatusRelations(yao, '日');
    const monthRelations = yao.month_relations?.length
        ? yao.month_relations
        : legacyStatusRelations(yao, '月');
    appendStatusRow(container, '日', dayRelations);
    appendStatusRow(container, '月', monthRelations);
    cell.appendChild(container);
}

function transformationTone(label) {
    if (/(回头克|化退|化空|化破|化墓|化绝|化冲|反吟)/.test(label)) {
        return 'warning';
    }
    if (/(回头生|化进|化长生|化帝旺)/.test(label)) return 'support';
    return '';
}

function renderTransformationTags(cell, yao) {
    let labels = yao.transformation_relations || [];
    if (!labels.length && yao.shengke) {
        labels = yao.shengke.split(/[、；\s]+/).filter(Boolean);
    }
    if (
        yao.is_changing
        && yao.biangua_info?.is_kong
        && !labels.includes('化空')
    ) {
        labels = [...labels, '化空'];
    }
    if (!labels.length) {
        cell.textContent = '—';
        return;
    }
    const tags = document.createElement('div');
    tags.className = 'transform-tags';
    labels.forEach(label => {
        const tag = document.createElement('span');
        tag.className = `transform-tag ${transformationTone(label)}`.trim();
        tag.textContent = label;
        tags.appendChild(tag);
    });
    cell.appendChild(tags);
}

async function renderPaipan(data) {
    currentPaipanData = data;
    currentYongShen = null;

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
    reversedYaos.forEach(yao => {
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
            handleCellHover(e, data.ben_gua_name, pos);
        });
        tdBen.addEventListener('mouseleave', hideTooltip);
        tr.appendChild(tdBen);

        // 5. 状态列
        const tdMark = document.createElement('td');
        renderYaoStatus(tdMark, yao, isShi, isYing);
        tr.appendChild(tdMark);

        // 6. 变卦（悬停显示变卦爻辞）
        const tdBian = document.createElement('td');
        if (yao.biangua_info) {
            const bianInfo = yao.biangua_info;
            const bianDizhiFull = getDizhiWithWuxing(bianInfo.dizhi);
            const bianYaoSymbol = bianInfo.yin_yang === 1 ? '▅▅▅▅▅' : '▅▅　▅▅';
            const bianMain = document.createElement('span');
            bianMain.className = 'bian-main';
            bianMain.textContent = `${bianInfo.liuqin} ${bianDizhiFull} ${bianYaoSymbol}`;
            tdBian.appendChild(bianMain);
            if (yao.is_changing) {
                bianMain.style.fontWeight = 'bold';
                const status = document.createElement('span');
                status.className = 'bian-status';
                const day = formatStatusText(bianInfo.day_relations, '日');
                const month = formatStatusText(bianInfo.month_relations, '月');
                status.textContent = `日：${day}　月：${month}`;
                tdBian.appendChild(status);
            }
        } else {
            tdBian.innerText = '—';
        }
        if (data.bian_gua_name) {
            tdBian.addEventListener('mouseenter', (e) => {
                handleCellHover(e, data.bian_gua_name, pos);
            });
            tdBian.addEventListener('mouseleave', hideTooltip);
        }
        tr.appendChild(tdBian);

        // 7. 关系列
        const tdRel = document.createElement('td');
        renderTransformationTags(tdRel, yao);
        tr.appendChild(tdRel);

        tbody.appendChild(tr);
    });

    // 渲染全局关系面板（三合局、六合六冲等）
    renderRelationsPanel(data.relations);
    renderInterpretationPanel(data.analysis);

    const warning = await loadGuaci(
        data.ben_gua_name,
        data.bian_gua_name
    );
    document.getElementById('result-section').classList.remove('hidden');
    return warning;
}

function handleCellHover(e, guaName, pos) {
    clearTimeout(tooltipTimer);
    tooltipTimer = setTimeout(async () => {
        try {
            const name = encodeURIComponent(guaName);
            const data = await requestJson(
                `/api/yaoci/name/${name}/${pos}`
            );
            showTooltip(e.clientX, e.clientY, data.yao_ci);
        } catch (error) {
            showTooltip(e.clientX, e.clientY, '暂无爻辞');
        }
    }, 600);
}

async function loadGuaci(benName, bianName) {
    const failures = [];

    async function loadOne(name, prefix) {
        const encodedName = encodeURIComponent(name);
        const gua = await requestJson(`/api/guaci/name/${encodedName}`);
        document.getElementById(`${prefix}-gua-name-ci`).textContent = gua.name;
        document.getElementById(`${prefix}-gua-ci`).textContent = gua.gua_ci;
        document.getElementById(`${prefix}-gua-xiang`).textContent = gua.xiang_ci;
    }

    try {
        await loadOne(benName, 'ben');
    } catch (error) {
        failures.push(`本卦卦辞：${error.message}`);
        document.getElementById('ben-gua-name-ci').textContent = benName;
        document.getElementById('ben-gua-ci').textContent = '卦辞加载失败';
        document.getElementById('ben-gua-xiang').textContent = '';
    }

    const bianContainer = document.getElementById('bian-guaci-container');
    if (!bianName) {
        bianContainer.style.display = 'none';
    } else {
        bianContainer.style.display = 'block';
        try {
            await loadOne(bianName, 'bian');
        } catch (error) {
            failures.push(`变卦卦辞：${error.message}`);
            document.getElementById('bian-gua-name-ci').textContent = bianName;
            document.getElementById('bian-gua-ci').textContent = '卦辞加载失败';
            document.getElementById('bian-gua-xiang').textContent = '';
        }
    }

    if (failures.length > 0) {
        return {
            message: `排盘完成，但${failures.join('；')}`,
            type: 'warning'
        };
    }
    return null;
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

}

function appendAnalysisEmpty(container, text) {
    container.innerHTML = '';
    const empty = document.createElement('p');
    empty.className = 'analysis-empty';
    empty.textContent = text;
    container.appendChild(empty);
}

function renderFindingList(containerId, findings, emptyText) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';
    if (!findings?.length) {
        appendAnalysisEmpty(container, emptyText);
        return;
    }
    findings.forEach(finding => {
        const entry = document.createElement('article');
        entry.className = 'analysis-entry';
        const title = document.createElement('div');
        title.className = 'analysis-entry-title';
        title.textContent = finding.title;
        const detail = document.createElement('div');
        detail.className = 'analysis-entry-detail';
        detail.textContent = finding.detail;
        entry.append(title, detail);
        if (finding.rule_ids?.length) {
            const rules = document.createElement('div');
            rules.className = 'analysis-entry-rules';
            rules.textContent = `依据：${finding.rule_ids.join('、')}`;
            entry.appendChild(rules);
        }
        container.appendChild(entry);
    });
}

function renderRoleCards(profile) {
    const grid = document.getElementById('yongshen-role-grid');
    if (!grid) return;
    grid.innerHTML = '';
    const roleClass = {
        '用神': 'role-yongshen',
        '元神': 'role-yuanshen',
        '忌神': 'role-jishen',
        '仇神': 'role-choushen'
    };
    profile.roles.forEach(role => {
        const card = document.createElement('article');
        card.className = `role-card ${roleClass[role.role] || ''}`.trim();
        const title = document.createElement('div');
        title.className = 'role-card-title';
        title.textContent = `${role.role} · ${role.liuqin}`;
        const relation = document.createElement('div');
        relation.className = 'role-card-relation';
        relation.textContent = role.relationship;
        card.append(title, relation);

        const list = document.createElement('div');
        list.className = 'candidate-list';
        if (!role.candidates.length) {
            const empty = document.createElement('span');
            empty.className = 'analysis-empty';
            empty.textContent = '本卦及伏神未见';
            list.appendChild(empty);
        }
        role.candidates.forEach(candidate => {
            const item = document.createElement('div');
            item.className = 'candidate-item';
            const main = document.createElement('div');
            main.className = 'candidate-main';
            const place = candidate.is_hidden
                ? `伏于${POSITION_NAMES[candidate.position]}爻`
                : `${POSITION_NAMES[candidate.position]}爻`;
            main.textContent = `${place} · ${candidate.dizhi}${candidate.wuxing} · ${candidate.activity}`;
            item.appendChild(main);
            if (candidate.statuses?.length) {
                const statuses = document.createElement('div');
                statuses.className = 'candidate-statuses';
                candidate.statuses.forEach(text => {
                    const status = document.createElement('span');
                    status.className = 'candidate-status';
                    status.textContent = text;
                    statuses.appendChild(status);
                });
                item.appendChild(statuses);
            }
            list.appendChild(item);
        });
        card.appendChild(list);
        grid.appendChild(card);
    });
}

function renderTimingHints(hints) {
    const container = document.getElementById('timing-content');
    if (!container) return;
    container.innerHTML = '';
    if (!hints?.length) {
        appendAnalysisEmpty(container, '当前用神没有可直接列出的应期线索。');
        return;
    }
    hints.forEach(hint => {
        const entry = document.createElement('article');
        entry.className = 'timing-entry';
        const trigger = document.createElement('div');
        trigger.className = 'timing-trigger';
        trigger.textContent = hint.trigger;
        const detail = document.createElement('div');
        detail.className = 'timing-detail';
        detail.textContent = hint.detail;
        const branches = document.createElement('div');
        branches.className = 'timing-branches';
        hint.branches.forEach(branch => {
            const tag = document.createElement('span');
            tag.className = 'branch-tag';
            tag.textContent = branch;
            branches.appendChild(tag);
        });
        entry.append(trigger, detail, branches);
        if (hint.rule_ids?.length) {
            const rules = document.createElement('div');
            rules.className = 'analysis-entry-rules';
            rules.textContent = `依据：${hint.rule_ids.join('、')}`;
            entry.appendChild(rules);
        }
        container.appendChild(entry);
    });
}

function renderRuleTraces(traces) {
    const container = document.getElementById('rule-trace-content');
    if (!container) return;
    container.innerHTML = '';
    (traces || []).forEach(trace => {
        const item = document.createElement('article');
        item.className = 'rule-trace-item';
        const title = document.createElement('div');
        title.className = 'rule-trace-title';
        const ruleId = document.createElement('span');
        ruleId.className = 'rule-id';
        ruleId.textContent = trace.rule_id;
        title.appendChild(ruleId);
        title.append(document.createTextNode(trace.title));

        const source = document.createElement('div');
        source.className = 'rule-trace-source';
        const link = document.createElement('a');
        link.href = trace.source_url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = trace.source;
        source.append(link, document.createTextNode(` · ${trace.confidence}`));

        const quote = document.createElement('div');
        quote.className = 'rule-trace-quote';
        quote.textContent = `“${trace.source_text}”`;
        item.append(title, source, quote);
        container.appendChild(item);
    });
}

function renderYongshenProfile(data) {
    const summary = document.getElementById('yongshen-summary');
    const basis = document.getElementById('yongshen-basis');
    const grid = document.getElementById('yongshen-role-grid');
    const actionSection = document.getElementById('yongshen-action-section');
    const timing = document.getElementById('timing-content');
    const profile = currentYongShen
        ? data?.analysis?.yongshen_profiles?.[currentYongShen]
        : null;
    if (!profile) {
        if (summary) summary.textContent = currentYongShen
            ? '当前响应没有该用神分析。'
            : '尚未选择用神。';
        if (basis) {
            basis.hidden = true;
            basis.textContent = '';
        }
        if (actionSection) actionSection.hidden = true;
        if (grid) grid.innerHTML = '';
        if (timing) appendAnalysisEmpty(timing, '选择用神后显示。');
        return;
    }
    if (summary) summary.textContent = profile.summary;
    if (basis) {
        basis.textContent = `取用依据：${(profile.rule_ids || []).join('、')}`;
        basis.hidden = !profile.rule_ids?.length;
    }
    renderRoleCards(profile);
    if (actionSection) actionSection.hidden = false;
    renderFindingList(
        'yongshen-action-content',
        profile.action_findings,
        '未触发明确的动爻或得扶静爻作用候选。'
    );
    renderTimingHints(profile.timing_hints);
}

function renderInterpretationPanel(analysis) {
    const panel = document.getElementById('analysis-panel');
    if (!panel) return;
    if (!analysis) {
        panel.style.display = 'none';
        return;
    }
    panel.style.display = 'grid';
    const notice = document.getElementById('analysis-notice');
    if (notice) notice.textContent = analysis.notice;
    renderFindingList(
        'transformation-content',
        analysis.transformation_findings,
        '本卦无明动爻。'
    );
    renderFindingList(
        'structure-content',
        analysis.structure_findings,
        '未触发反伏吟或特殊卦变。'
    );
    renderRuleTraces(analysis.rule_traces);

    const selector = document.getElementById('yongshen-selector');
    if (selector) {
        selector.querySelectorAll('.yongshen-btn').forEach(button => {
            button.classList.remove('active');
            if (button.dataset.yongshen) {
                button.setAttribute('aria-pressed', 'false');
            }
        });
        if (!selector.dataset.bound) {
            selector.addEventListener('click', event => {
                const button = event.target.closest('.yongshen-btn');
                if (!button) return;
                currentYongShen = button.dataset.yongshen || null;
                selector.querySelectorAll('.yongshen-btn').forEach(item => {
                    const selected = Boolean(currentYongShen)
                        && item.dataset.yongshen === currentYongShen;
                    item.classList.toggle('active', selected);
                    if (item.dataset.yongshen) {
                        item.setAttribute('aria-pressed', String(selected));
                    }
                });
                renderYongshenProfile(currentPaipanData);
                applyYongshenHighlight(currentPaipanData);
            });
            selector.dataset.bound = 'true';
        }
    }
    renderYongshenProfile(currentPaipanData);
    applyYongshenHighlight(currentPaipanData);
}

function applyYongshenHighlight(data) {
    const rowClasses = Object.values(ROLE_ROW_CLASS);
    document.querySelectorAll('#yao-tbody tr').forEach(row => {
        row.classList.remove(...rowClasses);
    });
    document.querySelectorAll('.relation-highlight').forEach(element => {
        element.classList.remove('relation-highlight');
    });
    if (!currentYongShen || !data) return;

    const profile = data.analysis?.yongshen_profiles?.[currentYongShen];
    const targetDizhiSet = new Set();
    if (profile) {
        profile.roles.forEach(role => {
            role.candidates.forEach(candidate => {
                if (role.role === '用神') {
                    targetDizhiSet.add(candidate.dizhi);
                }
                if (candidate.is_hidden) return;
                const row = document.querySelector(
                    `tr[data-yao-pos="${candidate.position}"]`
                );
                if (row) row.classList.add(ROLE_ROW_CLASS[role.role]);
            });
        });
    } else {
        data.yao_list.forEach(yao => {
            if (yao.liuqin !== currentYongShen) return;
            targetDizhiSet.add(yao.dizhi);
            const row = document.querySelector(
                `tr[data-yao-pos="${yao.position}"]`
            );
            if (row) row.classList.add('yongshen-highlight');
        });
    }

    ['sanhe-content', 'liuhe-liuchong-content', 'shengwangmujue-content']
        .forEach(containerId => {
            const container = document.getElementById(containerId);
            container?.querySelectorAll('.relation-entry').forEach(entry => {
                const related = Array.from(targetDizhiSet).some(dizhi => {
                    return entry.textContent.includes(dizhi);
                });
                entry.classList.toggle('relation-highlight', related);
            });
        });
}
