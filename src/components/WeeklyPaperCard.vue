<template>
  <article class="weekly-paper">
    <div class="paper-rank">{{ String(index).padStart(2, '0') }}</div>
    <div class="paper-body">
      <div class="paper-meta">
        <span>{{ paper.category }}</span>
        <span v-if="paper.published_date">{{ paper.published_date }}</span>
      </div>
      <h3>{{ paper.title }}</h3>
      <p class="paper-original">{{ paper.original_title }}</p>
      <p class="paper-summary">{{ paper.summary }}</p>

      <div v-if="paper.why_it_matters" class="paper-why">
        <span>WHY IT MATTERS</span>
        <p>{{ paper.why_it_matters }}</p>
      </div>

      <div class="paper-footer">
        <div class="paper-tags">
          <span v-for="keyword in paper.keywords || []" :key="keyword">{{ keyword }}</span>
        </div>
        <div class="paper-links">
          <a v-if="paper.paper_url" :href="paper.paper_url" target="_blank" rel="noopener noreferrer">论文</a>
          <a v-if="paper.code_url" :href="paper.code_url" target="_blank" rel="noopener noreferrer">代码 / 数据</a>
        </div>
      </div>
    </div>
  </article>
</template>

<script setup>
defineProps({
  paper: { type: Object, required: true },
  index: { type: Number, required: true },
})
</script>

<style scoped>
.weekly-paper {
  display: grid;
  grid-template-columns: 2rem 1fr;
  gap: 0.9rem;
  padding: 1.35rem 0;
  border-bottom: 1px solid rgba(201, 168, 106, 0.2);
}

.weekly-paper:last-child { border-bottom: 0; padding-bottom: 0; }

.paper-rank {
  width: 2rem;
  height: 2rem;
  display: grid;
  place-items: center;
  border-radius: 50%;
  color: #B8924D;
  border: 1px solid rgba(201, 168, 106, 0.35);
  font-size: 0.78rem;
  font-weight: 700;
}

.paper-body { min-width: 0; }

.paper-meta {
  display: flex;
  gap: 0.55rem;
  margin-bottom: 0.25rem;
  color: #A98545;
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.08em;
}

h3 {
  margin: 0;
  color: #211A12;
  font-size: 1.05rem;
  line-height: 1.45;
}

.paper-original {
  margin-top: 0.25rem;
  color: #9A876A;
  font-family: Georgia, serif;
  font-size: 0.7rem;
  line-height: 1.5;
}

.paper-summary {
  margin-top: 0.65rem;
  color: #594E3F;
  font-size: 0.88rem;
  line-height: 1.75;
}

.paper-why {
  margin-top: 0.85rem;
  padding: 0.75rem 0.85rem;
  border: 1px solid rgba(201, 168, 106, 0.16);
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(201, 168, 106, 0.09), rgba(201, 168, 106, 0.03));
}

.paper-why > span {
  display: block;
  margin-bottom: 0.25rem;
  color: #A98545;
  font-size: 0.6rem;
  font-weight: 750;
  letter-spacing: 0.13em;
}

.paper-why p {
  color: #655844;
  font-size: 0.79rem;
  line-height: 1.65;
}

.paper-footer {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  margin-top: 0.8rem;
}

.paper-tags, .paper-links { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.paper-tags span {
  padding: 0.13rem 0.45rem;
  border-radius: 10px;
  color: #8A7759;
  background: #F7F3EC;
  font-size: 0.61rem;
}
.paper-links a {
  color: #A98545;
  font-size: 0.64rem;
  text-decoration: underline;
  text-decoration-color: rgba(169, 133, 69, 0.25);
  text-underline-offset: 2px;
}

@media (max-width: 520px) {
  .paper-footer { flex-direction: column; }
}
</style>
