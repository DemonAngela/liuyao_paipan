// 通用工具函数

// 获取阴阳符号
function getYinYangSymbol(yinYang, isChanging) {
    if (yinYang === 1) {
        return isChanging ? '○' : '─';
    } else {
        return isChanging ? '×' : '--';
    }
}

// 格式化干支显示
function formatGanZhi(ganZhi) {
    return `${ganZhi.year}年 ${ganZhi.month}月 ${ganZhi.day}日 ${ganZhi.hour}时`;
}

// 延迟执行（用于悬停）
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// 获取卦ID通过名称
function getGuaIdByName(name) {
    return GUA_NAME_TO_ID[name] || null;
}