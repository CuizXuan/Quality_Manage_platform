<template>
  <div class="app-layout">
    <AppHeader />
    <div class="app-body">
      <Sidebar @load-request="onLoadRequest" />
      <main class="app-main">
        <router-view />
      </main>
    </div>
    <StatusBar />
  </div>
</template>

<script setup>
import AppHeader from './components/common/AppHeader.vue'
import Sidebar from './components/common/Sidebar.vue'
import StatusBar from './components/common/StatusBar.vue'

function onLoadRequest() {
  // Sidebar 加载请求后，可以在这里做后续处理
}
</script>

<style>
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}
.app-body {
  display: flex;
  flex: 1;
  margin-top: var(--header-height);
  margin-bottom: var(--status-bar-height);
}
.app-main {
  flex: 1;
  margin-left: var(--sidebar-width);
  overflow: hidden;
}
</style>
