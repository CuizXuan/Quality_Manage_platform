import request from '@/utils/request'

export function getCaseFolders() {
  return request.get('/case-folders')
}

export function getCaseFoldersFlat() {
  return request.get('/case-folders/flat')
}

export function createCaseFolder(data: { name: string; parent_id?: number; sort_order?: number }) {
  return request.post('/case-folders', data)
}

export function updateCaseFolder(id: number, data: { name?: string; parent_id?: number; sort_order?: number }) {
  return request.put(`/case-folders/${id}`, data)
}

export function deleteCaseFolder(id: number) {
  return request.delete(`/case-folders/${id}`)
}

export function ensureTerminalFolder() {
  return request.post('/case-folders/ensure-terminal-folder')
}

export function ensureRootFolder() {
  return request.post('/case-folders/ensure-root-folder')
}
