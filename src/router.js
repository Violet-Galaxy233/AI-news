import { createRouter, createWebHistory } from 'vue-router'
import NewsViewer from './components/NewsViewer.vue'
import PaperViewer from './components/PaperViewer.vue'
import TimelineViewer from './components/TimelineViewer.vue'

const routes = [
  { path: '/', component: NewsViewer },
  { path: '/papers', component: PaperViewer },
  { path: '/timeline', component: TimelineViewer },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
