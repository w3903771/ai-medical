import request from '@/utils/request'

export function getIndicators(params) {
  return request.get('/indicators', { params })
}

export function getIndicator(id) {
  return request.get(`/indicators/${id}`)
}

export function createIndicator(data) {
  return request.post('/indicators', data)
}

export function updateIndicator(id, data) {
  return request.put(`/indicators/${id}`, data)
}

export function deleteIndicator(id) {
  return request.delete(`/indicators/${id}`)
}

export function listRecords(id, params) {
  return request.get(`/indicators/${id}/records`, { params })
}

export function createRecord(id, data) {
  return request.post(`/indicators/${id}/records`, data)
}

export function updateRecord(id, recordId, data) {
  return request.patch(`/indicators/${id}/records/${recordId}`, data)
}

export function deleteRecord(id, recordId) {
  return request.delete(`/indicators/${id}/records/${recordId}`)
}

export function getDetail(id) {
  return request.get(`/indicators/${id}/detail`)
}

export function updateDetail(id, data) {
  return request.put(`/indicators/${id}/detail`, data)
}