import request from '@/utils/request'

export function listCategories(params) {
  return request.get('/categories', { params })
}

export function getCategory(id) {
  return request.get(`/categories/${id}`)
}

export function getCategoryIndicators(id, params) {
  return request.get(`/categories/${id}/indicators`, { params })
}