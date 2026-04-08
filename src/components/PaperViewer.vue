<template>
  <div class="paper-viewer">
    <div class="card-container">
      <!-- 头部 -->
      <header class="header">
        <div class="header-line top"></div>
        <div class="header-content">
          <div class="header-left">
            <h1 class="title">AI 前沿论文</h1>
            <div class="title-subtitle">每周精选 arxiv CS/AI 领域重要研究</div>
          </div>
          <div class="header-right">
            <div class="date-badge">{{ weekLabel }}</div>
          </div>
        </div>
        <div class="header-line bottom"></div>
      </header>

      <!-- 加载中 -->
      <div v-if="loading" class="state-msg">加载中…</div>

      <!-- 无数据 -->
      <div v-else-if="!paperData" class="state-msg">本周暂无论文数据</div>

      <!-- 主内容 -->
      <main v-else class="content">
        <!-- Featured：critical -->
        <section v-if="featuredPapers.length" class="papers-section">
          <h2 class="section-title">F E A T U R E D</h2>
          <div class="papers-list">
            <PaperCard
              v-for="(paper, index) in featuredPapers"
              :key="paper.id"
              :paper="paper"
              :index="index + 1"
            />
          </div>
        </section>

        <!-- Notable：high -->
        <section v-if="notablePapers.length" class="papers-section">
          <h2 class="section-title">N O T A B L E</h2>
          <div class="papers-list">
            <PaperCard
              v-for="paper in notablePapers"
              :key="paper.id"
              :paper="paper"
            />
          </div>
        </section>

        <!-- Brief：medium -->
        <section v-if="briefPapers.length" class="papers-section">
          <h2 class="section-title">B R I E F S</h2>
          <div class="papers-list">
            <PaperCard
              v-for="paper in briefPapers"
              :key="paper.id"
              :paper="paper"
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
import PaperCard from './PaperCard.vue'

const paperData = ref(null)
const loading = ref(true)

// 周标签（如 "2026 年第 15 周"）
const weekLabel = computed(() => {
  if (!paperData.value?.metadata) return ''
  const { week } = paperData.value.metadata
  if (!week) return ''
  // week 格式: "2026-W15"
  const [year, w] = week.split('-W')
  return `${year} 年第 ${w} 周`
})

// 按 importance 分组
const featuredPapers = computed(() =>
  paperData.value?.papers?.filter(p => p.importance === 'critical') ?? []
)
const notablePapers = computed(() =>
  paperData.value?.papers?.filter(p => p.importance === 'high') ?? []
)
const briefPapers = computed(() =>
  paperData.value?.papers?.filter(p => p.importance === 'medium') ?? []
)

// 找最近的周一（含今天如果是周一）
const getRecentMondays = () => {
  const mondays = []
  const today = new Date()
  const dow = today.getDay() // 0=Sun,1=Mon,...
  const diffToLastMonday = dow === 0 ? 6 : dow - 1
  const lastMonday = new Date(today)
  lastMonday.setDate(today.getDate() - diffToLastMonday)

  for (let i = 0; i < 5; i++) {
    const d = new Date(lastMonday)
    d.setDate(lastMonday.getDate() - i * 7)
    const y = d.getFullYear()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    mondays.push(`${y}-${m}-${day}`)
  }
  return mondays
}

const loadPapers = async () => {
  loading.value = true
  const mondays = getRecentMondays()

  for (const dateStr of mondays) {
    try {
      const res = await fetch(`/papers/${dateStr}.json`)
      if (res.ok) {
        paperData.value = await res.json()
        break
      }
    } catch {
      // 继续尝试
    }
  }

  loading.value = false
}

onMounted(loadPapers)
</script>

<style scoped>
.paper-viewer {
  min-height: 100vh;
  padding: 2rem 1rem;
  background: #F5F5F5;
}

.card-container {
  max-width: 520px;
  margin: 0 auto;
  background: #FFFFFF;
  border-radius: 12px;
  box-shadow:
    0 2px 8px rgba(0,0,0,0.04),
    0 4px 16px rgba(0,0,0,0.08);
  border: 1px solid rgba(201,168,106,0.15);
  overflow: hidden;
}

/* 头部（与 NewsViewer 一致） */
.header {
  background: linear-gradient(135deg, #1A1410 0%, #44382A 100%);
  padding: 1rem 1.75rem;
  position: relative;
}

.header-line {
  height: 1px;
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(201,168,106,0.3) 15%,
    rgba(201,168,106,0.6) 50%,
    rgba(201,168,106,0.3) 85%,
    transparent 100%
  );
}
.header-line.top { position: absolute; top: 0; left: 0; right: 0; }
.header-line.bottom { position: absolute; bottom: 0; left: 0; right: 0; }

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
}
.header-left { flex: 1; text-align: left; }
.header-right { flex-shrink: 0; display: flex; align-items: center; }

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
  color: rgba(201,168,106,0.85);
  margin-top: 0.125rem;
}

.date-badge {
  display: inline-block;
  padding: 0.3125rem 0.875rem;
  border: 1px solid rgba(201,168,106,0.35);
  border-radius: 14px;
  color: #C9A86A;
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  background: rgba(201,168,106,0.08);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
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
  top: 0; left: 0;
  width: 100%; height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 500;
  color: rgba(201,168,106,0.07);
  line-height: 3.25;
  white-space: pre-wrap;
  word-spacing: 3rem;
  transform: rotate(-45deg);
  pointer-events: none;
  user-select: none;
  z-index: 0;
  overflow: hidden;
}

.content > * { position: relative; z-index: 1; }

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
}

.section-title::before {
  content: '';
  width: 40px; height: 1px;
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(201,168,106,0.2) 30%,
    rgba(201,168,106,0.5) 70%,
    rgba(184,146,77,0.8) 100%
  );
}

.section-title::after {
  content: '';
  width: 40px; height: 1px;
  background: linear-gradient(90deg,
    rgba(184,146,77,0.8) 0%,
    rgba(201,168,106,0.5) 30%,
    rgba(201,168,106,0.2) 70%,
    transparent 100%
  );
}

.papers-section { margin-bottom: 2rem; }
.papers-section:last-child { margin-bottom: 0; }

/* 状态提示 */
.state-msg {
  padding: 3rem 2rem;
  text-align: center;
  color: #9A876A;
  font-size: 0.875rem;
}

/* 底部（与 NewsViewer 一致） */
.footer { padding: 0; background: #FFFFFF; }

.footer-tail {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  background: linear-gradient(135deg, #1A1410 0%, #44382A 100%);
  padding: 1rem 1.75rem;
  border-radius: 0 0 12px 12px;
}

.tail-section { display: flex; flex-direction: column; align-items: center; gap: 0.5rem; }
.tail-logo-section { gap: 0; }
.tail-qrcode-section { gap: 0.4rem; }

.tail-divider {
  width: 1px; height: 4rem;
  background: linear-gradient(180deg,
    transparent 0%,
    rgba(201,168,106,0.2) 10%,
    rgba(201,168,106,0.5) 50%,
    rgba(201,168,106,0.2) 90%,
    transparent 100%
  );
}

.logo-image { height: 3rem; width: auto; margin-top: 0.5rem; }

.qrcode-image {
  width: 4rem; height: 4rem;
  border-radius: 8px;
  border: 1px solid rgba(201,168,106,0.25);
  box-shadow:
    0 0 0 1px rgba(201,168,106,0.08) inset,
    0 4px 16px rgba(0,0,0,0.25),
    0 2px 4px rgba(0,0,0,0.15);
  background: #FFFFFF;
  padding: 0.15rem;
  transition: all 0.3s ease;
}

.qrcode-image:hover {
  box-shadow:
    0 0 0 1px rgba(201,168,106,0.15) inset,
    0 6px 20px rgba(0,0,0,0.3),
    0 3px 6px rgba(0,0,0,0.2);
  transform: translateY(-2px);
}

.qrcode-tip {
  font-size: 0.65rem;
  font-weight: 500;
  color: rgba(230,213,184,0.9);
  letter-spacing: 0.02em;
  text-align: center;
  line-height: 1.35;
  max-width: 5rem;
}
</style>
