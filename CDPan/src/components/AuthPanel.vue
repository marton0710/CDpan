<script setup>
import { computed } from "vue";

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  activeTab: {
    type: String,
    default: "login",
  },
  registerForm: {
    type: Object,
    required: true,
  },
  loginForm: {
    type: Object,
    required: true,
  },
  submitting: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "update:modelValue",
  "update:activeTab",
  "register",
  "login",
]);

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

const currentTab = computed({
  get: () => props.activeTab,
  set: (value) => emit("update:activeTab", value),
});
</script>

<template>
  <el-dialog v-model="dialogVisible" width="460px" class="auth-dialog" destroy-on-close>
    <template #header>
      <div class="dialog-head">
        <strong>欢迎使用 CDPan</strong>
        <p>使用账号登录后即可进入文件工作台。</p>
      </div>
    </template>

    <el-tabs v-model="currentTab" stretch>
      <el-tab-pane label="登录" name="login">
        <el-form label-position="top" @submit.prevent="emit('login')">
          <el-form-item label="用户名">
            <el-input v-model="loginForm.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input
              v-model="loginForm.password"
              type="password"
              show-password
              placeholder="请输入密码"
            />
          </el-form-item>
          <el-button
            class="wide-button"
            type="primary"
            :loading="submitting"
            @click="emit('login')"
          >
            登录
          </el-button>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="注册" name="register">
        <el-form label-position="top" @submit.prevent="emit('register')">
          <el-form-item label="用户名">
            <el-input v-model="registerForm.username" placeholder="请创建用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input
              v-model="registerForm.password"
              type="password"
              show-password
              placeholder="请创建密码"
            />
          </el-form-item>
          <el-button
            class="wide-button"
            type="success"
            :loading="submitting"
            @click="emit('register')"
          >
            注册账号
          </el-button>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </el-dialog>
</template>

<style scoped>
.dialog-head strong {
  display: block;
  margin-bottom: 6px;
  font-size: 1.1rem;
}

.dialog-head p {
  margin: 0;
  color: #6b6157;
  line-height: 1.6;
}

.wide-button {
  width: 100%;
  margin-top: 8px;
}

</style>
