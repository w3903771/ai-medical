<template>
  <div class="auth-container">
    <div class="auth-left">
      <div class="brand">
        <i class="el-icon-medical"></i>
        <div class="brand-text">
          <h1>医疗数据管理平台</h1>
        </div>
      </div>
      <div class="decor">
        <div class="circle c1"></div>
        <div class="circle c2"></div>
        <div class="circle c3"></div>
      </div>
    </div>
    <div class="auth-right">
      <transition name="fade-card" appear>
      <el-card class="auth-card" shadow="never">
        <template #header>
          <div class="card-header">
            <h2>欢迎登录</h2>
            <el-button text type="primary" @click="goRegister">去注册</el-button>
          </div>
        </template>
        <el-form :model="form" :rules="rules" ref="formRef" label-width="90px">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" placeholder="请输入密码" type="password" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" class="w-full" @click="handleLogin">登录</el-button>
          </el-form-item>
        </el-form>
        <div class="tips">
          开发可用 Mock 管理员：用户名 admin / 密码 admin
        </div>
      </el-card>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const formRef = ref(null)
const form = ref({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = () => {
  formRef.value.validate(async valid => {
    if (!valid) return
    loading.value = true
    try {
      await userStore.login({ username: form.value.username, password: form.value.password })
      ElMessage.success('登录成功')
      router.push('/dashboard')
    } catch (e) {
      ElMessage.error(e?.message || '登录失败')
    } finally {
      loading.value = false
    }
  })
}

const goRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.auth-container {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  height: 100vh;
  background: linear-gradient(135deg, #f6f9ff 0%, #f0f4ff 100%);
}
.auth-left {
  position: relative;
  padding: 48px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: #2b3a67;
  overflow: hidden;
}
.brand {
  display: flex;
  align-items: center;
  gap: 16px;
}
.brand-text h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
}
.decor .circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(99, 132, 255, 0.15);
  animation: float 8s ease-in-out infinite;
}
.decor .c1 { width: 220px; height: 220px; left: -60px; top: -60px; }
.decor .c2 { width: 320px; height: 320px; right: -80px; bottom: -60px; animation-delay: 1.2s; }
.decor .c3 { width: 140px; height: 140px; right: 120px; top: 200px; animation-delay: 2s; }

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.auth-right {
  display: flex;
  align-items: center;
  justify-content: center;
}
.auth-card {
  width: 460px;
  border-radius: 16px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.w-full { width: 100%; }
.tips { margin-top: 8px; color: #909399; font-size: 12px; }

/* 仅表单卡片淡入，不对整页进行位移 */
.fade-card-enter-active,
.fade-card-leave-active {
  transition: opacity 0.28s ease;
}
.fade-card-enter-from,
.fade-card-leave-to {
  opacity: 0;
}

@media (max-width: 900px) {
  .auth-container { grid-template-columns: 1fr; }
  .auth-left { display: none; }
}
</style>