<script setup>
defineProps({
  stats: {
    type: Array,
    required: true,
  },
});
</script>

<template>
  <section class="stats-grid">
    <el-card v-for="item in stats" :key="item.label" class="stat-card" shadow="hover">
      <p class="stat-label">{{ item.label }}</p>
      <strong class="stat-value">{{ item.value }}</strong>
      <p class="stat-note">{{ item.note }}</p>
    </el-card>
  </section>
</template>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
  margin-bottom: 24px;
}

.stat-card {
  border: none;
  border-radius: 24px;
  background: rgba(255, 251, 245, 0.84);
  box-shadow: 0 20px 40px rgba(34, 26, 14, 0.08);
}

.stat-label {
  margin: 0 0 10px;
  color: #6b6157;
  font-size: 0.9rem;
}

.stat-value {
  display: block;
  margin-bottom: 10px;
  font-size: clamp(1.9rem, 3vw, 2.5rem);
  line-height: 1;
}

.stat-note {
  margin: 0;
  color: #7a7268;
  line-height: 1.6;
  font-size: 0.92rem;
}

@media (max-width: 1080px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
