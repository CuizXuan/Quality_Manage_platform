import axios from 'axios'

const request = axios.create({
  baseURL: '/api',   // Vite proxy 会转发到 http://localhost:8000
  timeout: 60000,
})

// 封装常用 REST 方法，Vue 组件直接调用更直观
const http = {
  get<T = any>(url: string, config?: any): Promise<T> {
    return request.get(url, config)
  },
  post<T = any>(url: string, data?: any, config?: any): Promise<T> {
    return request.post(url, data, config)
  },
  put<T = any>(url: string, data?: any, config?: any): Promise<T> {
    return request.put(url, data, config)
  },
  delete<T = any>(url: string, config?: any): Promise<T> {
    return request.delete(url, config)
  },
  patch<T = any>(url: string, data?: any, config?: any): Promise<T> {
    return request.patch(url, data, config)
  },
}

export default http
