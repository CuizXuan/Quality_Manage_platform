<template>
  <Teleport to="body">
    <div class="cyber-toast-container">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="cyber-toast"
          :class="`toast-${toast.type}`"
        >
          <div class="toast-icon">
            <svg v-if="toast.type === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            <svg v-else-if="toast.type === 'error'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
            <svg v-else-if="toast.type === 'warning'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
          </div>
          <div class="toast-content">
            <div class="toast-title">{{ toast.title }}</div>
            <div v-if="toast.message" class="toast-message">{{ toast.message }}</div>
          </div>
          <button class="toast-close" @click="toastStore.removeToast(toast.id)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()
const { toasts } = toastStore
</script>

<style scoped>
.cyber-toast-container {
  position: fixed;
  top: 80px;
  right: 16px;
  z-index: 99999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.cyber-toast {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  background: rgba(10, 12, 18, 0.92);
  border: 1px solid;
  border-radius: 6px;
  backdrop-filter: blur(12px);
  min-width: 280px;
  max-width: 360px;
  pointer-events: auto;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
}

.toast-success {
  border-color: #00C9A7;
}
.toast-success .toast-icon {
  color: #00C9A7;
}

.toast-error {
  border-color: #F43F5E;
}
.toast-error .toast-icon {
  color: #F43F5E;
}

.toast-warning {
  border-color: #F59E0B;
}
.toast-warning .toast-icon {
  color: #F59E0B;
}

.toast-info {
  border-color: #3B82F6;
}
.toast-info .toast-icon {
  color: #3B82F6;
}

.toast-icon {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  margin-top: 1px;
}

.toast-icon svg {
  width: 100%;
  height: 100%;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-size: 13px;
  font-weight: 500;
  color: #E4E4E7;
  line-height: 1.4;
}

.toast-message {
  font-size: 12px;
  color: #71717A;
  margin-top: 2px;
  line-height: 1.4;
}

.toast-close {
  flex-shrink: 0;
  width: 16px;
  height: 16px;
  padding: 0;
  border: none;
  background: none;
  color: #52525B;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.15s;
}

.toast-close:hover {
  color: #A1A1AA;
}

.toast-close svg {
  width: 100%;
  height: 100%;
}

/* Transitions */
.toast-enter-active {
  transition: all 0.3s cubic-bezier(0.21, 1.02, 0.73, 1);
}

.toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(40px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(40px);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>
