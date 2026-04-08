<template>
  <div class="timeline-viewer">
    <!-- 顶部导航 -->
    <header class="tl-header">
      <div class="tl-header-inner">
        <div class="tl-branding">
          <span class="tl-logo-text">AI 追踪</span>
          <span class="tl-logo-sub">话题追踪 · 日报归档</span>
        </div>
        <RouterLink to="/" class="back-link">← 今日快讯</RouterLink>
      </div>
    </header>

    <div class="tl-body">
      <!-- ── 侧边栏 ── -->
      <aside class="tl-sidebar">
        <!-- Tab 切换 -->
        <div class="sb-tabs">
          <button
            class="sb-tab"
            :class="{ active: sidebarTab === 'topics' }"
            @click="sidebarTab = 'topics'"
          >话题</button>
          <button
            class="sb-tab"
            :class="{ active: sidebarTab === 'archive' }"
            @click="sidebarTab = 'archive'"
          >归档</button>
        </div>

        <!-- 话题 Tab -->
        <template v-if="sidebarTab === 'topics'">
          <section class="sb-section">
            <div class="sb-title">C A T E G O R Y</div>
            <div class="category-list">
              <button
                v-for="cat in categories"
                :key="cat.name"
                class="cat-btn"
                :class="{ active: activeFilter?.type === 'category' && activeFilter.value === cat.name }"
                @click="selectFilter('category', cat.name)"
              >
                <span>{{ cat.name }}</span>
                <span class="count-badge">{{ cat.count }}</span>
              </button>
            </div>
          </section>

          <section class="sb-section">
            <div class="sb-title">T O P I C S</div>
            <input v-model="search" class="search-input" placeholder="搜索话题..." />
            <div class="tag-list">
              <button
                v-for="tag in filteredKeywords"
                :key="tag.name"
                class="tag-btn"
                :class="{ active: activeFilter?.type === 'keyword' && activeFilter.value === tag.name }"
                @click="selectFilter('keyword', tag.name)"
              >
                <span class="tag-name">{{ tag.name }}</span>
                <span class="count-badge">{{ tag.count }}</span>
              </button>
            </div>
          </section>
        </template>

        <!-- 归档 Tab -->
        <template v-else>
          <section class="sb-section">
            <div class="sb-title">A R C H I V E</div>
            <div class="archive-months">
              <div
                v-for="group in archiveByMonth"
                :key="group.month"
                class="month-group"
              >
                <div class="month-label">{{ group.label }}</div>
                <div class="date-chips">
                  <button
                    v-for="date in group.dates"
                    :key="date"
                    class="date-chip"
                    :class="{ active: selectedArchiveDate === date }"
                    @click="openArchiveDate(date)"
                  >{{ date.slice(5) }}</button>
                </div>
              </div>
            </div>
          </section>
        </template>
      </aside>

      <!-- ── 主内容区 ── -->
      <main class="tl-main">

        <!-- 空状态 -->
        <div v-if="mainMode === 'empty'" class="empty-state">
          <div class="empty-icon">◈</div>
          <p class="empty-title">选择话题或日期</p>
          <p class="empty-sub">追踪事件发展 · 翻阅历史日报</p>
        </div>

        <!-- ── 话题时间线 ── -->
        <template v-else-if="mainMode === 'timeline'">
          <div class="tl-meta-bar">
            <span class="active-label">{{ activeFilter.value }}</span>
            <span class="tl-stats">共 {{ totalItems }} 条 · {{ timelineGroups.length }} 天</span>
          </div>

          <div v-if="totalItems === 0" class="no-results">该话题暂无相关记录</div>

          <div v-else class="timeline">
            <div v-for="group in timelineGroups" :key="group.date" class="date-group">
              <div class="date-divider">
                <div class="date-line"></div>
                <span class="date-text">{{ formatDate(group.date) }}</span>
                <div class="date-line"></div>
              </div>
              <div class="group-items">
                <div
                  v-for="item in group.items"
                  :key="item.date + '-' + item.id"
                  class="tl-item"
                >
                  <div class="tl-item-row" @click="toggleExpand(item)">
                    <span class="imp-dot" :class="item.importance"></span>
                    <span class="tl-item-title">{{ item.title }}</span>
                    <span class="expand-icon">{{ expandedKey === item.date + '-' + item.id ? '▲' : '▼' }}</span>
                  </div>
                  <Transition name="slide">
                    <div v-if="expandedKey === item.date + '-' + item.id" class="tl-item-body">
                      <div v-if="loadingKey === item.date + '-' + item.id" class="loading-dots">
                        <span>·</span><span>·</span><span>·</span>
                      </div>
                      <template v-else-if="contentCache[item.date + '-' + item.id]">
                        <p class="tl-content">{{ contentCache[item.date + '-' + item.id].content }}</p>
                        <div class="tl-content-footer">
                          <span class="tl-category-tag">{{ item.category }}</span>
                          <div class="tl-source-row">
                            <span class="tl-source">{{ contentCache[item.date + '-' + item.id].source }}</span>
                            <a
                              v-if="contentCache[item.date + '-' + item.id].url"
                              :href="contentCache[item.date + '-' + item.id].url"
                              target="_blank" class="tl-link" @click.stop
                            >原文 →</a>
                          </div>
                        </div>
                        <div v-if="item.keywords?.length" class="tl-keywords">
                          <span
                            v-for="kw in item.keywords" :key="kw"
                            class="kw-chip"
                            :class="{ 'kw-active': activeFilter?.value === kw }"
                            @click.stop="selectFilter('keyword', kw)"
                          >{{ kw }}</span>
                        </div>
                      </template>
                      <div v-else class="no-results" style="padding:0.5rem">加载失败</div>
                    </div>
                  </Transition>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- ── 日报归档视图 ── -->
        <template v-else-if="mainMode === 'archive'">
          <div v-if="archiveLoading" class="loading-full">
            <div class="loading-dots large"><span>·</span><span>·</span><span>·</span></div>
          </div>
          <template v-else-if="archiveNews">
            <!-- 日报头部 -->
            <div class="archive-header">
              <div class="archive-date-label">{{ formatDate(selectedArchiveDate) }}</div>
              <div class="archive-count">
                {{ archiveNews.filter(n => n.importance === 'critical').length }} 条头条
                · {{ archiveNews.filter(n => n.importance !== 'critical').length }} 条快讯
              </div>
            </div>

            <!-- 头条 -->
            <section class="archive-section" v-if="archiveHeadlines.length">
              <div class="archive-section-title">H E A D L I N E S</div>
              <div class="archive-news-list">
                <div
                  v-for="(item, idx) in archiveHeadlines"
                  :key="item.id"
                  class="archive-headline"
                >
                  <div class="archive-num">{{ String(idx + 1).padStart(2, '0') }}</div>
                  <div class="archive-headline-body">
                    <div class="archive-headline-title">{{ item.title }}</div>
                    <p class="archive-headline-content">{{ item.content }}</p>
                    <div class="archive-item-footer">
                      <span class="tl-category-tag">{{ item.category }}</span>
                      <div class="tl-source-row">
                        <span class="tl-source">{{ item.source }}</span>
                        <a v-if="item.url" :href="item.url" target="_blank" class="tl-link">原文 →</a>
                      </div>
                    </div>
                    <div v-if="item.keywords?.length" class="tl-keywords">
                      <span
                        v-for="kw in item.keywords" :key="kw"
                        class="kw-chip"
                        @click="switchToTopicAndFilter(kw)"
                      >{{ kw }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <!-- 快讯 -->
            <section class="archive-section" v-if="archiveBriefs.length">
              <div class="archive-section-title">B R I E F</div>
              <div class="archive-news-list">
                <div
                  v-for="item in archiveBriefs"
                  :key="item.id"
                  class="archive-brief"
                >
                  <span class="brief-bullet">✦</span>
                  <div class="archive-brief-body">
                    <span class="archive-brief-title">{{ item.title }}：</span>
                    <span class="archive-brief-content">{{ item.content }}</span>
                    <div class="archive-item-footer">
                      <span class="tl-category-tag">{{ item.category }}</span>
                      <div class="tl-source-row">
                        <span class="tl-source">{{ item.source }}</span>
                        <a v-if="item.url" :href="item.url" target="_blank" class="tl-link">原文 →</a>
                      </div>
                    </div>
                    <div v-if="item.keywords?.length" class="tl-keywords">
                      <span
                        v-for="kw in item.keywords" :key="kw"
                        class="kw-chip"
                        @click="switchToTopicAndFilter(kw)"
                      >{{ kw }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </template>
          <div v-else class="no-results">该日期数据加载失败</div>
        </template>

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { RouterLink } from 'vue-router'

// ── 状态 ──────────────────────────────────────────────
const index = ref([])
const sidebarTab = ref('topics')         // 'topics' | 'archive'
const activeFilter = ref(null)           // { type, value } — 话题模式
const search = ref('')
const expandedKey = ref(null)
const loadingKey = ref(null)
const contentCache = reactive({})
const dateCache = {}

const selectedArchiveDate = ref(null)    // 归档模式选中日期
const archiveNews = ref(null)            // 当天完整 news[]
const archiveLoading = ref(false)

// ── 主区渲染模式 ──────────────────────────────────────
const mainMode = computed(() => {
  if (selectedArchiveDate.value && sidebarTab.value === 'archive') return 'archive'
  if (activeFilter.value && sidebarTab.value === 'topics') return 'timeline'
  return 'empty'
})

// ── 初始化 ────────────────────────────────────────────
onMounted(async () => {
  try {
    const res = await fetch('/data/index.json')
    if (res.ok) index.value = await res.json()
  } catch (e) {
    console.error('无法加载 index.json', e)
  }
})

// ── 话题 Tab 计算属性 ─────────────────────────────────

const allKeywords = computed(() => {
  const counts = {}
  for (const item of index.value)
    for (const kw of item.keywords || [])
      counts[kw] = (counts[kw] || 0) + 1
  return Object.entries(counts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
})

const filteredKeywords = computed(() => {
  const q = search.value.trim().toLowerCase()
  const list = q ? allKeywords.value.filter(t => t.name.toLowerCase().includes(q)) : allKeywords.value
  return list.slice(0, 100)
})

const categories = computed(() => {
  const counts = {}
  for (const item of index.value)
    if (item.category) counts[item.category] = (counts[item.category] || 0) + 1
  return Object.entries(counts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
})

const filteredItems = computed(() => {
  if (!activeFilter.value) return []
  const { type, value } = activeFilter.value
  return type === 'keyword'
    ? index.value.filter(item => item.keywords?.includes(value))
    : index.value.filter(item => item.category === value)
})

const totalItems = computed(() => filteredItems.value.length)

const timelineGroups = computed(() => {
  const byDate = {}
  for (const item of filteredItems.value) {
    if (!byDate[item.date]) byDate[item.date] = []
    byDate[item.date].push(item)
  }
  return Object.entries(byDate)
    .sort(([a], [b]) => b.localeCompare(a))
    .map(([date, items]) => ({ date, items }))
})

// ── 归档 Tab 计算属性 ─────────────────────────────────

// 所有日期去重降序
const availableDates = computed(() =>
  [...new Set(index.value.map(i => i.date))].sort((a, b) => b.localeCompare(a))
)

// 按年月分组
const archiveByMonth = computed(() => {
  const groups = {}
  for (const date of availableDates.value) {
    const ym = date.slice(0, 7)  // 'YYYY-MM'
    if (!groups[ym]) groups[ym] = []
    groups[ym].push(date)
  }
  return Object.entries(groups)
    .sort(([a], [b]) => b.localeCompare(a))
    .map(([month, dates]) => {
      const [y, m] = month.split('-')
      return { month, label: `${y} 年 ${parseInt(m)} 月`, dates }
    })
})

const archiveHeadlines = computed(() =>
  (archiveNews.value || []).filter(n => n.importance === 'critical')
)
const archiveBriefs = computed(() =>
  (archiveNews.value || []).filter(n => n.importance !== 'critical')
)

// ── 方法 ─────────────────────────────────────────────

const selectFilter = (type, value) => {
  activeFilter.value =
    activeFilter.value?.type === type && activeFilter.value?.value === value
      ? null
      : { type, value }
  expandedKey.value = null
  sidebarTab.value = 'topics'
}

const toggleExpand = async (item) => {
  const key = item.date + '-' + item.id
  if (expandedKey.value === key) { expandedKey.value = null; return }
  expandedKey.value = key
  if (contentCache[key]) return

  if (!dateCache[item.date]) {
    loadingKey.value = key
    try {
      const res = await fetch(`/data/${item.date}.json`)
      if (res.ok) dateCache[item.date] = (await res.json()).news || []
    } catch (e) {
      console.error(`加载 ${item.date}.json 失败`, e)
    } finally {
      loadingKey.value = null
    }
  }

  const full = (dateCache[item.date] || []).find(n => n.id === item.id)
  if (full) contentCache[key] = full
}

const openArchiveDate = async (date) => {
  selectedArchiveDate.value = date
  archiveNews.value = null

  // 优先用已有缓存
  if (dateCache[date]) {
    archiveNews.value = dateCache[date]
    return
  }

  archiveLoading.value = true
  try {
    const res = await fetch(`/data/${date}.json`)
    if (res.ok) {
      const data = await res.json()
      dateCache[date] = data.news || []
      archiveNews.value = dateCache[date]
    }
  } catch (e) {
    console.error(`加载 ${date}.json 失败`, e)
  } finally {
    archiveLoading.value = false
  }
}

// 从日报关键词跳转到话题追踪
const switchToTopicAndFilter = (kw) => {
  sidebarTab.value = 'topics'
  selectedArchiveDate.value = null
  activeFilter.value = { type: 'keyword', value: kw }
  expandedKey.value = null
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const [year, month, day] = dateStr.split('-')
  return `${year} 年 ${parseInt(month)} 月 ${parseInt(day)} 日`
}
</script>

<style scoped>
/* ─── 整体布局 ─────────────────────────────────────── */
.timeline-viewer {
  min-height: 100vh;
  background: #F0EDE8;
  display: flex;
  flex-direction: column;
}

/* ─── 顶部导航 ─────────────────────────────────────── */
.tl-header {
  background: linear-gradient(135deg, #1A1410 0%, #44382A 100%);
  border-bottom: 1px solid rgba(201, 168, 106, 0.2);
  position: sticky;
  top: 0;
  z-index: 20;
}

.tl-header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.875rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tl-branding {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
}

.tl-logo-text {
  font-size: 1.25rem;
  font-weight: 600;
  background: linear-gradient(135deg, #E6D5B8 0%, #C9A86A 50%, #B8924D 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.03em;
}

.tl-logo-sub {
  font-size: 0.65rem;
  font-weight: 500;
  letter-spacing: 0.06em;
  color: rgba(201, 168, 106, 0.55);
}

.back-link {
  font-size: 0.8rem;
  color: rgba(201, 168, 106, 0.75);
  text-decoration: none;
  border: 1px solid rgba(201, 168, 106, 0.2);
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  transition: all 0.2s;
}

.back-link:hover {
  color: #C9A86A;
  border-color: rgba(201, 168, 106, 0.4);
}

/* ─── 主体区 ───────────────────────────────────────── */
.tl-body {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 1.5rem 2rem 3rem;
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

/* ─── 侧边栏 ───────────────────────────────────────── */
.tl-sidebar {
  width: 240px;
  flex-shrink: 0;
  position: sticky;
  top: calc(52px + 1.5rem);
  max-height: calc(100vh - 52px - 3rem);
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(201, 168, 106, 0.2) transparent;
}

.tl-sidebar::-webkit-scrollbar { width: 4px; }
.tl-sidebar::-webkit-scrollbar-thumb {
  background: rgba(201, 168, 106, 0.2);
  border-radius: 2px;
}

/* Tab 切换 */
.sb-tabs {
  display: flex;
  background: #FFFFFF;
  border-radius: 10px;
  border: 1px solid rgba(201, 168, 106, 0.12);
  padding: 0.25rem;
  margin-bottom: 0.75rem;
  gap: 0.25rem;
}

.sb-tab {
  flex: 1;
  padding: 0.45rem 0;
  border: none;
  background: transparent;
  border-radius: 7px;
  font-size: 0.82rem;
  font-weight: 500;
  color: #A89478;
  cursor: pointer;
  transition: all 0.15s;
}

.sb-tab.active {
  background: linear-gradient(135deg, #1A1410 0%, #44382A 100%);
  color: #C9A86A;
}

.sb-tab:not(.active):hover {
  color: #5C5142;
  background: rgba(201, 168, 106, 0.06);
}

/* 通用 section */
.sb-section {
  background: #FFFFFF;
  border-radius: 10px;
  border: 1px solid rgba(201, 168, 106, 0.12);
  padding: 1rem;
  margin-bottom: 0.75rem;
}

.sb-title {
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.2em;
  color: #B8924D;
  margin-bottom: 0.75rem;
}

/* 分类 */
.category-list {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.cat-btn {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0.4rem 0.55rem;
  border: none;
  background: transparent;
  border-radius: 6px;
  font-size: 0.82rem;
  color: #5C5142;
  cursor: pointer;
  transition: all 0.15s;
  text-align: left;
}

.cat-btn:hover { background: rgba(201, 168, 106, 0.07); color: #3D3529; }
.cat-btn.active { background: rgba(201, 168, 106, 0.12); color: #B8924D; font-weight: 500; }

/* 搜索框 */
.search-input {
  width: 100%;
  padding: 0.4rem 0.6rem;
  border: 1px solid rgba(201, 168, 106, 0.2);
  border-radius: 6px;
  background: #FAFAF8;
  font-size: 0.8rem;
  color: #3D3529;
  outline: none;
  margin-bottom: 0.5rem;
  transition: border-color 0.2s;
}

.search-input:focus { border-color: rgba(201, 168, 106, 0.5); }

/* 关键词 */
.tag-list {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  max-height: 380px;
  overflow-y: auto;
  scrollbar-width: thin;
}

.tag-btn {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0.32rem 0.55rem;
  border: none;
  background: transparent;
  border-radius: 5px;
  font-size: 0.8rem;
  color: #5C5142;
  cursor: pointer;
  transition: all 0.15s;
  text-align: left;
}

.tag-btn:hover { background: rgba(201, 168, 106, 0.07); color: #3D3529; }
.tag-btn.active { background: rgba(201, 168, 106, 0.12); color: #B8924D; font-weight: 500; }
.tag-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-right: 0.5rem; }
.count-badge { flex-shrink: 0; font-size: 0.67rem; color: rgba(184, 146, 77, 0.55); font-variant-numeric: tabular-nums; }

/* ── 归档日历 ─────────────────────────────────────── */
.archive-months {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.month-group { }

.month-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: #B8924D;
  letter-spacing: 0.04em;
  margin-bottom: 0.45rem;
}

.date-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.date-chip {
  padding: 0.25rem 0.55rem;
  border: 1px solid rgba(201, 168, 106, 0.2);
  border-radius: 6px;
  background: #FAFAF8;
  font-size: 0.75rem;
  color: #5C5142;
  cursor: pointer;
  transition: all 0.15s;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.02em;
}

.date-chip:hover {
  background: rgba(201, 168, 106, 0.09);
  color: #3D3529;
  border-color: rgba(201, 168, 106, 0.35);
}

.date-chip.active {
  background: linear-gradient(135deg, #1A1410 0%, #44382A 100%);
  color: #C9A86A;
  border-color: rgba(201, 168, 106, 0.4);
  font-weight: 500;
}

/* ─── 主内容区 ─────────────────────────────────────── */
.tl-main {
  flex: 1;
  min-width: 0;
  background: #FFFFFF;
  border-radius: 10px;
  border: 1px solid rgba(201, 168, 106, 0.12);
  padding: 1.5rem;
  min-height: 480px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 0.5rem;
}

.empty-icon { font-size: 2.5rem; color: rgba(201, 168, 106, 0.3); margin-bottom: 0.5rem; }
.empty-title { font-size: 1rem; font-weight: 500; color: #8C7A5E; }
.empty-sub { font-size: 0.82rem; color: #A89478; }
.no-results { text-align: center; color: #A89478; font-size: 0.875rem; padding: 3rem; }

/* 全屏 loading */
.loading-full {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

/* meta 栏 */
.tl-meta-bar {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(201, 168, 106, 0.1);
}

.active-label { font-size: 1.1rem; font-weight: 600; color: #1A1410; letter-spacing: -0.01em; }
.tl-stats { font-size: 0.78rem; color: #A89478; }

/* ─── 话题时间线 ───────────────────────────────────── */
.timeline { display: flex; flex-direction: column; }
.date-group { margin-bottom: 1.75rem; }

.date-divider {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.date-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, rgba(201,168,106,0.08), rgba(201,168,106,0.25), rgba(201,168,106,0.08));
}

.date-text {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: #B8924D;
  white-space: nowrap;
}

.group-items { display: flex; flex-direction: column; gap: 0.375rem; }

.tl-item {
  border-radius: 7px;
  border: 1px solid rgba(201, 168, 106, 0.08);
  background: #FAFAF8;
  overflow: hidden;
  transition: border-color 0.2s;
}

.tl-item:hover { border-color: rgba(201, 168, 106, 0.22); }

.tl-item-row {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.625rem 0.875rem;
  cursor: pointer;
  user-select: none;
}

.tl-item-row:hover .tl-item-title { color: #2C2416; }

.imp-dot { flex-shrink: 0; width: 7px; height: 7px; border-radius: 50%; }
.imp-dot.critical { background: #C0392B; box-shadow: 0 0 4px rgba(192,57,43,0.4); }
.imp-dot.high { background: #C9A86A; box-shadow: 0 0 4px rgba(201,168,106,0.4); }
.imp-dot.medium { background: #BDC3C7; }

.tl-item-title { flex: 1; font-size: 0.875rem; font-weight: 500; color: #3D3529; line-height: 1.4; transition: color 0.15s; }
.expand-icon { flex-shrink: 0; font-size: 0.55rem; color: rgba(201,168,106,0.5); }

.tl-item-body {
  padding: 0.75rem 0.875rem 0.875rem;
  border-top: 1px solid rgba(201, 168, 106, 0.1);
  background: #FFFFFF;
}

/* loading dots */
.loading-dots {
  text-align: center;
  padding: 0.5rem;
}

.loading-dots span {
  display: inline-block;
  animation: blink 1.2s infinite;
  font-size: 1.4rem;
  color: rgba(201, 168, 106, 0.5);
  line-height: 1;
}

.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }
.loading-dots.large span { font-size: 2rem; }

@keyframes blink {
  0%, 80%, 100% { opacity: 0.2; }
  40% { opacity: 1; }
}

.tl-content { font-size: 0.875rem; color: #4A3F33; line-height: 1.75; margin: 0 0 0.75rem; }

.tl-content-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.tl-category-tag {
  font-size: 0.68rem;
  color: rgba(184,146,77,0.7);
  border: 1px solid rgba(201,168,106,0.2);
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
}

.tl-source-row { display: flex; align-items: center; gap: 0.75rem; }
.tl-source { font-size: 0.72rem; color: #A89478; }
.tl-link { font-size: 0.72rem; color: #B8924D; text-decoration: none; transition: color 0.15s; }
.tl-link:hover { color: #C9A86A; }

.tl-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-top: 0.625rem;
  padding-top: 0.625rem;
  border-top: 1px solid rgba(201,168,106,0.08);
}

.kw-chip {
  font-size: 0.68rem;
  color: #8C7A5E;
  background: rgba(201,168,106,0.07);
  border: 1px solid rgba(201,168,106,0.15);
  border-radius: 10px;
  padding: 0.15rem 0.55rem;
  cursor: pointer;
  transition: all 0.15s;
  user-select: none;
}

.kw-chip:hover { background: rgba(201,168,106,0.14); color: #B8924D; border-color: rgba(201,168,106,0.3); }
.kw-active { background: rgba(201,168,106,0.18); color: #B8924D; border-color: rgba(201,168,106,0.4); font-weight: 500; }

/* ─── 日报归档视图 ─────────────────────────────────── */
.archive-header {
  margin-bottom: 1.75rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(201, 168, 106, 0.1);
}

.archive-date-label {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1A1410;
  letter-spacing: -0.01em;
  margin-bottom: 0.25rem;
}

.archive-count {
  font-size: 0.78rem;
  color: #A89478;
}

.archive-section {
  margin-bottom: 2rem;
}

.archive-section-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.22em;
  color: #B8924D;
  margin-bottom: 1.25rem;
}

.archive-section-title::before,
.archive-section-title::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(201,168,106,0.3), transparent);
}

.archive-news-list { display: flex; flex-direction: column; gap: 1.25rem; }

/* 头条条目 */
.archive-headline {
  display: flex;
  gap: 1rem;
}

.archive-num {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
  color: #B8924D;
  background: rgba(201,168,106,0.08);
  border-radius: 50%;
  border: 1.5px solid rgba(201,168,106,0.2);
  margin-top: 0.1rem;
  flex-shrink: 0;
}

.archive-headline-body { flex: 1; }

.archive-headline-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1A1410;
  line-height: 1.4;
  margin-bottom: 0.375rem;
}

.archive-headline-content {
  font-size: 0.875rem;
  color: #5C5142;
  line-height: 1.75;
  margin: 0 0 0.625rem;
}

.archive-item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 0.375rem;
}

/* 快讯条目 */
.archive-brief {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.brief-bullet {
  flex-shrink: 0;
  font-size: 1rem;
  color: #C9A86A;
  margin-top: 0.1rem;
  line-height: 1.6;
}

.archive-brief-body { flex: 1; }

.archive-brief-title {
  font-weight: 600;
  font-size: 0.875rem;
  color: #3D3529;
}

.archive-brief-content {
  font-size: 0.875rem;
  color: #5C5142;
  line-height: 1.7;
}

/* ─── 展开动画 ─────────────────────────────────────── */
.slide-enter-active, .slide-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}

.slide-enter-from, .slide-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.slide-enter-to, .slide-leave-from {
  opacity: 1;
  max-height: 600px;
}

/* ─── 响应式 ───────────────────────────────────────── */
@media (max-width: 768px) {
  .tl-body {
    flex-direction: column;
    padding: 1rem;
  }

  .tl-sidebar {
    width: 100%;
    position: static;
    max-height: none;
  }

  .tl-header-inner { padding: 0.75rem 1rem; }
  .tl-main { padding: 1rem; }
}
</style>
