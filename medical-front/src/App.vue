<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

onMounted(() => {
  // 初始化用户信息
  userStore.initUserInfo()
})
</script>

<style>
#app {
  width: 100%;
  height: 100vh;
}

/* 页面保持静止，不进行全局位移动效 */
</style>