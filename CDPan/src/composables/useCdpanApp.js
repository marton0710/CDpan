import { computed, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";

const DEFAULT_API_BASE = (import.meta.env.VITE_API_BASE_URL || "/api").replace(
  /\/$/,
  ""
);

export function useCdpanApp() {
  const state = reactive({
    baseUrl: DEFAULT_API_BASE,
    token: localStorage.getItem("cdpan_token") || "",
    currentUsername: localStorage.getItem("cdpan_username") || "",
    files: [],
    loadingFiles: false,
    uploading: false,
    submittingAuth: false,
  });

  const registerForm = reactive({
    username: "",
    password: "",
  });

  const loginForm = reactive({
    username: "",
    password: "",
  });

  const uploadFile = ref(null);
  const traceDialog = reactive({
    visible: false,
    loading: false,
    data: null,
  });

  const isAuthenticated = computed(() => Boolean(state.token));
  const fileCountText = computed(() => `${state.files.length} 个文件`);
  const selectedFileName = computed(() => uploadFile.value?.name || "");

  const dashboardStats = computed(() => {
    const counts = summarizeLevels(state.files);
    const versionCount = state.files.filter((file) => (file.version_no || 1) > 1).length;
    const totalDownloads = state.files.reduce(
      (sum, file) => sum + Number(file.download_count || 0),
      0
    );

    return [
      {
        label: "托管文件",
        value: state.files.length,
        note: "当前账号下可访问的 PDF 文档",
      },
      {
        label: "高安全文件",
        value: counts.high,
        note: "签名有效且追踪链路完整",
      },
      {
        label: "版本变更",
        value: versionCount,
        note: "同一追踪链路下出现多个版本",
      },
      {
        label: "累计下载",
        value: totalDownloads,
        note: "按后端追踪记录汇总",
      },
    ];
  });

  const securityOverview = computed(() => {
    const counts = summarizeLevels(state.files);
    const duplicateVersionCount = state.files.reduce(
      (sum, file) => sum + Number(file.repeat_upload_count || 0),
      0
    );
    const warnings = [];

    if (counts.low > 0) {
      warnings.push(`有 ${counts.low} 个文件处于低安全等级，建议优先重新验签。`);
    }
    if (counts.medium > 0) {
      warnings.push(`有 ${counts.medium} 个文件存在版本变更或追踪不完整，需要人工复核。`);
    }
    if (duplicateVersionCount > 0) {
      warnings.push(`系统已识别 ${duplicateVersionCount} 次同版本重复上传，并进行了追踪归并。`);
    }
    if (warnings.length === 0) {
      warnings.push("当前文件库状态稳定，未发现明显的安全异常。");
    }

    return {
      high: counts.high,
      medium: counts.medium,
      low: counts.low,
      trustedRate: state.files.length
        ? `${Math.round((counts.high / state.files.length) * 100)}%`
        : "0%",
      warnings,
    };
  });

  function summarizeLevels(files) {
    return files.reduce(
      (summary, file) => {
        const level = file.security_level || "low";
        summary[level] = Number(summary[level] || 0) + 1;
        return summary;
      },
      { high: 0, medium: 0, low: 0 }
    );
  }

  function setToken(token, username = state.currentUsername) {
    state.token = token;
    state.currentUsername = username;

    if (token) {
      localStorage.setItem("cdpan_token", token);
      if (username) {
        localStorage.setItem("cdpan_username", username);
      }
    } else {
      localStorage.removeItem("cdpan_token");
      localStorage.removeItem("cdpan_username");
    }
  }

  function getApiUrl(path) {
    return `${state.baseUrl}${path}`;
  }

  async function request(path, options = {}) {
    const headers = new Headers(options.headers || {});
    if (state.token) {
      headers.set("Authorization", `Bearer ${state.token}`);
    }

    const response = await fetch(getApiUrl(path), {
      ...options,
      headers,
    });

    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json")
      ? await response.json()
      : await response.blob();

    if (!response.ok) {
      if (response.status === 401) {
        clearToken();
      }
      throw payload;
    }

    return payload;
  }

  function getSecurityText(level) {
    if (level === "high") {
      return "高安全";
    }
    if (level === "medium") {
      return "中风险";
    }
    return "低安全";
  }

  function getUploadTypeText(uploadType) {
    if (uploadType === "same_version") {
      return "重复上传同一版本";
    }
    if (uploadType === "restore_same_version") {
      return "已恢复之前删除的同一版本";
    }
    if (uploadType === "new_version") {
      return "识别为同一文档的新版本";
    }
    return "新建文档";
  }

  function normalizeErrorMessage(error, fallback) {
    if (!error) {
      return fallback;
    }

    if (typeof error === "string") {
      return error;
    }

    if (typeof error.detail === "string") {
      return error.detail;
    }

    if (typeof error.message === "string") {
      return error.message;
    }

    if (typeof error.detail?.message === "string") {
      return error.detail.message;
    }

    if (typeof error.message?.msg === "string") {
      return error.message.msg;
    }

    return fallback;
  }

  async function loadFiles() {
    if (!state.token) {
      state.files = [];
      return;
    }

    state.loadingFiles = true;
    try {
      const result = await request("/files");
      state.files = result.message || [];
    } catch (error) {
      state.files = [];
      ElMessage.error(normalizeErrorMessage(error, "获取文件列表失败"));
    } finally {
      state.loadingFiles = false;
    }
  }

  async function submitRegister() {
    state.submittingAuth = true;
    try {
      await request("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(registerForm),
      });

      loginForm.username = registerForm.username;
      registerForm.username = "";
      registerForm.password = "";
      ElMessage.success("注册成功，请直接登录");
      return true;
    } catch (error) {
      ElMessage.error(normalizeErrorMessage(error, "注册失败"));
      return false;
    } finally {
      state.submittingAuth = false;
    }
  }

  async function submitLogin() {
    state.submittingAuth = true;
    try {
      const result = await request("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(loginForm),
      });

      setToken(result.message.token, loginForm.username);
      loginForm.password = "";
      await loadFiles();
      ElMessage.success("登录成功");
      return true;
    } catch (error) {
      ElMessage.error(normalizeErrorMessage(error, "登录失败"));
      return false;
    } finally {
      state.submittingAuth = false;
    }
  }

  async function submitUpload() {
    if (!uploadFile.value) {
      ElMessage.warning("请先选择一个 PDF 文件");
      return;
    }

    const formData = new FormData();
    formData.append("file", uploadFile.value);

    state.uploading = true;
    try {
      const result = await request("/upload", {
        method: "POST",
        body: formData,
      });

      uploadFile.value = null;
      await loadFiles();
      ElMessage.success(`上传完成：${getUploadTypeText(result.message.upload_type)}`);
    } catch (error) {
      ElMessage.error(normalizeErrorMessage(error, "上传失败"));
    } finally {
      state.uploading = false;
    }
  }

  async function downloadFile(file) {
    try {
      const blob = await request(`/download/${file.id}`);
      const objectUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = file.filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(objectUrl);
      await loadFiles();
      ElMessage.success("文件下载已开始");
    } catch (error) {
      ElMessage.error(normalizeErrorMessage(error, "下载失败"));
    }
  }

  async function verifyFile(file) {
    try {
      const result = await request(`/verify/${file.id}`);
      await loadFiles();
      const statusText = result.message.is_valid ? "签名有效" : "签名无效";
      ElMessage.success(
        `${statusText}，当前等级：${getSecurityText(result.message.security.security_level)}`
      );
    } catch (error) {
      ElMessage.error(normalizeErrorMessage(error, "验签失败"));
    }
  }

  async function showTrace(file) {
    traceDialog.visible = true;
    traceDialog.loading = true;
    traceDialog.data = null;

    try {
      const result = await request(`/trace/${file.id}`);
      traceDialog.data = result.message;
    } catch (error) {
      traceDialog.visible = false;
      ElMessage.error(normalizeErrorMessage(error, "获取追踪详情失败"));
    } finally {
      traceDialog.loading = false;
    }
  }

  async function deleteFile(file) {
    try {
      await ElMessageBox.confirm(
        `确认删除 ${file.filename} 吗？该操作会同时删除数据库记录和存储文件。`,
        "删除确认",
        {
          type: "warning",
          confirmButtonText: "删除",
          cancelButtonText: "取消",
        }
      );
    } catch {
      return;
    }

    try {
      await request(`/delete/${file.id}`, { method: "POST" });
      await loadFiles();
      ElMessage.success("文件已删除");
    } catch (error) {
      ElMessage.error(normalizeErrorMessage(error, "删除失败"));
    }
  }

  function clearToken() {
    setToken("", "");
    state.files = [];
    traceDialog.visible = false;
    traceDialog.data = null;
  }

  function onPickFile(file) {
    uploadFile.value = file;
  }

  if (state.token) {
    loadFiles();
  }

  return {
    state,
    registerForm,
    loginForm,
    traceDialog,
    isAuthenticated,
    fileCountText,
    selectedFileName,
    dashboardStats,
    securityOverview,
    getSecurityText,
    submitRegister,
    submitLogin,
    submitUpload,
    downloadFile,
    verifyFile,
    showTrace,
    deleteFile,
    loadFiles,
    clearToken,
    onPickFile,
  };
}
