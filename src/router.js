import { createRouter, createWebHistory } from 'vue-router'
import NewsViewer from './components/NewsViewer.vue'
import PaperViewer from './components/PaperViewer.vue'
import TimelineViewer from './components/TimelineViewer.vue'
import WeeklyViewer from './components/WeeklyViewer.vue'

const routes = [
  { path: '/', component: WeeklyViewer },
  { path: '/weekly/:week?', component: WeeklyViewer },
  { path: '/daily', component: NewsViewer },
  { path: '/papers', component: PaperViewer },
  { path: '/timeline', component: TimelineViewer },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
