<template>
  <div class="news-viewer">
    <div class="card-container">
      <!-- 头部 -->
      <header class="header">
        <div class="header-line top"></div>
        <div class="header-content">
          <div class="header-left">
            <h1 class="title">{{ newsData?.title || 'AI 闪电快讯' }}</h1>
            <div class="title-subtitle">二十四小时内最值得关注的 AI 事件</div>
          </div>
          <div class="header-right">
            <div class="date-badge">{{ formattedDate }}</div>
          </div>
        </div>
        <div class="header-line bottom"></div>
      </header>

      <!-- 主内容 -->
      <main class="content">
        <!-- 追踪入口 -->
        <div class="tracker-entry">
          <RouterLink to="/timeline" class="tracker-link">◈ 话题追踪</RouterLink>
        </div>

        <!-- 头条区 -->
        <section class="headlines-section">
          <h2 class="section-title">H E A D L I N E S</h2>
          <div class="news-list">
            <NewsCard
              v-for="(news, index) in headlineNews"
              :key="news.id"
              :news="news"
              :type="'headline'"
              :index="index + 1"
            />
          </div>
        </section>

        <!-- 快讯区 -->
        <section class="brief-section">
          <h2 class="section-title">B R I E F</h2>
          <div class="news-list">
            <NewsCard
              v-for="news in briefNews"
              :key="news.id"
              :news="news"
              :type="'brief'"
            />
          </div>
        </section>
      </main>

      <!-- 底部 -->
      <footer class="footer">
        <div class="footer-tail">
          <div class="tail-section tail-logo-section">
            <img src="/logo.svg" alt="AI Daily" class="logo-image" />
          </div>
          <div class="tail-divider"></div>
          <div class="tail-section tail-qrcode-section">
            <img src="/qrcode-website.jpeg" alt="官网" class="qrcode-image" />
            <div class="qrcode-tip">www.CSAIA.sg</div>
          </div>
          <div class="tail-divider"></div>
          <div class="tail-section tail-qrcode-section">
            <img src="/qrcode.jpg" alt="公众号" class="qrcode-image" />
            <div class="qrcode-tip">公众号: CSAIA</div>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import NewsCard from './NewsCard.vue'

const newsData = ref(null)

const formattedDate = computed(() => {
  if (!newsData.value?.date) return ''
  const [year, month, day] = newsData.value.date.split('-')
  return `${year} 年 ${parseInt(month)} 月 ${parseInt(day)} 日`
})

const headlineNews = computed(() =>
  (newsData.value?.news || []).filter(n => n.importance === 'critical')
)

const briefNews = computed(() =>
  (newsData.value?.news || []).filter(n => n.importance === 'high' || n.importance === 'medium')
)

onMounted(async () => {
  // 先从 index.json 取最新日期
  try {
    const res = await fetch('/data/index.json')
    if (res.ok) {
      const index = await res.json()
      const dates = [...new Set(index.map(i => i.date))].sort((a, b) => b.localeCompare(a))
      if (dates.length) {
        const r = await fetch(`/data/${dates[0]}.json`)
        if (r.ok) { newsData.value = await r.json(); return }
      }
    }
  } catch (e) { /* fallback */ }

  // fallback：往前7天试探
  const pad = n => String(n).padStart(2, '0')
  for (let i = 0; i < 7; i++) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    const s = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
    try {
      const r = await fetch(`/data/${s}.json`)
      if (r.ok) { newsData.value = await r.json(); return }
    } catch (e) { /* continue */ }
  }
})
</script>

<style scoped>
.news-viewer {
  min-height: 100vh;
  padding: 2rem 1rem;
  background: #F5F5F5;
}

/* 卡片容器 */
.card-container {
  max-width: 520px;
  margin: 0 auto;
  background: #FFFFFF;
  border-radius: 12px;
  box-shadow:
    0 2px 8px rgba(0, 0, 0, 0.04),
    0 4px 16px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(201, 168, 106, 0.15);
  overflow: hidden;
}

/* 头部 */
.header {
  background: linear-gradient(135deg, #1A1410 0%, #44382A 100%);
  padding: 1rem 1.75rem;
  position: relative;
}

.header-line {
  height: 1px;
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(201, 168, 106, 0.3) 15%,
    rgba(201, 168, 106, 0.6) 50%,
    rgba(201, 168, 106, 0.3) 85%,
    transparent 100%
  );
}

.header-line.top {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
}

.header-line.bottom {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
}

.header-left {
  flex: 1;
  text-align: left;
}

.header-right {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.title {
  font-size: 1.75rem;
  font-weight: 600;
  background: linear-gradient(135deg, #E6D5B8 0%, #C9A86A 50%, #B8924D 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  letter-spacing: 0.03em;
  line-height: 1.2;
}

.title-subtitle {
  font-size: 0.625rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: rgba(201, 168, 106, 0.85);
  margin-top: 0.125rem;
  text-transform: none;
}

.date-badge {
  display: inline-block;
  padding: 0.3125rem 0.875rem;
  border: 1px solid rgba(201, 168, 106, 0.35);
  border-radius: 14px;
  color: #C9A86A;
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  background: rgba(201, 168, 106, 0.08);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* 内容区 */
.content {
  padding: 2rem 1.75rem;
  position: relative;
}

/* 水印 */
.content::before {
  content: '中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA    中新人工智能协会 CSAIA';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 500;
  color: rgba(201, 168, 106, 0.07);
  line-height: 3.25;
  white-space: pre-wrap;
  word-spacing: 3rem;
  transform: rotate(-45deg);
  pointer-events: none;
  user-select: none;
  z-index: 0;
  overflow: hidden;
}

.content > * {
  position: relative;
  z-index: 1;
}

/* 区域标题 */
.section-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.25em;
  color: #B8924D;
  margin: 0 0 1.25rem;
  text-transform: uppercase;
}

.section-title::before {
  content: '';
  width: 40px;
  height: 1px;
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(201, 168, 106, 0.2) 30%,
    rgba(201, 168, 106, 0.5) 70%,
    rgba(184, 146, 77, 0.8) 100%
  );
}

.section-title::after {
  content: '';
  width: 40px;
  height: 1px;
  background: linear-gradient(90deg,
    rgba(184, 146, 77, 0.8) 0%,
    rgba(201, 168, 106, 0.5) 30%,
    rgba(201, 168, 106, 0.2) 70%,
    transparent 100%
  );
}

/* 追踪入口 */
.tracker-entry {
  text-align: right;
  margin-bottom: 1.25rem;
}

.tracker-link {
  font-size: 0.68rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  color: rgba(184, 146, 77, 0.65);
  text-decoration: none;
  border: 1px solid rgba(201, 168, 106, 0.18);
  padding: 0.25rem 0.7rem;
  border-radius: 12px;
  transition: all 0.2s;
}

.tracker-link:hover {
  color: #B8924D;
  border-color: rgba(201, 168, 106, 0.4);
  background: rgba(201, 168, 106, 0.05);
}

/* 头条区 */
.headlines-section {
  margin-bottom: 2rem;
}

/* 快讯区 */
.brief-section {
  margin-top: 2rem;
}

/* 新闻列表 */
.news-list {
  /* 由子组件控制间距 */
}

/* 底部 */
.footer {
  padding: 0;
  background: #FFFFFF;
}

.footer-tail {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  background: linear-gradient(135deg, #1A1410 0%, #44382A 100%);
  padding: 1rem 1.75rem;
  margin: 0;
  border-radius: 0 0 12px 12px;
}

.tail-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.tail-logo-section {
  gap: 0;
}

.tail-qrcode-section {
  gap: 0.4rem;
}

.tail-divider {
  width: 1px;
  height: 4rem;
  background: linear-gradient(180deg,
    transparent 0%,
    rgba(201, 168, 106, 0.2) 10%,
    rgba(201, 168, 106, 0.5) 50%,
    rgba(201, 168, 106, 0.2) 90%,
    transparent 100%
  );
}

.logo-image {
  height: 3rem;
  width: auto;
  margin-top: 0.5rem;
}

.logo-image:hover {
  opacity: 1;
}

.qrcode-image {
  width: 4rem;
  height: 4rem;
  border-radius: 8px;
  border: 1px solid rgba(201, 168, 106, 0.25);
  box-shadow:
    0 0 0 1px rgba(201, 168, 106, 0.08) inset,
    0 4px 16px rgba(0, 0, 0, 0.25),
    0 2px 4px rgba(0, 0, 0, 0.15);
  background: #FFFFFF;
  padding: 0.15rem;
  transition: all 0.3s ease;
}

.qrcode-image:hover {
  box-shadow:
    0 0 0 1px rgba(201, 168, 106, 0.15) inset,
    0 6px 20px rgba(0, 0, 0, 0.3),
    0 3px 6px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.qrcode-tip {
  font-size: 0.65rem;
  font-weight: 500;
  color: rgba(230, 213, 184, 0.9);
  letter-spacing: 0.02em;
  text-align: center;
  line-height: 1.35;
  max-width: 5rem;
}
</style>
