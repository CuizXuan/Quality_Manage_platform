<template>
  <div class="folder-manager">
    <div class="toolbar">
      <el-button type="primary" size="small" @click="dialogRef?.open()">+ 新增分类</el-button>
    </div>

    <el-table
      :data="folderTree"
      row-key="id"
      :tree-props="{ children: 'children' }"
      default-expand-all
      v-loading="loading"
      class="cyber-table mt-2"
    >
      <el-table-column prop="name" label="分类名称" min-width="200">
        <template #default="{ row }">
          <span class="folder-name">
            <span v-if="row.is_fixed" class="fixed-badge">SYSTEM</span>
            {{ row.name }}
          </span>
        </template>
      </el-table-column>

      <el-table-column prop="sort_order" label="排序" width="100" />

      <el-table-column prop="parent_id" label="上级目录" width="150">
        <template #default="{ row }">
          {{ getParentName(row.parent_id) || '-' }}
        </template>
      </el-table-column>

      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <span v-if="row.is_fixed" class="fixed-text">系统目录</span>
          <template v-else>
            <el-button size="small" link @click="openEdit(row)">编辑</el-button>
            <el-button size="small" link type="danger" @click="confirmDelete(row)">删除</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <CaseFolderDialog ref="dialogRef" @refresh="fetchFolders" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deleteCaseFolder, ensureRootFolder, getCaseFolders } from '@/api/caseFolders'
import CaseFolderDialog from './CaseFolderDialog.vue'

interface FolderNode {
  id: number
  name: string
  parent_id: number | null
  sort_order: number
  children: FolderNode[]
  is_fixed: boolean
}

const folders = ref<FolderNode[]>([])
const loading = ref(false)
const dialogRef = ref<InstanceType<typeof CaseFolderDialog> | null>(null)

const folderTree = computed(() => folders.value)
const flatFolders = computed(() => flattenFolders(folders.value))

function flattenFolders(list: FolderNode[]): FolderNode[] {
  return list.flatMap(folder => [
    folder,
    ...flattenFolders(folder.children || []),
  ])
}

function getParentName(parentId: number | null): string {
  if (parentId == null) return ''
  return flatFolders.value.find(folder => folder.id === parentId)?.name || ''
}

async function fetchFolders() {
  loading.value = true
  try {
    await ensureRootFolder()
    const res = await getCaseFolders()
    folders.value = res.data || []
  } catch {
    ElMessage.error('加载分类失败')
  } finally {
    loading.value = false
  }
}

function openEdit(row: FolderNode) {
  dialogRef.value?.open(row)
}

async function confirmDelete(row: FolderNode) {
  if (row.is_fixed) {
    ElMessage.warning('系统目录无法删除')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除分类「${row.name}」吗？`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
    )
    await deleteCaseFolder(row.id)
    ElMessage.success('删除成功')
    await fetchFolders()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e?.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(fetchFolders)
</script>

<style scoped>
.folder-manager {
  padding: 0;
}

.toolbar {
  margin-bottom: 8px;
  padding-top: 16px;
}

.mt-2 {
  margin-top: 8px;
}

.folder-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.fixed-badge {
  padding: 2px 6px;
  border: 1px solid var(--neon-cyan, #0ff);
  border-radius: 4px;
  color: var(--neon-cyan, #0ff);
  font-size: 11px;
  font-weight: 700;
}

.fixed-text {
  color: var(--text-tertiary, #666);
  font-size: 13px;
}

:deep(.el-table) {
  --el-table-bg-color: var(--bg-panel, #0d0d14);
  --el-table-tr-bg-color: var(--bg-panel, #0d0d14);
  --el-table-header-bg-color: var(--bg-secondary, #0a0a0f);
  --el-table-header-text-color: var(--neon-cyan, #0ff);
  --el-table-text-color: var(--text-primary, #e0e0e0);
  --el-table-border-color: var(--border-default, rgba(0, 255, 255, 0.2));
  --el-table-row-hover-bg-color: rgba(0, 255, 255, 0.05);
}

:deep(.el-table th.el-table__cell) {
  background: var(--bg-secondary, #0a0a0f) !important;
  color: var(--neon-cyan, #0ff) !important;
  font-weight: 600;
}

:deep(.el-table td.el-table__cell) {
  background: var(--bg-panel, #0d0d14) !important;
  color: var(--text-primary, #e0e0e0) !important;
  border-color: var(--border-default, rgba(0, 255, 255, 0.2)) !important;
}

:deep(.el-table__body tr:hover > td.el-table__cell) {
  background: rgba(0, 255, 255, 0.05) !important;
}
</style>
