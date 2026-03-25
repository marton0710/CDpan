<script setup>
import { Search } from "@element-plus/icons-vue";
import { computed, ref, watch } from "vue";

const props = defineProps({
  files: {
    type: Array,
    required: true,
  },
  hasToken: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  fileCountText: {
    type: String,
    required: true,
  },
  securityText: {
    type: Function,
    required: true,
  },
});

defineEmits(["download", "verify", "trace", "delete"]);

const PAGE_SIZE = 5;
const currentPage = ref(1);
const searchKeyword = ref("");

const filteredFiles = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase();
  if (!keyword) {
    return props.files;
  }

  return props.files.filter((file) => {
    const searchFields = [
      file.filename,
      file.original_filename,
      file.owner_username,
      file.owner_uuid,
      file.tracking_id,
    ];

    return searchFields.some((field) => String(field || "").toLowerCase().includes(keyword));
  });
});

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(filteredFiles.value.length / PAGE_SIZE));
});

const pagedFiles = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE;
  return filteredFiles.value.slice(start, start + PAGE_SIZE);
});

watch(
  () => filteredFiles.value.length,
  (length) => {
    if (length === 0) {
      currentPage.value = 1;
      return;
    }

    if (currentPage.value > totalPages.value) {
      currentPage.value = totalPages.value;
    }
  },
  { immediate: true }
);

watch(searchKeyword, () => {
  currentPage.value = 1;
});

function securityType(level) {
  if (level === "high") {
    return "success";
  }
  if (level === "medium") {
    return "warning";
  }
  return "danger";
}

function ownerTagType(file) {
  return file.is_owner_for_viewer ? "success" : "warning";
}

function ownerTagText(file) {
  return file.is_owner_for_viewer ? "我的文件" : "他人文件";
}

function ownerDisplayName(file) {
  return file.owner_username || file.owner_uuid || "未知用户";
}

function shortText(value, start = 18, end = 10) {
  if (!value) {
    return "-";
  }
  if (value.length <= start + end + 3) {
    return value;
  }
  return `${value.slice(0, start)}...${value.slice(-end)}`;
}
</script>

<template>
  <el-card class="surface-card" shadow="hover">
    <template #header>
      <div class="card-head">
        <div>
          <strong>文件工作台</strong>
          <p>这里会展示当前可访问的 PDF 文件，并区分哪些是你的文件、哪些来自其他账号。</p>
        </div>
        <el-tag type="info" effect="plain">{{ fileCountText }}</el-tag>
      </div>

      <div v-if="hasToken" class="toolbar-row">
        <el-input
          v-model="searchKeyword"
          class="search-input"
          clearable
          placeholder="搜索文件名、原始文件名、归属账号或 Tracking ID"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <p class="search-copy">
          当前显示 {{ filteredFiles.length }} 条结果
          <span v-if="searchKeyword">，关键词：{{ searchKeyword }}</span>
        </p>
      </div>
    </template>

    <div v-if="!hasToken" class="empty-box">
      <el-empty description="登录后即可查看文件列表和追踪记录" />
    </div>
    <div v-else-if="loading" class="empty-box">
      <el-skeleton :rows="8" animated />
    </div>
    <div v-else-if="files.length === 0" class="empty-box">
      <el-empty description="当前还没有可访问的 PDF 文件，先上传一份开始使用" />
    </div>
    <div v-else-if="filteredFiles.length === 0" class="empty-box">
      <el-empty description="没有匹配的文件，换个关键词试试" />
    </div>
    <div v-else class="file-stack">
      <article v-for="file in pagedFiles" :key="file.id" class="file-item">
        <div class="file-item-head">
          <div class="file-title-block">
            <div class="file-title-row">
              <h3>{{ file.filename }}</h3>
              <div class="head-tags">
                <el-tag :type="ownerTagType(file)" effect="plain">
                  {{ ownerTagText(file) }}
                </el-tag>
                <el-tag effect="plain">V{{ file.version_no ?? 1 }}</el-tag>
                <el-tag :type="securityType(file.security_level)" effect="dark">
                  {{ securityText(file.security_level) }}
                </el-tag>
              </div>
            </div>
            <p class="file-subtitle">
              原始文件名：{{ file.original_filename || file.filename }}
            </p>
            <p class="file-owner-line">
              归属账号：
              <span class="owner-name">{{ ownerDisplayName(file) }}</span>
              <span v-if="file.is_owner_for_viewer" class="owner-tip">你可以管理这份文件</span>
              <span v-else class="owner-tip owner-tip-muted">你可以查看，但不能删除这份文件</span>
            </p>
          </div>

          <div class="action-row">
            <el-button type="primary" @click="$emit('download', file)">下载</el-button>
            <el-button plain @click="$emit('verify', file)">验签</el-button>
            <el-button plain @click="$emit('trace', file)">追踪</el-button>
            <el-button
              v-if="file.is_owner_for_viewer"
              type="danger"
              plain
              @click="$emit('delete', file)"
            >
              删除
            </el-button>
            <el-tooltip v-else content="只有文件所有者可以删除" placement="top">
              <el-button plain disabled>仅所有者可删除</el-button>
            </el-tooltip>
          </div>
        </div>

        <div class="file-info-grid">
          <section class="info-card">
            <span class="info-label">Tracking ID</span>
            <strong class="info-value mono" :title="file.tracking_id || '-'">
              {{ shortText(file.tracking_id || "-", 18, 12) }}
            </strong>
          </section>

          <section class="info-card">
            <span class="info-label">文件 Hash</span>
            <strong class="info-value mono" :title="file.hash || '-'">
              {{ shortText(file.hash || "-", 18, 12) }}
            </strong>
          </section>

          <section class="info-card info-card-wide">
            <span class="info-label">安全说明</span>
            <p class="info-text">{{ file.security_reason || "暂时没有安全说明" }}</p>
          </section>
        </div>

        <div class="stats-row">
          <div class="stat-pill">
            <span>上传</span>
            <strong>{{ file.upload_count }}</strong>
          </div>
          <div class="stat-pill">
            <span>重复上传</span>
            <strong>{{ file.repeat_upload_count ?? 0 }}</strong>
          </div>
          <div class="stat-pill">
            <span>下载</span>
            <strong>{{ file.download_count }}</strong>
          </div>
          <div class="stat-pill">
            <span>验签</span>
            <strong>{{ file.verify_count }}</strong>
          </div>
        </div>
      </article>

      <div v-if="filteredFiles.length > PAGE_SIZE" class="pagination-wrap">
        <p class="pagination-copy">
          当前第 {{ currentPage }} / {{ totalPages }} 页，每页 {{ PAGE_SIZE }} 条
        </p>
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="PAGE_SIZE"
          :total="filteredFiles.length"
          layout="total, prev, pager, next"
          background
        />
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.surface-card {
  border: none;
  border-radius: 26px;
  background: rgba(255, 251, 245, 0.9);
  box-shadow: 0 22px 46px rgba(34, 26, 14, 0.08);
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.card-head strong {
  display: block;
  margin-bottom: 6px;
  font-size: 1.06rem;
}

.card-head p {
  margin: 0;
  color: #6b6157;
  line-height: 1.6;
}

.toolbar-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 18px;
}

.search-input {
  max-width: 420px;
}

.search-copy {
  margin: 0;
  color: #6b6157;
  font-size: 0.92rem;
}

.empty-box {
  padding: 8px 0;
}

.file-stack {
  display: grid;
  gap: 18px;
}

.file-item {
  padding: 22px;
  border: 1px solid rgba(198, 180, 156, 0.38);
  border-radius: 24px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(249, 244, 236, 0.78));
}

.file-item-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.file-title-block {
  min-width: 0;
}

.file-title-row {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.file-title-row h3 {
  margin: 0;
  font-size: 1.4rem;
  line-height: 1.2;
}

.head-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.file-subtitle,
.file-owner-line {
  margin: 10px 0 0;
  color: #6b6157;
  line-height: 1.55;
}

.owner-name {
  color: #2f2a24;
  font-weight: 600;
}

.owner-tip {
  margin-left: 12px;
  padding: 3px 10px;
  border-radius: 999px;
  background: rgba(15, 118, 110, 0.1);
  color: #0f766e;
  font-size: 0.82rem;
}

.owner-tip-muted {
  background: rgba(180, 83, 9, 0.1);
  color: #b45309;
}

.action-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.file-info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 18px;
}

.info-card {
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(245, 239, 229, 0.72);
  border: 1px solid rgba(202, 186, 163, 0.24);
}

.info-card-wide {
  grid-column: 1 / -1;
}

.info-label {
  display: block;
  margin-bottom: 8px;
  color: #7a7268;
  font-size: 0.82rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.info-value {
  display: block;
  font-size: 1rem;
  color: #2f2a24;
}

.info-text {
  margin: 0;
  color: #5f564c;
  line-height: 1.65;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-top: 18px;
}

.stat-pill {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(15, 118, 110, 0.06);
  display: grid;
  gap: 6px;
}

.stat-pill span {
  color: #73695f;
  font-size: 0.84rem;
}

.stat-pill strong {
  font-size: 1.3rem;
  line-height: 1;
}

.mono {
  font-family: "Cascadia Code", "Consolas", monospace;
}

.pagination-wrap {
  display: grid;
  gap: 12px;
  justify-items: end;
  padding-top: 6px;
}

.pagination-copy {
  margin: 0;
  color: #6b6157;
  font-size: 0.92rem;
}

@media (max-width: 1080px) {
  .toolbar-row {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input {
    max-width: none;
  }

  .file-item-head {
    flex-direction: column;
  }

  .action-row {
    justify-content: flex-start;
  }

  .stats-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .file-item {
    padding: 18px;
  }

  .file-info-grid,
  .stats-row {
    grid-template-columns: 1fr;
  }

  .file-title-row h3 {
    font-size: 1.16rem;
  }

  .action-row {
    width: 100%;
  }

  .pagination-wrap {
    justify-items: start;
  }
}
</style>
