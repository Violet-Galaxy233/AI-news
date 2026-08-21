<template>
  <div :class="['weekly-viewer', { 'capture-mode': captureMode }]">
    <div class="weekly-shell">
      <header class="weekly-header">
        <div class="header-kicker">CSAIA · WEEKLY INTELLIGENCE</div>
        <div class="header-main">
          <div>
            <h1>{{ weeklyData?.title || 'AI 一周要闻' }}</h1>
            <p>过去一周最值得关注的 AI 事件与趋势</p>
          </div>
          <div class="week-badge">
            <strong>{{ weekNumber }}</strong>
            <span>{{ weeklyData?.date_range || '' }}</span>
          </div>
        </div>
      </header>

      <nav class="weekly-nav">
        <RouterLink to="/">最新周报</RouterLink>
        <RouterLink to="/timeline">话题追踪</RouterLink>
        <RouterLink to="/papers">前沿论文</RouterLink>
        <RouterLink to="/daily">历史日报</RouterLink>
        <label v-if="weeklyIndex.length > 1" class="archive-select">
          <span>往期</span>
          <select :value="selectedWeek" @change="openWeek($event.target.value)">
            <option v-for="item in weeklyIndex" :key="item.week" :value="item.week">
              {{ item.week }} · {{ item.date_range }}
            </option>
          </select>
        </label>
      </nav>

      <main>
        <div v-if="loading" class="state-message">正在加载本周内容…</div>
        <div v-else-if="loadError" class="state-message state-error">
          <p>{{ loadError }}</p>
          <button @click="loadWeekly">重新加载</button>
        </div>

        <template v-else-if="weeklyData">
          <section class="weekly-lead">
            <div class="lead-label">THE WEEK IN ONE MINUTE</div>
            <p>{{ weeklyData.summary }}</p>
            <div class="weekly-stats">
              <span><strong>{{ weeklyData.stories?.length || 0 }}</strong> 个主题</span>
              <span><strong>{{ criticalStories.length }}</strong> 条头条</span>
              <span v-if="weeklyPapers.length"><strong>{{ weeklyPapers.length }}</strong> 篇论文</span>
              <span><strong>{{ sourceCount }}</strong> 个信息来源</span>
            </div>
          </section>

          <section v-if="criticalStories.length" class="weekly-section headline-section">
            <span class="cut-marker cut-section" aria-hidden="true"></span>
            <h2><span>WEEKLY HEADLINES</span><em>本周头条</em></h2>
            <template v-for="(story, index) in criticalStories" :key="story.id">
              <span class="cut-marker cut-story" aria-hidden="true"></span>
              <WeeklyStoryCard
                :story="story"
                :index="index + 1"
              />
            </template>
          </section>

          <section
            v-for="group in sectionGroups"
            :key="group.name"
            class="weekly-section"
          >
            <span class="cut-marker cut-section" aria-hidden="true"></span>
            <h2><span>{{ group.english }}</span><em>{{ group.name }}</em></h2>
            <template v-for="story in group.stories" :key="story.id">
              <span class="cut-marker cut-story" aria-hidden="true"></span>
              <WeeklyStoryCard :story="story" />
            </template>
          </section>

          <section v-if="weeklyPapers.length" class="weekly-section research-section">
            <span class="cut-marker cut-section" aria-hidden="true"></span>
            <h2><span>RESEARCH PICKS</span><em>本周 Top {{ weeklyPapers.length }} 论文</em></h2>
            <template v-for="(paper, index) in weeklyPapers" :key="paper.id">
              <span class="cut-marker cut-story" aria-hidden="true"></span>
              <WeeklyPaperCard :paper="paper" :index="index + 1" />
            </template>
          </section>

          <section v-if="weeklyData.trend" class="trend-section">
            <span class="cut-marker cut-section" aria-hidden="true"></span>
            <span>EDITOR'S VIEW · 一周趋势</span>
            <h2>{{ weeklyData.trend.title }}</h2>
            <p>{{ weeklyData.trend.content }}</p>
          </section>
        </template>
      </main>

      <footer class="weekly-footer">
        <img src="/logo.svg" alt="CSAIA" />
        <div>
          <strong>中新人工智能协会 CSAIA</strong>
          <span>每周筛选真正影响行业的 AI 事件</span>
        </div>
        <img src="/qrcode-website.jpeg" alt="官网二维码" class="footer-qr" />
      </footer>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import WeeklyPaperCard from './WeeklyPaperCard.vue'
import WeeklyStoryCard from './WeeklyStoryCard.vue'

const route = useRoute()
const router = useRouter()
const captureMode = computed(() => route.query.capture === 'wechat')
const weeklyData = ref(null)
const weeklyIndex = ref([])
const selectedWeek = ref('')
const loading = ref(true)
const loadError = ref('')

const sectionOrder = [
  { name: '产品与技术', english: 'PRODUCT & TECHNOLOGY' },
  { name: '公司与资本', english: 'COMPANIES & CAPITAL' },
  { name: '政策与安全', english: 'POLICY & SAFETY' },
  { name: '行业观察', english: 'INDUSTRY WATCH' },
]

const criticalStories = computed(() =>
  (weeklyData.value?.stories || []).filter(item => item.importance === 'critical')
)

const weeklyPapers = computed(() => weeklyData.value?.papers || [])

const sectionGroups = computed(() =>
  sectionOrder
    .map(section => ({
      ...section,
      stories: (weeklyData.value?.stories || []).filter(
        item => item.importance !== 'critical' && item.section === section.name
      ),
    }))
    .filter(section => section.stories.length)
)

const weekNumber = computed(() => {
  const week = weeklyData.value?.week
  if (!week) return ''
  const [year, number] = week.split('-W')
  return `${year} 年第 ${Number(number)} 周`
})

const sourceCount = computed(() => {
  const urls = new Set()
  for (const story of weeklyData.value?.stories || [])
    for (const source of story.sources || [])
      if (source.url) urls.add(source.url)
  for (const paper of weeklyPapers.value) {
    if (paper.paper_url) urls.add(paper.paper_url)
    if (paper.code_url) urls.add(paper.code_url)
  }
  return urls.size
})

const fetchWeek = async week => {
  const response = await fetch(`/weekly/${week}.json`)
  if (!response.ok) throw new Error(`无法加载 ${week}`)
  weeklyData.value = await response.json()
  selectedWeek.value = week
}

const loadWeekly = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const response = await fetch('/weekly/index.json')
    if (!response.ok) throw new Error('周报索引不可用')
    weeklyIndex.value = await response.json()
    const requestedWeek = route.params.week
    const target = requestedWeek || weeklyIndex.value[0]?.week
    if (!target) throw new Error('暂无周报数据')
    await fetchWeek(target)
  } catch (error) {
    weeklyData.value = null
    loadError.value = '周报加载失败，请检查数据后重试'
    console.error(error)
  } finally {
    loading.value = false
  }
}

const openWeek = week => {
  if (!week || week === selectedWeek.value) return
  router.push(`/weekly/${week}`)
}

watch(() => route.params.week, () => loadWeekly())
onMounted(loadWeekly)
</script>

<style scoped>
.weekly-viewer {
  min-height: 100vh;
  padding: 2rem 1rem;
  background:
    radial-gradient(circle at 50% 0%, rgba(201, 168, 106, 0.12), transparent 30rem),
    #EEEAE3;
}

.weekly-shell {
  width: min(760px, 100%);
  margin: 0 auto;
  overflow: hidden;
  background: #FFFEFC;
  border: 1px solid rgba(121, 94, 52, 0.18);
  border-radius: 14px;
  box-shadow: 0 18px 60px rgba(43, 32, 18, 0.11);
}

.weekly-header {
  padding: 1.6rem 2.2rem 1.8rem;
  color: #F5E8CE;
  background:
    linear-gradient(115deg, rgba(201, 168, 106, 0.12), transparent 55%),
    #211A14;
}

.header-kicker {
  margin-bottom: 1rem;
  color: #C9A86A;
  font-size: 0.66rem;
  font-weight: 750;
  letter-spacing: 0.2em;
}

.header-main {
  display: flex;
  justify-content: space-between;
  gap: 2rem;
  align-items: flex-end;
}

.header-main h1 {
  margin: 0;
  font-family: Georgia, 'Songti SC', serif;
  font-size: clamp(2rem, 7vw, 3.25rem);
  font-weight: 500;
  letter-spacing: 0.03em;
}

.header-main p {
  margin-top: 0.35rem;
  color: rgba(245, 232, 206, 0.68);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
}

.week-badge {
  flex: 0 0 auto;
  padding-left: 1.2rem;
  border-left: 1px solid rgba(201, 168, 106, 0.45);
}

.week-badge strong, .week-badge span { display: block; }
.week-badge strong { color: #D6B97E; font-size: 0.82rem; }
.week-badge span { margin-top: 0.25rem; color: rgba(245, 232, 206, 0.65); font-size: 0.68rem; }

.weekly-nav {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-height: 3.1rem;
  padding: 0.55rem 2.2rem;
  border-bottom: 1px solid rgba(201, 168, 106, 0.18);
  background: #FAF7F1;
}

.weekly-nav a {
  color: #786344;
  font-size: 0.7rem;
  font-weight: 650;
  white-space: nowrap;
}

.weekly-nav a.router-link-exact-active { color: #AA8342; }

.archive-select {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin-left: auto;
  color: #8D7958;
  font-size: 0.68rem;
}

.archive-select select {
  max-width: 12rem;
  border: 1px solid rgba(201, 168, 106, 0.28);
  border-radius: 6px;
  padding: 0.24rem 0.4rem;
  color: #6A583D;
  background: #FFF;
  font: inherit;
}

main { padding: 2rem 2.2rem 2.4rem; }

.weekly-lead {
  position: relative;
  padding: 1.45rem 1.55rem;
  border-radius: 10px;
  background: #F5F0E7;
}

.lead-label {
  margin-bottom: 0.55rem;
  color: #A98545;
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.15em;
}

.weekly-lead > p {
  color: #4B4032;
  font-family: Georgia, 'Songti SC', serif;
  font-size: 1.02rem;
  line-height: 1.8;
}

.weekly-stats {
  display: flex;
  gap: 1.15rem;
  margin-top: 1rem;
  padding-top: 0.8rem;
  border-top: 1px solid rgba(155, 125, 74, 0.2);
  color: #887354;
  font-size: 0.67rem;
}

.weekly-stats strong { color: #A27D40; font-size: 0.9rem; }

.weekly-section { margin-top: 2.25rem; }

.weekly-section > h2 {
  display: flex;
  align-items: baseline;
  gap: 0.7rem;
  margin: 0 0 1.2rem;
  padding-bottom: 0.6rem;
  border-bottom: 2px solid #2C241A;
}

.weekly-section > h2 span {
  color: #2C241A;
  font-size: 0.78rem;
  letter-spacing: 0.14em;
}

.weekly-section > h2 em {
  color: #A98545;
  font-size: 0.72rem;
  font-style: normal;
  font-weight: 500;
}

.headline-section > h2 { border-color: #B58B48; }
.research-section > h2 { border-color: #6F8065; }

.trend-section {
  margin-top: 2.4rem;
  padding: 1.45rem 1.55rem;
  color: #F0E4CC;
  background: #2A2118;
  border-radius: 10px;
}

.trend-section span {
  color: #C9A86A;
  font-size: 0.62rem;
  font-weight: 750;
  letter-spacing: 0.14em;
}

.trend-section h2 {
  margin: 0.5rem 0 0.65rem;
  font-family: Georgia, 'Songti SC', serif;
  font-size: 1.2rem;
}

.trend-section p {
  color: rgba(240, 228, 204, 0.76);
  font-size: 0.84rem;
  line-height: 1.8;
}

.state-message {
  padding: 5rem 1rem;
  text-align: center;
  color: #8C7654;
}

.state-error button {
  margin-top: 1rem;
  padding: 0.4rem 0.9rem;
  border: 1px solid #C9A86A;
  border-radius: 6px;
  color: #8A6832;
  background: transparent;
  cursor: pointer;
}

.weekly-footer {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.15rem 2.2rem;
  color: #E8D8BA;
  background: #211A14;
}

.weekly-footer > img { width: auto; height: 2.8rem; }
.weekly-footer > div { display: flex; flex: 1; flex-direction: column; }
.weekly-footer strong { font-size: 0.75rem; }
.weekly-footer span { color: rgba(232, 216, 186, 0.58); font-size: 0.63rem; }
.weekly-footer .footer-qr { width: 3.4rem; height: 3.4rem; padding: 0.12rem; border-radius: 5px; background: white; }

@media (max-width: 620px) {
  .weekly-viewer { padding: 0; }
  .weekly-shell { border: 0; border-radius: 0; }
  .weekly-header, main { padding-left: 1.25rem; padding-right: 1.25rem; }
  .header-main { align-items: flex-start; flex-direction: column; gap: 1.1rem; }
  .week-badge { padding-left: 0; border-left: 0; }
  .weekly-nav { gap: 0.7rem; padding: 0.65rem 1.25rem; overflow-x: auto; }
  .weekly-nav a { font-size: 0.66rem; }
  .archive-select { display: none; }
  .weekly-stats { gap: 0.7rem; }
  .weekly-footer { padding: 1rem 1.25rem; }
}

.capture-mode {
  width: 100%;
  max-width: 600px;
  min-height: 0;
  padding: 0;
  background: #FFFEFC;
}

.capture-mode .weekly-shell {
  width: 100%;
  border: 0;
  border-radius: 0;
  box-shadow: none;
}

.capture-mode .weekly-nav {
  display: none;
}

.capture-mode .weekly-header,
.capture-mode main {
  padding-left: 1.4rem;
  padding-right: 1.4rem;
}

.capture-mode .header-main {
  align-items: flex-end;
  flex-direction: row;
}

.capture-mode .week-badge {
  padding-left: 1rem;
  border-left: 1px solid rgba(201, 168, 106, 0.45);
}

.capture-mode .weekly-footer {
  border-radius: 0;
}

/* 微信长图：以手机点开后的实际阅读尺寸为准，避免桌面版字号缩小后发虚难读 */
.capture-mode .header-kicker {
  font-size: 0.72rem;
}

.capture-mode .header-main p,
.capture-mode .week-badge strong {
  font-size: 0.88rem;
}

.capture-mode .week-badge span {
  font-size: 0.75rem;
}

.capture-mode .weekly-lead > p {
  font-size: 1.16rem;
  line-height: 1.82;
}

.capture-mode .lead-label,
.capture-mode .trend-section span {
  font-size: 0.69rem;
}

.capture-mode .weekly-stats {
  font-size: 0.76rem;
}

.capture-mode .weekly-stats strong {
  font-size: 1rem;
}

.capture-mode .weekly-section > h2 span {
  font-size: 0.86rem;
}

.capture-mode .weekly-section > h2 em {
  font-size: 0.8rem;
}

.capture-mode :deep(.story-category) {
  font-size: 0.75rem;
}

.capture-mode :deep(.continued-tag) {
  font-size: 0.68rem;
}

.capture-mode :deep(.weekly-story h3) {
  font-size: 1.18rem;
  line-height: 1.48;
}

.capture-mode :deep(.importance-critical h3) {
  font-size: 1.28rem;
}

.capture-mode :deep(.story-content) {
  font-size: 1.04rem;
  line-height: 1.78;
}

.capture-mode :deep(.timeline-row) {
  grid-template-columns: 4.1rem 1fr;
  font-size: 0.88rem;
  line-height: 1.62;
}

.capture-mode :deep(.why-box span) {
  font-size: 0.68rem;
}

.capture-mode :deep(.why-box p) {
  font-size: 0.92rem;
  line-height: 1.72;
}

.capture-mode :deep(.keyword-list span),
.capture-mode :deep(.source-list a),
.capture-mode :deep(.paper-tags span),
.capture-mode :deep(.paper-links a) {
  font-size: 0.72rem;
}

.capture-mode :deep(.weekly-paper h3) {
  font-size: 1.16rem;
}

.capture-mode :deep(.paper-meta),
.capture-mode :deep(.paper-original) {
  font-size: 0.73rem;
}

.capture-mode :deep(.paper-summary) {
  font-size: 1rem;
  line-height: 1.76;
}

.capture-mode :deep(.paper-why > span) { font-size: 0.68rem; }
.capture-mode :deep(.paper-why p) { font-size: 0.9rem; line-height: 1.7; }

.capture-mode .trend-section h2 {
  font-size: 1.36rem;
}

.capture-mode .trend-section p {
  font-size: 0.98rem;
  line-height: 1.82;
}

.capture-mode .weekly-footer strong {
  font-size: 0.84rem;
}

.capture-mode .weekly-footer span {
  font-size: 0.72rem;
}

/* Safari 导出的高清母图会保留右侧分页导航点；拆图脚本读取后裁掉该窄条。 */
.cut-marker {
  display: none;
}

.capture-mode .cut-marker {
  position: relative;
  display: block;
  width: 100%;
  height: 0;
  pointer-events: none;
}

.capture-mode .cut-marker::after {
  position: absolute;
  z-index: 20;
  top: -3px;
  right: -1.4rem;
  width: 6px;
  height: 6px;
  content: '';
}

.capture-mode .cut-section::after {
  background: #23B26D;
}

.capture-mode .cut-story::after {
  background: #E0A72E;
}
</style>
