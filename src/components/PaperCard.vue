<template>
  <!-- Critical：完整展示 -->
  <article v-if="paper.importance === 'critical'" class="paper-item featured">
    <div class="featured-number">{{ formattedIndex }}</div>
    <div class="featured-content">
      <h3 class="featured-title">{{ paper.title }}</h3>
      <div class="featured-original">{{ paper.original_title }}</div>
      <div class="featured-meta">
        <span class="meta-org">{{ paper.authors_org }}</span>
        <a :href="paper.arxiv_url" target="_blank" rel="noopener" class="meta-link">arXiv ↗</a>
      </div>
      <p class="featured-summary">{{ paper.summary }}</p>
      <div v-if="paper.impact" class="featured-impact">
        <span class="impact-label">影响</span>
        <span class="impact-text">{{ paper.impact }}</span>
      </div>
    </div>
  </article>

  <!-- High：中等展示 -->
  <article v-else-if="paper.importance === 'high'" class="paper-item notable">
    <span class="notable-bullet">◆</span>
    <div class="notable-content">
      <div class="notable-header">
        <span class="notable-title">{{ paper.title }}</span>
        <a :href="paper.arxiv_url" target="_blank" rel="noopener" class="notable-link">arXiv ↗</a>
      </div>
      <div class="notable-original">{{ paper.original_title }}</div>
      <p class="notable-summary">{{ paper.summary }}</p>
    </div>
  </article>

  <!-- Medium：简洁展示 -->
  <article v-else class="paper-item compact">
    <span class="compact-bullet">✦</span>
    <div class="compact-content">
      <span class="compact-title">{{ paper.title }}：</span>
      <span class="compact-summary">{{ paper.summary }}</span>
      <a :href="paper.arxiv_url" target="_blank" rel="noopener" class="compact-link">arXiv ↗</a>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  paper: { type: Object, required: true },
  index: { type: Number, default: 0 },
})

const formattedIndex = computed(() => String(props.index).padStart(2, '0'))
</script>

<style scoped>
/* ── Featured (critical) ── */
.paper-item.featured {
  display: flex;
  gap: 1.125rem;
  margin-bottom: 1.75rem;
}
.paper-item.featured:last-child { margin-bottom: 0; }

.featured-number {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: #B8924D;
  background: linear-gradient(135deg, rgba(201,168,106,0.08) 0%, rgba(184,146,77,0.08) 100%);
  border-radius: 50%;
  border: 1.5px solid rgba(201,168,106,0.2);
  margin-top: -0.1rem;
}

.featured-content { flex: 1; }

.featured-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1A1410;
  line-height: 1.45;
  margin: 0 0 0.2rem;
  letter-spacing: -0.01em;
}

.featured-original {
  font-size: 0.75rem;
  color: #9A876A;
  margin-bottom: 0.5rem;
  font-style: italic;
  line-height: 1.4;
}

.featured-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.6rem;
}

.meta-org {
  font-size: 0.75rem;
  font-weight: 500;
  color: #B8924D;
  background: rgba(201,168,106,0.08);
  border: 1px solid rgba(201,168,106,0.2);
  border-radius: 4px;
  padding: 0.1rem 0.5rem;
}

.meta-link {
  font-size: 0.75rem;
  font-weight: 500;
  color: #B8924D;
  text-decoration: none;
  letter-spacing: 0.03em;
}
.meta-link:hover { color: #C9A86A; }

.featured-summary {
  font-size: 0.9rem;
  color: #5C5142;
  line-height: 1.7;
  margin: 0 0 0.6rem;
  letter-spacing: 0.005em;
}

.featured-impact {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
  background: rgba(201,168,106,0.05);
  border-left: 2px solid rgba(201,168,106,0.35);
  padding: 0.45rem 0.7rem;
  border-radius: 0 4px 4px 0;
}

.impact-label {
  flex-shrink: 0;
  font-size: 0.7rem;
  font-weight: 600;
  color: #B8924D;
  letter-spacing: 0.08em;
  padding-top: 0.05rem;
}

.impact-text {
  font-size: 0.8rem;
  color: #5C5142;
  line-height: 1.6;
}

/* ── Notable (high) ── */
.paper-item.notable {
  display: flex;
  gap: 0.8rem;
  margin-bottom: 1.35rem;
  align-items: flex-start;
}
.paper-item.notable:last-child { margin-bottom: 0; }

.notable-bullet {
  flex-shrink: 0;
  font-size: 0.7rem;
  color: #C9A86A;
  margin-top: 0.3rem;
}

.notable-content { flex: 1; }

.notable-header {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.15rem;
}

.notable-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #3D3529;
}

.notable-link {
  font-size: 0.72rem;
  color: #B8924D;
  text-decoration: none;
  white-space: nowrap;
}
.notable-link:hover { color: #C9A86A; }

.notable-original {
  font-size: 0.72rem;
  color: #9A876A;
  font-style: italic;
  margin-bottom: 0.35rem;
}

.notable-summary {
  font-size: 0.875rem;
  color: #5C5142;
  line-height: 1.65;
  margin: 0;
}

/* ── Compact (medium) ── */
.paper-item.compact {
  display: flex;
  gap: 0.8rem;
  margin-bottom: 1rem;
  align-items: flex-start;
}
.paper-item.compact:last-child { margin-bottom: 0; }

.compact-bullet {
  flex-shrink: 0;
  font-size: 1.1rem;
  color: #C9A86A;
  line-height: 1;
  margin-top: 0.18rem;
}

.compact-content {
  flex: 1;
  font-size: 0.875rem;
  color: #5C5142;
  line-height: 1.65;
}

.compact-title {
  font-weight: 600;
  color: #3D3529;
}

.compact-link {
  margin-left: 0.4rem;
  font-size: 0.72rem;
  color: #B8924D;
  text-decoration: none;
  white-space: nowrap;
}
.compact-link:hover { color: #C9A86A; }
</style>
