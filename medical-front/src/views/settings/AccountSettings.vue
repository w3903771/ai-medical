<template>
  <div class="account-settings">
    <el-card class="section-card" shadow="never">
      <template #header>
        <h2>账号信息</h2>
      </template>
      
      <el-form
        ref="accountFormRef"
        :model="accountForm"
        :rules="accountFormRules"
        label-width="100px"
        class="account-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="accountForm.username" disabled>
            <template #append>
              <el-button @click="handleEditUsername">修改</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="accountForm.email" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="accountForm.phone" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="accountForm.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="出生日期" prop="birthDate">
          <el-date-picker
            v-model="accountForm.birthDate"
            type="date"
            placeholder="选择出生日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleUpdateAccount">保存修改</el-button>
          <el-button @click="resetAccountForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="section-card" shadow="never">
      <template #header>
        <h2>密码修改</h2>
      </template>
      
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordFormRules"
        label-width="100px"
        class="password-form"
      >
        <el-form-item label="当前密码" prop="oldPassword">
          <el-input
            v-model="passwordForm.oldPassword"
            type="password"
            show-password
            placeholder="请输入当前密码"
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            show-password
            placeholder="请输入新密码"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleUpdatePassword">修改密码</el-button>
          <el-button @click="resetPasswordForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用户名修改对话框 -->
    <el-dialog
      v-model="usernameDialogVisible"
      title="修改用户名"
      width="30%"
    >
      <el-form
        ref="usernameFormRef"
        :model="{ newUsername }"
        :rules="{ newUsername: [{ required: true, message: '请输入新用户名', trigger: 'blur' }] }"
        label-width="100px"
      >
        <el-form-item label="新用户名" prop="newUsername">
          <el-input v-model="newUsername" placeholder="请输入新用户名" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="usernameDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitUsername">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()
const { accountForm, passwordForm } = settingsStore

// 表单引用
const accountFormRef = ref(null)
const passwordFormRef = ref(null)
const usernameFormRef = ref(null)

// 用户名修改对话框
const usernameDialogVisible = ref(false)
const newUsername = ref('')

// 账号表单验证规则
const accountFormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

// 密码表单验证规则
const passwordFormRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 处理用户名修改按钮点击
const handleEditUsername = () => {
  newUsername.value = accountForm.username
  usernameDialogVisible.value = true
}

// 提交用户名修改
const handleSubmitUsername = async () => {
  try {
    await usernameFormRef.value.validate()
    // 这里可以添加API调用来更新用户名
    accountForm.username = newUsername.value
    ElMessage.success('用户名修改成功')
    usernameDialogVisible.value = false
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

const handleUpdateAccount = async () => {
  try {
    await accountFormRef.value.validate()
    ElMessage.success('账号信息更新成功')
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

const resetAccountForm = () => {
  accountFormRef.value.resetFields()
}

const handleUpdatePassword = async () => {
  try {
    await passwordFormRef.value.validate()
    ElMessage.success('密码修改成功')
    resetPasswordForm()
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

const resetPasswordForm = () => {
  passwordFormRef.value.resetFields()
}
</script>

<style scoped>
.account-settings {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-card {
  margin-bottom: 0;
}

.account-form,
.password-form {
  max-width: 500px;
}
</style>