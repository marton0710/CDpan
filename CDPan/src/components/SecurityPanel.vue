<script setup>
defineProps({
  summary: {
    type: Object,
    required: true,
  },
});
</script>

<template>
  <el-card class="surface-card" shadow="hover">
    <template #header>
      <div class="card-head">
        <div>
          <strong>安全概览</strong>
          <p>结合签名、追踪和版本信息，对当前文件库进行风险归纳。</p>
        </div>
        <el-tag type="success" effect="plain">可信占比 {{ summary.trustedRate }}</el-tag>
      </div>
    </template>

    <div class="level-grid">
      <div class="level-box level-high">
        <span>高安全</span>
        <strong>{{ summary.high }}</strong>
      </div>
      <div class="level-box level-medium">
        <span>中风险</span>
        <strong>{{ summary.medium }}</strong>
      </div>
      <div class="level-box level-low">
        <span>低安全</span>
        <strong>{{ summary.low }}</strong>
      </div>
    </div>

    <div class="warning-stack">
      <div v-for="item in summary.warnings" :key="item" class="warning-item">
        {{ item }}
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.surface-card {
  border: none;
  border-radius: 26px;
  background: rgba(255, 251, 245, 0.86);
  box-shadow: 0 20px 44px rgba(34, 26, 14, 0.08);
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.card-head strong {
  display: block;
  margin-bottom: 6px;
  font-size: 1.04rem;
}

.card-head p {
  margin: 0;
  color: #6b6157;
  line-height: 1.6;
}

.level-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.level-box {
  padding: 16px;
  border-radius: 18px;
  display: grid;
  gap: 8px;
}

.level-box span {
  font-size: 0.88rem;
}

.level-box strong {
  font-size: 1.7rem;
}

.level-high {
  background: rgba(22, 163, 74, 0.09);
  color: #166534;
}

.level-medium {
  background: rgba(217, 119, 6, 0.12);
  color: #9a6700;
}

.level-low {
  background: rgba(220, 38, 38, 0.1);
  color: #a61b1b;
}

.warning-stack {
  margin-top: 18px;
  display: grid;
  gap: 10px;
}

.warning-item {
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(255, 247, 237, 0.9);
  color: #6f675d;
  line-height: 1.62;
}

@media (max-width: 640px) {
  .level-grid {
    grid-template-columns: 1fr;
  }
}
</style>
