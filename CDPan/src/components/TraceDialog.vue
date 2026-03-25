<script setup>
defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  traceData: {
    type: Object,
    default: null,
  },
  securityText: {
    type: Function,
    required: true,
  },
});

defineEmits(["update:modelValue"]);

function levelType(level) {
  if (level === "high") {
    return "success";
  }
  if (level === "medium") {
    return "warning";
  }
  return "danger";
}

function ownerTagType(traceData) {
  return traceData?.is_owner_for_viewer ? "success" : "warning";
}

function ownerTagText(traceData) {
  return traceData?.is_owner_for_viewer ? "我的文件" : "他人文件";
}

function ownerDisplayName(traceData) {
  return traceData?.owner_username || traceData?.owner_uuid || "未知用户";
}

function eventLabel(eventType) {
  const mapping = {
    upload: "上传",
    download: "下载",
    verify: "验签",
    delete: "删除",
    reupload_same_version: "重复上传同一版本",
    restore_same_version: "恢复已删除版本",
    upload_new_version: "上传新版本",
  };
  return mapping[eventType] || eventType;
}

function actorLabel(trace) {
  return trace.actor_username || trace.actor_uuid || "系统 / 未记录";
}

function shortText(value, start = 18, end = 12) {
  if (!value) {
    return "-";
  }
  if (value.length <= start + end + 3) {
    return value;
  }
  return `${value.slice(0, start)}...${value.slice(-end)}`;
}

function parseDetail(detail) {
  if (!detail || typeof detail !== "string") {
    return [];
  }

  return detail
    .split(";")
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => {
      const [rawKey, ...rest] = item.split("=");
      const rawValue = rest.join("=").trim();
      const key = rawKey.trim();
      return {
        key,
        label: detailLabel(key),
        value: detailValue(key, rawValue),
      };
    });
}

function detailLabel(key) {
  const mapping = {
    original_filename: "原始文件名",
    tracking_id: "文档追踪编号",
    version_no: "版本号",
    metadata_written: "追踪标记写入结果",
    filename: "文件名",
    is_valid: "验签结果",
  };
  return mapping[key] || key;
}

function detailValue(key, value) {
  if (key === "metadata_written") {
    return value === "True" ? "已写入文件追踪标记" : "未写入文件追踪标记";
  }
  if (key === "is_valid") {
    return value === "True" ? "签名有效，文件未发现异常" : "签名无效，建议人工复核";
  }
  if (key === "version_no") {
    return `第 ${value} 个版本`;
  }
  return value || "-";
}

function detailSummary(trace) {
  const items = parseDetail(trace.detail);
  const isValid = items.find((item) => item.key === "is_valid")?.value;

  const mapping = {
    upload: "文件已上传，系统已完成追踪和签名处理。",
    download: "文件已被下载一次，系统已记录本次访问。",
    delete: "文件已被删除，系统保留了这次操作的审计记录。",
    reupload_same_version: "检测到同一版本再次上传，系统已归并到原有版本链路。",
    restore_same_version: "检测到你恢复了一份曾删除的版本，系统已重新启用该记录。",
    upload_new_version: "检测到同一文档的新版本，系统已新增版本记录。",
  };

  if (trace.event_type === "verify") {
    return isValid || "系统已完成一次验签。";
  }

  return mapping[trace.event_type] || "系统已记录本次文件操作。";
}
</script>

<template>
  <el-dialog
    :model-value="modelValue"
    width="920px"
    destroy-on-close
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <template #header>
      <div class="trace-head">
        <div>
          <strong>文件追踪详情</strong>
          <p>这里会展示这份文件的归属账号、版本信息，以及每一次关键操作是谁完成的。</p>
        </div>
        <el-tag
          v-if="traceData?.security"
          :type="levelType(traceData.security.security_level)"
          effect="dark"
        >
          {{ securityText(traceData.security.security_level) }}
        </el-tag>
      </div>
    </template>

    <el-skeleton v-if="loading" :rows="10" animated />

    <div v-else-if="traceData" class="trace-stack">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="文件名称">{{ traceData.filename }}</el-descriptions-item>
        <el-descriptions-item label="文件归属">
          <el-tag :type="ownerTagType(traceData)" effect="plain">
            {{ ownerTagText(traceData) }}
          </el-tag>
          <span class="owner-name">{{ ownerDisplayName(traceData) }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="原始文件名">
          {{ traceData.original_filename || traceData.filename }}
        </el-descriptions-item>
        <el-descriptions-item label="Tracking ID">
          <span class="mono" :title="traceData.tracking_id || '-'">
            {{ shortText(traceData.tracking_id || "-", 20, 16) }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="版本号">V{{ traceData.version_no ?? 1 }}</el-descriptions-item>
        <el-descriptions-item label="Hash">
          <span class="mono" :title="traceData.hash || '-'">
            {{ shortText(traceData.hash || "-", 22, 16) }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="安全说明">
          {{ traceData.security?.security_reason || "暂时没有安全说明" }}
        </el-descriptions-item>
      </el-descriptions>

      <el-timeline>
        <el-timeline-item
          v-for="trace in traceData.traces"
          :key="trace.id"
          :timestamp="trace.created_at"
          placement="top"
        >
          <el-card shadow="never" class="trace-card">
            <div class="trace-event-head">
              <div class="trace-title-row">
                <strong>{{ eventLabel(trace.event_type) }}</strong>
                <el-tag effect="plain">{{ actorLabel(trace) }}</el-tag>
              </div>
              <span class="mono" :title="trace.file_hash || '-'">
                {{ shortText(trace.file_hash || "-", 20, 16) }}
              </span>
            </div>

            <p class="trace-summary">{{ detailSummary(trace) }}</p>

            <div v-if="parseDetail(trace.detail).length" class="detail-grid">
              <div
                v-for="item in parseDetail(trace.detail)"
                :key="`${trace.id}-${item.key}`"
                class="detail-item"
              >
                <span class="detail-label">{{ item.label }}</span>
                <strong class="detail-value" :title="item.value">{{ item.value }}</strong>
              </div>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>
  </el-dialog>
</template>

<style scoped>
.trace-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.trace-head strong {
  display: block;
  margin-bottom: 6px;
  font-size: 1.08rem;
}

.trace-head p {
  margin: 0;
  color: #6b6157;
  line-height: 1.6;
}

.trace-stack {
  display: grid;
  gap: 22px;
}

.trace-card {
  border-radius: 18px;
}

.trace-event-head {
  display: grid;
  gap: 8px;
}

.trace-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.trace-summary {
  margin: 12px 0 0;
  color: #5f564c;
  line-height: 1.6;
  font-weight: 500;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.detail-item {
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(244, 238, 228, 0.72);
}

.detail-label {
  display: block;
  margin-bottom: 6px;
  color: #7a7268;
  font-size: 0.82rem;
}

.detail-value {
  display: block;
  color: #2f2a24;
  line-height: 1.5;
  word-break: break-word;
}

.owner-name {
  margin-left: 10px;
  color: #6b6157;
}

.mono {
  word-break: break-all;
  font-family: "Cascadia Code", "Consolas", monospace;
}

@media (max-width: 720px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
