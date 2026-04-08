/**
 * AI 新闻简报 - 工具函数库
 * 提供各种辅助功能
 */

// 日期格式化工具
const DateUtils = {
    /**
     * 格式化日期为 YYYY-MM-DD
     */
    formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    },

    /**
     * 格式化日期为 YY/MM/DD
     */
    formatDateShort(date) {
        const year = String(date.getFullYear()).slice(-2);
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}/${month}/${day}`;
    },

    /**
     * 解析日期字符串
     */
    parseDate(dateStr) {
        return new Date(dateStr);
    },

    /**
     * 获取相对日期（今天、昨天等）
     */
    getRelativeDate(dateStr) {
        const date = new Date(dateStr);
        const today = new Date();
        const diffDays = Math.floor((today - date) / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return '今天';
        if (diffDays === 1) return '昨天';
        if (diffDays === 2) return '前天';
        if (diffDays < 7) return `${diffDays}天前`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)}周前`;
        return date.toLocaleDateString('zh-CN');
    }
};

// 文本处理工具
const TextUtils = {
    /**
     * 截断文本
     */
    truncate(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.slice(0, maxLength - 3) + '...';
    },

    /**
     * 高亮关键词
     */
    highlight(text, keywords) {
        let result = text;
        keywords.forEach(keyword => {
            const regex = new RegExp(`(${keyword})`, 'gi');
            result = result.replace(regex, '<mark>$1</mark>');
        });
        return result;
    },

    /**
     * 移除HTML标签
     */
    stripHtml(html) {
        const tmp = document.createElement('div');
        tmp.innerHTML = html;
        return tmp.textContent || tmp.innerText || '';
    },

    /**
     * 计算阅读时间（分钟）
     */
    readingTime(text) {
        const wordsPerMinute = 200;
        const wordCount = text.length / 2; // 中文按字符数/2估算
        return Math.ceil(wordCount / wordsPerMinute);
    }
};

// 存储工具
const StorageUtils = {
    /**
     * 保存到本地存储
     */
    save(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('保存失败:', e);
            return false;
        }
    },

    /**
     * 从本地存储读取
     */
    load(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('读取失败:', e);
            return defaultValue;
        }
    },

    /**
     * 删除本地存储
     */
    remove(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (e) {
            console.error('删除失败:', e);
            return false;
        }
    },

    /**
     * 清空本地存储
     */
    clear() {
        try {
            localStorage.clear();
            return true;
        } catch (e) {
            console.error('清空失败:', e);
            return false;
        }
    }
};

// 导出工具
const ExportUtils = {
    /**
     * 导出为Markdown
     */
    toMarkdown(newsData) {
        let md = `# ${newsData.title} - ${newsData.date_formatted}\n\n`;

        newsData.news.forEach((item, index) => {
            const icons = { 'critical': '🔥', 'high': '📌', 'medium': '·' };
            const icon = icons[item.importance] || '·';

            md += `${icon} ${item.content}\n`;

            if (item.keywords && item.keywords.length > 0) {
                md += `   *关键词: ${item.keywords.join(', ')}*\n`;
            }

            if (item.url) {
                md += `   [查看原文](${item.url})\n`;
            }

            md += '\n';
        });

        md += '---\n\n';
        md += `*生成时间: ${newsData.metadata.generated_at}*\n`;
        md += `*新闻总数: ${newsData.metadata.total_news}*\n`;

        return md;
    },

    /**
     * 导出为纯文本
     */
    toPlainText(newsData) {
        let text = `${newsData.title} - ${newsData.date_formatted}\n`;
        text += '='.repeat(60) + '\n\n';

        newsData.news.forEach((item) => {
            const icons = { 'critical': '🔥', 'high': '📌', 'medium': '·' };
            const icon = icons[item.importance] || '·';
            text += `${icon} ${item.content}\n\n`;
        });

        text += '-'.repeat(60) + '\n';
        text += `生成时间: ${newsData.metadata.generated_at}\n`;
        text += `新闻总数: ${newsData.metadata.total_news}\n`;

        return text;
    },

    /**
     * 下载文件
     */
    downloadFile(content, filename, mimeType = 'text/plain') {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    },

    /**
     * 导出为Markdown文件
     */
    exportMarkdown(newsData) {
        const md = this.toMarkdown(newsData);
        this.downloadFile(md, `ai-news-${newsData.date}.md`, 'text/markdown');
    },

    /**
     * 导出为文本文件
     */
    exportText(newsData) {
        const text = this.toPlainText(newsData);
        this.downloadFile(text, `ai-news-${newsData.date}.txt`, 'text/plain');
    },

    /**
     * 导出为JSON文件
     */
    exportJSON(newsData) {
        const json = JSON.stringify(newsData, null, 2);
        this.downloadFile(json, `ai-news-${newsData.date}.json`, 'application/json');
    }
};

// 统计工具
const StatsUtils = {
    /**
     * 统计新闻类别分布
     */
    countByCategory(newsList) {
        const counts = {};
        newsList.forEach(item => {
            const category = item.category || '未分类';
            counts[category] = (counts[category] || 0) + 1;
        });
        return counts;
    },

    /**
     * 统计重要性分布
     */
    countByImportance(newsList) {
        const counts = { critical: 0, high: 0, medium: 0 };
        newsList.forEach(item => {
            const importance = item.importance || 'medium';
            counts[importance]++;
        });
        return counts;
    },

    /**
     * 提取所有关键词
     */
    extractKeywords(newsList) {
        const keywords = new Set();
        newsList.forEach(item => {
            if (item.keywords) {
                item.keywords.forEach(kw => keywords.add(kw));
            }
        });
        return Array.from(keywords);
    },

    /**
     * 统计关键词频率
     */
    keywordFrequency(newsList) {
        const freq = {};
        newsList.forEach(item => {
            if (item.keywords) {
                item.keywords.forEach(kw => {
                    freq[kw] = (freq[kw] || 0) + 1;
                });
            }
        });
        return Object.entries(freq)
            .sort((a, b) => b[1] - a[1])
            .map(([keyword, count]) => ({ keyword, count }));
    }
};

// 搜索和过滤工具
const FilterUtils = {
    /**
     * 搜索新闻
     */
    search(newsList, query) {
        const lowerQuery = query.toLowerCase();
        return newsList.filter(item =>
            item.content.toLowerCase().includes(lowerQuery) ||
            (item.keywords && item.keywords.some(kw => kw.toLowerCase().includes(lowerQuery)))
        );
    },

    /**
     * 按重要性过滤
     */
    filterByImportance(newsList, importance) {
        return newsList.filter(item => item.importance === importance);
    },

    /**
     * 按类别过滤
     */
    filterByCategory(newsList, category) {
        return newsList.filter(item => item.category === category);
    },

    /**
     * 按关键词过滤
     */
    filterByKeyword(newsList, keyword) {
        return newsList.filter(item =>
            item.keywords && item.keywords.includes(keyword)
        );
    }
};

// UI 工具
const UIUtils = {
    /**
     * 显示加载动画
     */
    showLoading(element, message = '加载中...') {
        element.innerHTML = `
            <div class="loading">
                <div class="loading-spinner"></div>
                <p>${message}</p>
            </div>
        `;
    },

    /**
     * 显示错误消息
     */
    showError(element, message) {
        element.innerHTML = `
            <div class="error">
                <p>❌ ${message}</p>
            </div>
        `;
    },

    /**
     * 显示Toast提示
     */
    showToast(message, duration = 3000) {
        const toast = document.getElementById('toast');
        if (!toast) return;

        toast.textContent = message;
        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
        }, duration);
    },

    /**
     * 平滑滚动到元素
     */
    scrollToElement(element, offset = 0) {
        const top = element.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({ top, behavior: 'smooth' });
    },

    /**
     * 防抖函数
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * 节流函数
     */
    throttle(func, limit) {
        let inThrottle;
        return function (...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// 验证工具
const ValidationUtils = {
    /**
     * 验证JSON数据格式
     */
    validateNewsData(data) {
        const required = ['date', 'date_formatted', 'title', 'news', 'metadata'];
        const missing = required.filter(key => !(key in data));

        if (missing.length > 0) {
            return { valid: false, error: `缺少必需字段: ${missing.join(', ')}` };
        }

        if (!Array.isArray(data.news)) {
            return { valid: false, error: 'news 必须是数组' };
        }

        return { valid: true };
    },

    /**
     * 验证单条新闻格式
     */
    validateNewsItem(item) {
        const required = ['id', 'content', 'importance'];
        const missing = required.filter(key => !(key in item));

        if (missing.length > 0) {
            return { valid: false, error: `缺少必需字段: ${missing.join(', ')}` };
        }

        const validImportance = ['critical', 'high', 'medium'];
        if (!validImportance.includes(item.importance)) {
            return { valid: false, error: `无效的重要性级别: ${item.importance}` };
        }

        return { valid: true };
    }
};

// 导出所有工具（如果使用ES6模块）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        DateUtils,
        TextUtils,
        StorageUtils,
        ExportUtils,
        StatsUtils,
        FilterUtils,
        UIUtils,
        ValidationUtils
    };
}
