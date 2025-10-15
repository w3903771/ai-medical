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
        <el-form-item label="昵称" prop="name">
          <el-input v-model="accountForm.name" disabled>
            <template #append>
              <el-button @click="handleEditName">修改</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="accountForm.email" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="accountForm.gender">
            <el-radio :label="0">男</el-radio>
            <el-radio :label="1">女</el-radio>
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
        <el-form-item label="角色">
          <el-tag type="info">{{ accountForm.role || 'user' }}</el-tag>
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

    <!-- 昵称修改对话框 -->
    <el-dialog
      v-model="nameDialogVisible"
      title="修改昵称"
      width="30%"
    >
      <el-form
        ref="nameFormRef"
        :model="{ newName }"
        :rules="{ newName: [{ required: true, message: '请输入新昵称', trigger: 'blur' }] }"
        label-width="100px"
      >
        <el-form-item label="新昵称" prop="newName">
          <el-input v-model="newName" placeholder="请输入新昵称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="nameDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitName">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useSettingsStore } from '@/stores/settings'
import { useAccountStore } from '@/stores/account'

const settingsStore = useSettingsStore()
const { accountForm, passwordForm } = settingsStore
const accountStore = useAccountStore()

// 表单引用
const accountFormRef = ref(null)
const passwordFormRef = ref(null)
const nameFormRef = ref(null)

// 昵称修改对话框
const nameDialogVisible = ref(false)
const newName = ref('')

// 账号表单验证规则
const accountFormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
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

// 处理昵称修改按钮点击
const handleEditName = () => {
  newName.value = accountForm.name
  nameDialogVisible.value = true
}

// 提交昵称修改
const handleSubmitName = async () => {
  try {
    await nameFormRef.value.validate()
    // 更新本地字段并调用保存（与后端同步）
    accountForm.name = newName.value
    const ok = await accountStore.saveAccountInfo()
    if (ok) {
      ElMessage.success('昵称修改成功')
      nameDialogVisible.value = false
    } else {
      ElMessage.error('昵称修改失败')
    }
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

const handleUpdateAccount = async () => {
  try {
    await accountFormRef.value.validate()
    const ok = await accountStore.saveAccountInfo()
    if (ok) {
      ElMessage.success('账号信息更新成功')
    } else {
      ElMessage.error('账号信息更新失败')
    }
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
    const ok = await accountStore.changePassword()
    if (ok) {
      ElMessage.success('密码修改成功')
      resetPasswordForm()
    } else {
      ElMessage.error('密码修改失败')
    }
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

const resetPasswordForm = () => {
  passwordFormRef.value.resetFields()
}

// 页面挂载时，从后端加载账号信息（与当前登录用户同步）
onMounted(async () => {
  try {
    await accountStore.loadAccountInfo()
  } catch (e) {
    // 忽略加载错误（未登录或网络问题）
  }
})
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