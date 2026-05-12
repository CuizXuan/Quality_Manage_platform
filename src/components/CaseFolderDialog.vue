<template>
  <el-dialog v-model="visible" :title="isEdit ? '编辑分类' : '新增分类'" width="400px" destroy-on-close>
    <el-form :model="form" label-width="80px">
      <el-form-item label="分类名称" required>
        <el-input v-model="form.name" placeholder="请输入分类名称" maxlength="200" show-word-limit />
      </el-form-item>
      <el-form-item label="排序">
        <el-input-number v-model="form.sort_order" :min="0" :max="9999" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit" :loading="loading">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { createCaseFolder, updateCaseFolder } from '@/api/caseFolders'
import { ElMessage } from 'element-plus'

const visible = ref(false)
const isEdit = ref(false)
const editingId = ref<number | null>(null)
const loading = ref(false)
const form = ref({ name: '', sort_order: 0 })

function open(row?: any) {
  if (row) {
    isEdit.value = true
    editingId.value = row.id
    form.value = { name: row.name, sort_order: row.sort_order ?? 0 }
  } else {
    isEdit.value = false
    editingId.value = null
    form.value = { name: '', sort_order: 0 }
  }
  visible.value = true
}

async function submit() {
  if (!form.value.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  loading.value = true
  try {
    if (isEdit.value && editingId.value) {
      await updateCaseFolder(editingId.value, form.value)
      ElMessage.success('编辑成功')
    } else {
      await createCaseFolder(form.value)
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

const emit = defineEmits<{
  (e: 'refresh'): void
}>()
defineExpose({ open })
</script>