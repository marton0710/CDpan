<script setup>
import { nextTick, ref, watch } from "vue";

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
  loadingFiles: {
    type: Boolean,
    default: false,
  },
  uploading: {
    type: Boolean,
    default: false,
  },
  selectedFileName: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["pick-file", "upload", "refresh"]);
const uploadRef = ref(null);

function handleFileChange(uploadFile) {
  emit("pick-file", uploadFile.raw || null);
}

watch(
  () => props.selectedFileName,
  async (value) => {
    if (!value) {
      await nextTick();
      uploadRef.value?.clearFiles();
    }
  }
);
</script>

<template>
  <el-card class="surface-card" shadow="hover">
    <template #header>
      <div class="card-head">
        <div>
          <strong>上传中心</strong>
          <p>仅支持 PDF，上传后自动触发哈希、签名和追踪识别。</p>
        </div>
        <el-tag :type="disabled ? 'warning' : 'success'" effect="plain">
          {{ disabled ? "请先登录" : "已就绪" }}
        </el-tag>
      </div>
    </template>

    <div class="upload-stack">
      <el-upload
        ref="uploadRef"
        drag
        :auto-upload="false"
        :limit="1"
        accept=".pdf,application/pdf"
        :disabled="disabled || uploading"
        :on-change="handleFileChange"
        :show-file-list="false"
      >
        <div class="upload-copy">
          <div class="upload-title">拖拽 PDF 到这里，或点击选择文件</div>
          <div class="upload-tip">系统会识别是否为同一文档的重复上传或新版本。</div>
        </div>
      </el-upload>

      <div class="selected-box">
        <span>当前文件</span>
        <strong>{{ selectedFileName || "尚未选择文件" }}</strong>
      </div>

      <div class="button-row">
        <el-button type="primary" :disabled="disabled" :loading="uploading" @click="emit('upload')">
          立即上传
        </el-button>
        <el-button :loading="loadingFiles" @click="emit('refresh')">刷新列表</el-button>
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

.upload-stack {
  display: grid;
  gap: 18px;
}

.upload-copy {
  display: grid;
  gap: 8px;
}

.upload-title {
  font-size: 1rem;
  font-weight: 700;
}

.upload-tip {
  color: #766c60;
  font-size: 0.92rem;
}

.selected-box {
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(15, 118, 110, 0.06);
  display: grid;
  gap: 6px;
}

.selected-box span {
  color: #6b6157;
  font-size: 0.86rem;
}

.selected-box strong {
  word-break: break-all;
}

.button-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
