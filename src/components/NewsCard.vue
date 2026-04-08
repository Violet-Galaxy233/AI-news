<template>
  <!-- 头条样式 -->
  <article v-if="type === 'headline'" class="news-item headline">
    <div class="headline-number">{{ formattedIndex }}</div>
    <div class="headline-content">
      <h3 v-if="news.title" class="headline-title">{{ news.title }}</h3>
      <p class="headline-text">{{ news.content }}</p>
    </div>
  </article>

  <!-- 快讯样式 -->
  <article v-else class="news-item brief">
    <span class="brief-bullet">✦</span>
    <p class="brief-text">
      <span v-if="news.title" class="brief-title">{{ news.title }}：</span>{{ news.content }}
    </p>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  news: {
    type: Object,
    required: true
  },
  type: {
    type: String,
    required: true,
    validator: (value) => ['headline', 'brief'].includes(value)
  },
  index: {
    type: Number,
    default: 0
  }
})

// 格式化序号（01、02、03）
const formattedIndex = computed(() => {
  return String(props.index).padStart(2, '0')
})
</script>

<style scoped>
/* 头条样式 */
.news-item.headline {
  display: flex;
  gap: 1.125rem;
  margin-bottom: 1.5rem;
}

.news-item.headline:last-child {
  margin-bottom: 0;
}

.headline-number {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: #B8924D;
  background: linear-gradient(135deg, rgba(201, 168, 106, 0.08) 0%, rgba(184, 146, 77, 0.08) 100%);
  border-radius: 50%;
  border: 1.5px solid rgba(201, 168, 106, 0.2);
  margin-top: -0.27rem;
}

.headline-content {
  flex: 1;
}

.headline-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1A1410;
  line-height: 1.45;
  margin: 0 0 0.375rem 0;
  letter-spacing: -0.01em;
}

.headline-text {
  font-size: 0.9rem;
  font-weight: 400;
  color: #5C5142;
  line-height: 1.7;
  margin: 0;
  letter-spacing: 0.005em;
}

/* 快讯样式 */
.news-item.brief {
  display: flex;
  gap: 0.8rem;
  margin-bottom: 1.35rem;
  align-items: flex-start;
}

.news-item.brief:last-child {
  margin-bottom: 0;
}

.brief-bullet {
  flex-shrink: 0;
  width: 1rem;
  height: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: #C9A86A;
  line-height: 1;
  margin-top: 0.115rem;
}

.brief-text {
  flex: 1;
  font-size: 0.9rem;
  font-weight: 400;
  color: #5C5142;
  line-height: 1.65;
  margin: 0;
  letter-spacing: 0.005em;
}

.brief-title {
  font-weight: 600;
  color: #3D3529;
}
</style>
