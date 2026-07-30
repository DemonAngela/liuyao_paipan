// 通用前端工具。

function getYinYangSymbol(yinYang, isChanging) {
    if (yinYang === 1) {
        return isChanging ? '○' : '─';
    }
    return isChanging ? '×' : '--';
}

function formatGanZhi(ganZhi) {
    return `${ganZhi.year}年 ${ganZhi.month}月 ${ganZhi.day}日 ${ganZhi.hour}时`;
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

function extractErrorMessage(payload, status) {
    if (typeof payload?.detail === 'string') {
        return payload.detail;
    }
    if (Array.isArray(payload?.detail) && payload.detail.length > 0) {
        return '输入无效，请检查日期时间和六爻参数';
    }
    return `请求失败（HTTP ${status}）`;
}

async function requestJson(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, options);
    const contentType = response.headers.get('content-type') || '';
    let payload = null;

    if (contentType.includes('application/json')) {
        payload = await response.json();
    } else {
        const text = await response.text();
        payload = text ? { detail: text } : null;
    }
    if (!response.ok) {
        throw new Error(extractErrorMessage(payload, response.status));
    }
    return payload;
}

function readLocalDateTime(inputId) {
    const value = document.getElementById(inputId).value;
    if (!value) {
        return {};
    }
    const match = value.match(
        /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?$/
    );
    if (!match) {
        throw new Error('日期时间格式无效');
    }
    const [, year, month, day, hour, minute, second = '0'] = match;
    return {
        year: Number(year),
        month: Number(month),
        day: Number(day),
        hour: Number(hour),
        minute: Number(minute),
        second: Number(second)
    };
}
