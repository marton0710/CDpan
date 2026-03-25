<script setup>
defineProps({
  logs: {
    type: Array,
    required: true,
  },
});
</script>

<template>
  <el-card class="surface-card" shadow="hover">
    <template #header>
      <div class="card-head">
        <span>运行日志</span>
        <el-tag type="info" effect="plain">{{ logs.length }} 条</el-tag>
      </div>
    </template>

    <el-scrollbar max-height="260px">
      <pre class="log-output">{{ logs.join("\n\n") }}</pre>
    </el-scrollbar>
  </el-card>
</template>

<style scoped>
.surface-card {
  border: none;
  border-radius: 24px;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.log-output {
  min-height: 180px;
  margin: 0;
  padding: 14px;
  border-radius: 18px;
  background: #171411;
  color: #f4efe7;
  white-space: pre-wrap;
}
</style>
