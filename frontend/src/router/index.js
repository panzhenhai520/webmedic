import { createRouter, createWebHistory } from 'vue-router'
import DoctorWorkbench from '@/views/DoctorWorkbench.vue'
import DocumentManagement from '@/views/DocumentManagement.vue'
import SessionHistory from '@/views/SessionHistory.vue'
import VocabularyManagement from '@/views/VocabularyManagement.vue'

const routes = [
  {
    path: '/',
    name: 'DoctorWorkbench',
    component: DoctorWorkbench,
    meta: {
      title: 'WebMedic - 医生工作站'
    }
  },
  {
    path: '/sessions',
    name: 'SessionHistory',
    component: SessionHistory,
    meta: {
      title: 'WebMedic - 会话历史'
    }
  },
  {
    path: '/documents',
    name: 'DocumentManagement',
    component: DocumentManagement,
    meta: {
      title: 'WebMedic - 病历管理'
    }
  },
  {
    path: '/vocabulary',
    name: 'VocabularyManagement',
    component: VocabularyManagement,
    meta: {
      title: 'WebMedic - 医学词库维护'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫：设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router
