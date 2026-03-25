<script setup>
defineEmits(["open-login", "open-register"]);
</script>

<template>
  <section class="hero-card">
    <div class="hero-copy">
      <p class="eyebrow">Secure PDF Hub</p>
      <h1>让用户直接上传、签名、追踪和管理 PDF 文件</h1>
      <p class="hero-text">
        CDPan 提供用户认证、文件工作台、数字签名、版本识别和安全追踪能力，
        可以作为可直接部署的 PDF 文件服务入口。
      </p>

      <div class="hero-actions">
        <el-button type="primary" size="large" @click="$emit('open-register')">
          立即注册
        </el-button>
        <el-button size="large" plain @click="$emit('open-login')">
          已有账号，去登录
        </el-button>
      </div>

      <div class="hero-highlights">
        <div class="highlight-item">
          <strong>文件工作台</strong>
          <span>面向真实用户的上传、下载、验签与删除流程</span>
        </div>
        <div class="highlight-item">
          <strong>安全视图</strong>
          <span>基于哈希、签名和追踪记录展示安全等级</span>
        </div>
        <div class="highlight-item">
          <strong>部署友好</strong>
          <span>支持直接部署到服务器，供真实用户访问和使用</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-card {
  border-radius: 32px;
  overflow: hidden;
}

.hero-copy {
  padding: 40px;
  border-radius: 32px;
  background:
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.12), transparent 28%),
    linear-gradient(140deg, rgba(17, 94, 89, 0.98), rgba(15, 118, 110, 0.82));
  color: #fffbf5;
  box-shadow: 0 22px 48px rgba(15, 118, 110, 0.16);
}

.eyebrow {
  margin: 0 0 10px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  font-size: 0.76rem;
  opacity: 0.78;
}

h1 {
  margin: 0 0 14px;
  max-width: 760px;
  font-size: clamp(2.2rem, 4vw, 3.6rem);
  line-height: 1.06;
}

.hero-text {
  margin: 0;
  max-width: 720px;
  color: rgba(255, 250, 244, 0.88);
  line-height: 1.72;
}

.hero-actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 26px;
}

.hero-highlights {
  margin-top: 28px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.highlight-item {
  padding: 18px;
  border-radius: 22px;
  background: rgba(255, 251, 245, 0.1);
  backdrop-filter: blur(8px);
}

.highlight-item strong {
  display: block;
  margin-bottom: 8px;
  font-size: 1rem;
}

.highlight-item span {
  color: rgba(255, 250, 244, 0.82);
  line-height: 1.62;
  font-size: 0.94rem;
}

@media (max-width: 960px) {
  .hero-copy {
    padding: 28px;
  }

  .hero-highlights {
    grid-template-columns: 1fr;
  }
}
</style>
