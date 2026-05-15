<template>
  <CyberModal
    v-model="visible"
    :title="isEdit ? '编辑分类' : '新增分类'"
    size="small"
    :confirm-text="isEdit ? '保存' : '创建'"
    :loading="loading"
    @confirm="submit"
    @cancel="close"
    @after-close="resetForm"
  >
    <div class="form-group">
      <label class="form-label">分类名称</label>
      <input
        v-model="form.name"
        class="form-input"
        type="text"
        placeholder="请输入分类名称"
        maxlength="200"
        :disabled="form.is_fixed"
        @keydown.enter="submit"
      />
    </div>

    <div class="form-group">
      <label class="form-label">上级分类</label>
      <el-cascader
        v-model="form.parent_id"
        :options="folderOptions"
        :props="cascaderProps"
        placeholder="请选择上级分类"
        filterable
        append-to-body
        popper-class="folder-cascader-popper"
        class="folder-cascader"
        :disabled="form.is_fixed"
      />
    </div>

    <div class="form-group">
      <label class="form-label">排序</label>
      <input
        v-model.number="form.sort_order"
        class="form-input form-input--number"
        type="number"
        min="0"
        max="9999"
        :disabled="form.is_fixed"
      />
    </div>
  </CyberModal>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createCaseFolder, getCaseFolders, updateCaseFolder } from '@/api/caseFolders'
import CyberModal from '@/components/common/modal/CyberModal.vue'

interface FolderNode {
  id: number
  name: string
  parent_id: number | null
  sort_order: number
  children?: FolderNode[]
  is_fixed?: boolean
  label?: string
}

const emit = defineEmits<{
  (e: 'refresh'): void
}>()

const cascaderProps = {
  checkStrictly: true,
  emitPath: false,
  label: 'label',
  value: 'id',
}

const visible = ref(false)
const isEdit = ref(false)
const editingId = ref<number | null>(null)
const loading = ref(false)
const rawFolders = ref<FolderNode[]>([])
const form = ref({
  name: '',
  parent_id: null as number | null,
  sort_order: 0,
  is_fixed: false,
})

const folderOptions = computed(() => toOptions(rawFolders.value))
const rootFolderId = computed(() => {
  return flatFolders(rawFolders.value).find(folder => folder.name === '根目录')?.id ?? null
})

watch(visible, async (opened) => {
  if (!opened) return
  await loadFolders()
  if (!isEdit.value && form.value.parent_id == null) {
    form.value.parent_id = rootFolderId.value
  }
})

async function loadFolders() {
  try {
    const res = await getCaseFolders()
    rawFolders.value = res.data || []
  } catch {
    rawFolders.value = []
  }
}

function toOptions(folders: FolderNode[]): FolderNode[] {
  return folders.map(folder => ({
    ...folder,
    label: folder.name,
    children: folder.children?.length ? toOptions(folder.children) : undefined,
  }))
}

function flatFolders(folders: FolderNode[]): FolderNode[] {
  return folders.flatMap(folder => [
    folder,
    ...flatFolders(folder.children || []),
  ])
}

function open(row?: FolderNode) {
  if (row) {
    isEdit.value = true
    editingId.value = row.id
    form.value = {
      name: row.name,
      parent_id: row.parent_id ?? null,
      sort_order: row.sort_order ?? 0,
      is_fixed: row.is_fixed ?? false,
    }
  } else {
    isEdit.value = false
    editingId.value = null
    form.value = {
      name: '',
      parent_id: rootFolderId.value,
      sort_order: 0,
      is_fixed: false,
    }
  }
  visible.value = true
}

async function submit() {
  if (form.value.is_fixed) {
    ElMessage.warning('系统目录无法编辑')
    return
  }
  if (!form.value.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }

  loading.value = true
  try {
    const data = {
      name: form.value.name.trim(),
      parent_id: form.value.parent_id ?? rootFolderId.value,
      sort_order: form.value.sort_order,
    }
    if (isEdit.value && editingId.value) {
      await updateCaseFolder(editingId.value, data)
      ElMessage.success('编辑成功')
    } else {
      await createCaseFolder(data)
      ElMessage.success('创建成功')
    }
    visible.value = false
    emit('refresh')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}

function close() {
  visible.value = false
}

function resetForm() {
  form.value = {
    name: '',
    parent_id: rootFolderId.value,
    sort_order: 0,
    is_fixed: false,
  }
  isEdit.value = false
  editingId.value = null
  loading.value = false
}

defineExpose({ open })
</script>

<style scoped>
.form-group {
  margin-bottom: 18px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  color: var(--modal-text-secondary, #888);
  font-family: var(--font-title, sans-serif);
  font-size: 13px;
  font-weight: 600;
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  background: var(--bg-secondary, #0a0a0f);
  border: 1px solid rgba(0, 255, 255, 0.22);
  border-radius: 4px;
  color: var(--text-primary, #e0e0e0);
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: var(--neon-cyan, #0ff);
  box-shadow: 0 0 0 2px rgba(0, 240, 255, 0.15);
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-input--number {
  width: 120px;
}

.folder-cascader {
  width: 100%;
}

:deep(.folder-cascader .el-input__wrapper) {
  min-height: 38px !important;
  background: var(--bg-secondary, #0a0a0f) !important;
  border: 1px solid rgba(0, 255, 255, 0.22) !important;
  border-radius: 4px !important;
  box-shadow: none !important;
}
</style>
