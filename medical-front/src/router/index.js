import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import Layout from '@/layout/Layout.vue'

const routes = [
  { path: '/login', name: 'login', component: () => import('@/views/Login.vue'), meta: { title: '登录', public: true } },
  { path: '/register', name: 'register', component: () => import('@/views/Register.vue'), meta: { title: '注册', public: true } },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页', icon: 'House' }
      },
      {
        path: 'indicators',
        name: 'indicators',
        component: () => import('@/views/Indicators.vue'),
        meta: { title: '指标数据', icon: 'DataAnalysis' }
      },
      {
        path: 'indicator/:id/:name',
        name: 'indicatorDetail',
        component: () => import('@/views/IndicatorDetail.vue'),
        meta: { title: '指标详情', activeMenu: '/indicators' }
      },
      {
        path: 'admissions',
        name: 'admissions',
        component: () => import('@/views/Admissions.vue'),
        meta: { title: '住院管理', icon: 'Document' }
      },
      {
        path: 'llm-interface',
        name: 'llmInterface',
        component: () => import('@/views/LLMInterface.vue'),
        meta: { title: '大模型界面', icon: 'ChatDotRound' }
      },
      // {
      //   path: 'knowledge',
      //   name: 'Knowledge',
      //   component: () => import('@/views/Knowledge.vue'),
      //   meta: { title: '知识库管理', icon: 'Collection' }
      // },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '设置', icon: 'Setting' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：未登录跳转到登录页
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const isPublic = to.meta?.public || ['/login', '/register'].includes(to.path)
  if (!isPublic && !userStore.isLoggedIn) {
    next({ path: '/login' })
  } else {
    next()
  }
})

export default router