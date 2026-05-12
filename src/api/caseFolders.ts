import request from '@/utils/request'

export function getCaseFolders() {
  return request.get('/api/case-folders')
}

export function createCaseFolder(data: { name: string; parent_id?: number; sort_order?: number }) {
  return request.post('/api/case-folders', data)
}

export function updateCaseFolder(id: number, data: { name?: string; parent_id?: number; sort_order?: number }) {
  return request.put(`/api/case-folders/${id}`, data)
}

export function deleteCaseFolder(id: number) {
  return request.delete(`/api/case-folders/${id}`)
}
