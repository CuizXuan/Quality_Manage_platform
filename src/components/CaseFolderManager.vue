<template>
  <div class="folder-manager">
    <div class="toolbar">
      <el-button type="primary" size="small" @click="dialogRef?.open()">+ 新增分类</el-button>
    </div>
    <el-table :data="folders" stripe v-loading="loading" class="mt-2">
      <el-table-column prop="name" label="分类名称" min-width="150" />
      <el-table-column prop="sort_order" label="排序" width="100" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" link @click="openEdit(row)">编辑</el-button>
          <el-button size="small" link type="danger" @click="confirmDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <CaseFolderDialog ref="dialogRef" @refresh="fetchFolders" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getCaseFolders, deleteCaseFolder } from '@/api/caseFolders'
import { ElMessage, ElMessageBox } from 'element-plus'
import CaseFolderDialog from './CaseFolderDialog.vue'

const folders = ref<any[]>([])
const loading = ref(false)
const dialogRef = ref<any>(null)

async function fetchFolders() {
  loading.value = true
  try {
    const { data } = await getCaseFolders()
    folders.value = data
  } catch {
    ElMessage.error('加载分类失败')
  } finally {
    loading.value = false
  }
}

function openEdit(row: any) {
  dialogRef.value?.open(row)
}

async function confirmDelete(row: any) {
  try {
    await ElMessageBox.confirm(
      `确定要删除分类「${row.name}」吗？`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
    await deleteCaseFolder(row.id)
    ElMessage.success('删除成功')
    fetchFolders()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e?.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(fetchFolders)
</script>

<style scoped>
.folder-manager { padding: 0; }
.toolbar { margin-bottom: 8px; }
.mt-2 { margin-top: 8px; }
</style>