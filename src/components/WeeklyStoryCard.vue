<template>
  <article :class="['weekly-story', `importance-${story.importance}`]">
    <div class="story-heading">
      <span v-if="index" class="story-number">{{ String(index).padStart(2, '0') }}</span>
      <div>
        <div class="story-meta">
          <span class="story-category">{{ story.section }}</span>
          <span v-if="story.previous_week" class="continued-tag">承接上周</span>
        </div>
        <h3>{{ story.title }}</h3>
      </div>
    </div>

    <p class="story-content">{{ story.content }}</p>

    <div v-if="story.timeline?.length" class="story-timeline">
      <div v-for="event in story.timeline" :key="`${event.date}-${event.event}`" class="timeline-row">
        <span>{{ event.date }}</span>
        <p>{{ event.event }}</p>
      </div>
    </div>

    <div v-if="story.why_it_matters" class="why-box">
      <span>WHY IT MATTERS</span>
      <p>{{ story.why_it_matters }}</p>
    </div>

    <div class="story-footer">
      <div class="keyword-list">
        <span v-for="keyword in story.keywords || []" :key="keyword">{{ keyword }}</span>
      </div>
      <div class="source-list">
        <a
          v-for="source in story.sources || []"
          :key="source.url"
          :href="source.url"
          target="_blank"
          rel="noopener noreferrer"
        >{{ source.name }}</a>
      </div>
    </div>
  </article>
</template>

<script setup>
defineProps({
  story: { type: Object, required: true },
  index: { type: Number, default: 0 },
})
</script>

<style scoped>
.weekly-story {
  padding: 1.35rem 0;
  border-bottom: 1px solid rgba(201, 168, 106, 0.2);
}

.weekly-story:first-child { padding-top: 0; }
.weekly-story:last-child { border-bottom: 0; padding-bottom: 0; }

.story-heading {
  display: flex;
  gap: 0.9rem;
  align-items: flex-start;
  margin-bottom: 0.7rem;
}

.story-heading > div {
  min-width: 0;
}

.story-number {
  flex: 0 0 2rem;
  height: 2rem;
  border: 1px solid rgba(201, 168, 106, 0.35);
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #B8924D;
  font-size: 0.78rem;
  font-weight: 700;
}

.story-meta {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  margin-bottom: 0.22rem;
}

.story-category {
  color: #A98545;
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.12em;
}

.continued-tag {
  padding: 0.08rem 0.38rem;
  border-radius: 10px;
  background: rgba(201, 168, 106, 0.1);
  color: #8C7652;
  font-size: 0.6rem;
}

h3 {
  margin: 0;
  color: #211A12;
  font-size: 1.04rem;
  line-height: 1.45;
  overflow-wrap: anywhere;
}

.importance-critical h3 { font-size: 1.12rem; }

.story-content {
  color: #594E3F;
  font-size: 0.9rem;
  line-height: 1.75;
  overflow-wrap: anywhere;
}

.story-timeline {
  margin-top: 0.85rem;
  padding-left: 0.75rem;
  border-left: 2px solid rgba(201, 168, 106, 0.25);
}

.timeline-row {
  display: grid;
  grid-template-columns: 3.6rem 1fr;
  gap: 0.55rem;
  margin-bottom: 0.38rem;
  font-size: 0.76rem;
  line-height: 1.55;
}

.timeline-row:last-child { margin-bottom: 0; }
.timeline-row span { color: #A98545; font-weight: 650; }
.timeline-row p { color: #72634E; }

.why-box {
  margin-top: 0.9rem;
  padding: 0.78rem 0.9rem;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(201, 168, 106, 0.09), rgba(201, 168, 106, 0.03));
  border: 1px solid rgba(201, 168, 106, 0.16);
}

.why-box span {
  display: block;
  margin-bottom: 0.28rem;
  color: #A98545;
  font-size: 0.6rem;
  font-weight: 750;
  letter-spacing: 0.13em;
}

.why-box p {
  color: #655844;
  font-size: 0.8rem;
  line-height: 1.65;
}

.story-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 0.75rem;
  margin-top: 0.85rem;
}

.keyword-list, .source-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.keyword-list span {
  color: #8A7759;
  background: #F7F3EC;
  border-radius: 10px;
  padding: 0.13rem 0.45rem;
  font-size: 0.61rem;
}

.source-list {
  justify-content: flex-end;
}

.source-list a {
  color: #A98545;
  font-size: 0.64rem;
  text-decoration: underline;
  text-decoration-color: rgba(169, 133, 69, 0.25);
  text-underline-offset: 2px;
}

@media (max-width: 520px) {
  .story-footer { align-items: flex-start; flex-direction: column; }
  .source-list { justify-content: flex-start; }
}
</style>
