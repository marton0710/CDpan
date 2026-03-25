<script setup>
import { reactive } from "vue";
import AuthPanel from "./components/AuthPanel.vue";
import FileListPanel from "./components/FileListPanel.vue";
import HeroSection from "./components/HeroSection.vue";
import OverviewPanel from "./components/OverviewPanel.vue";
import SecurityPanel from "./components/SecurityPanel.vue";
import TraceDialog from "./components/TraceDialog.vue";
import UploadPanel from "./components/UploadPanel.vue";
import { useCdpanApp } from "./composables/useCdpanApp";

const app = useCdpanApp();
const authDialog = reactive({
  visible: false,
  tab: "login",
});

function openAuthDialog(tab = "login") {
  authDialog.tab = tab;
  authDialog.visible = true;
}

async function handleLogin() {
  const success = await app.submitLogin();
  if (success) {
    authDialog.visible = false;
  }
}

async function handleRegister() {
  const success = await app.submitRegister();
  if (success) {
    authDialog.tab = "login";
  }
}
</script>

<template>
  <div class="app-shell">
    <div class="ambient ambient-a"></div>
    <div class="ambient ambient-b"></div>
    <div class="ambient ambient-c"></div>

    <header class="site-header">
      <div class="brand-block">
        <div class="brand-mark">CD</div>
        <div>
          <p class="brand-name">CDPan</p>
          <p class="brand-subtitle">面向 PDF 交付、签名与追踪的安全文档平台</p>
        </div>
      </div>

      <div v-if="app.isAuthenticated.value" class="session-actions">
        <div class="session-copy">
          <span class="session-label">当前账号</span>
          <strong>{{ app.state.currentUsername || "已登录用户" }}</strong>
        </div>
        <el-button :loading="app.state.loadingFiles" plain @click="app.loadFiles">
          刷新文件
        </el-button>
        <el-button type="danger" plain @click="app.clearToken">退出登录</el-button>
      </div>

      <div v-else class="guest-actions">
        <el-button plain @click="openAuthDialog('login')">登录</el-button>
        <el-button type="primary" @click="openAuthDialog('register')">注册账号</el-button>
      </div>
    </header>

    <main v-if="!app.isAuthenticated.value" class="landing-page">
      <HeroSection
        @open-login="openAuthDialog('login')"
        @open-register="openAuthDialog('register')"
      />

      <section class="landing-grid landing-grid-wide">
        <section class="feature-stack">
          <el-card class="feature-card" shadow="hover">
            <template #header>
              <div class="card-title-row">
                <span>使用流程</span>
                <el-tag type="primary" effect="plain">3 Steps</el-tag>
              </div>
            </template>

            <div class="feature-copy">
              <p>1. 用户注册并登录后进入个人文件工作台。</p>
              <p>2. 上传 PDF 后，系统自动执行哈希、签名和追踪识别。</p>
              <p>3. 在工作台中完成下载、验签、版本查看和安全复核。</p>
            </div>
          </el-card>

          <el-card class="feature-card" shadow="hover">
            <template #header>
              <div class="card-title-row">
                <span>平台能力</span>
                <el-tag type="success" effect="plain">PDF Only</el-tag>
              </div>
            </template>

            <ul class="feature-list">
              <li>用户登录后即可上传、下载、删除和验签 PDF 文件。</li>
              <li>同一文档支持基于 tracking ID 的版本追踪与安全分级。</li>
              <li>下载、验签、重复上传等行为会进入后端追踪链路。</li>
            </ul>
          </el-card>
        </section>

        <section class="feature-stack">
          <el-card class="feature-card" shadow="hover">
            <template #header>
              <div class="card-title-row">
                <span>安全能力</span>
                <el-tag type="warning" effect="plain">Signed & Tracked</el-tag>
              </div>
            </template>

            <div class="feature-copy">
              <p>文件级哈希用于确认二进制内容是否一致。</p>
              <p>签名、追踪和版本链路组合后，可直接在界面内看到安全等级。</p>
              <p>同一文档重复上传或新版本上传会被区分记录，不再只是简单重名文件。</p>
            </div>
          </el-card>

          <el-card class="feature-card" shadow="hover">
            <template #header>
              <div class="card-title-row">
                <span>部署能力</span>
                <el-tag type="success" effect="plain">Server Ready</el-tag>
              </div>
            </template>

            <div class="feature-copy">
              <p>界面可直接部署在服务器，对用户仅暴露业务能力，不展示底层接口地址。</p>
              <p>支持与现有后端联动，适合部署为团队或客户可直接访问的 PDF 平台。</p>
              <p>前后端可同域或分离部署，部署细节保留给运维配置，不在界面层暴露。</p>
            </div>
          </el-card>
        </section>
      </section>
    </main>

    <main v-else class="workspace-page">
      <section class="workspace-hero">
        <div class="workspace-copy">
          <p class="workspace-eyebrow">Document Workspace</p>
          <h1>我的文件中心</h1>
          <p>
            文件上传后会自动进入签名与追踪链路。你可以在这里统一查看版本状态、
            安全等级、下载记录和验签结果。
          </p>
        </div>

        <el-card class="workspace-meta" shadow="hover">
          <div class="meta-item">
            <span>受保护资源</span>
            <strong>已启用登录守卫</strong>
          </div>
          <div class="meta-item">
            <span>会话模式</span>
            <strong>JWT Bearer</strong>
          </div>
        </el-card>
      </section>

      <OverviewPanel :stats="app.dashboardStats.value" />

      <section class="workspace-grid">
        <div class="workspace-side">
          <UploadPanel
            :disabled="!app.isAuthenticated.value"
            :loading-files="app.state.loadingFiles"
            :uploading="app.state.uploading"
            :selected-file-name="app.selectedFileName.value"
            @pick-file="app.onPickFile"
            @upload="app.submitUpload"
            @refresh="app.loadFiles"
          />

          <SecurityPanel :summary="app.securityOverview.value" />
        </div>

        <FileListPanel
          :files="app.state.files"
          :has-token="app.isAuthenticated.value"
          :loading="app.state.loadingFiles"
          :file-count-text="app.fileCountText.value"
          :security-text="app.getSecurityText"
          @download="app.downloadFile"
          @verify="app.verifyFile"
          @trace="app.showTrace"
          @delete="app.deleteFile"
        />
      </section>
    </main>

    <TraceDialog
      v-model="app.traceDialog.visible"
      :loading="app.traceDialog.loading"
      :trace-data="app.traceDialog.data"
      :security-text="app.getSecurityText"
    />

    <AuthPanel
      v-model="authDialog.visible"
      v-model:active-tab="authDialog.tab"
      :register-form="app.registerForm"
      :login-form="app.loginForm"
      :submitting="app.state.submittingAuth"
      @register="handleRegister"
      @login="handleLogin"
    />
  </div>
</template>
