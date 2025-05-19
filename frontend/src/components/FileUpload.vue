<template>
  <div class="main-container">
    <div class="upload-sections">
      <div class="upload-section">
        <h3>词汇表上传</h3>
        <el-upload
          class="upload-demo"
          drag
          action="/api/upload"
          :on-success="(response: any, file: any) => handleWordsSuccess(response, file)"
          :on-error="handleError"
          :before-upload="beforeUpload"
          :on-remove="handleRemove"
          :data="{ type: 'vocabulary' }"
          accept=".pdf"
          :file-list="vocabFileList"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将词汇表PDF拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只能上传PDF文件
            </div>
          </template>
        </el-upload>
      </div>

      <div class="upload-section">
        <h3>中英对照上传</h3>
        <el-upload
          class="upload-demo"
          drag
          action="/api/upload"
          :on-success="(response: any, file: any) => handleTranslationsSuccess(response, file)"
          :on-error="handleError"
          :before-upload="beforeUpload"
          :on-remove="handleRemove"
          :data="{ type: 'translation' }"
          accept=".pdf"
          :file-list="transFileList"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将中英对照PDF拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只能上传PDF文件
            </div>
          </template>
        </el-upload>
      </div>
    </div>

    <div v-if="words.length > 0" class="words-block">
      <h3 class="words-title">提取的单词 (共 {{ words.length }} 个):</h3>
      <div class="words-container">
        <a
          v-for="word in words"
          :key="word"
          :href="`https://www.iciba.com/word?w=${word.replace(/\\s+/g, '+')}`"
          target="_blank"
          class="word-link"
        >
          {{ word }}
        </a>
      </div>
    </div>

    <div v-if="translations.length > 0" class="translations-list">
      <h3>中英对照 (共 {{ translations.length }} 条):</h3>
      <el-table
        :data="translations"
        class="full-table"
        border
        size="small"
        style="width: 100%;"
      >
        <el-table-column
          v-if="submitted"
          prop="en"
          label="英文"
          :min-width="120"
          :max-width="200">
          <template #default="scope">
            <span>{{ scope.row.en }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="zh"
          label="中文"
          :min-width="120"
          :max-width="200"
          show-overflow-tooltip>
          <template #default="scope">
            <span class="zh-cell">
              {{ scope.row.zh }}
            </span>
          </template>
        </el-table-column>
        <el-table-column
          prop="my_en_contents"
          label="我的译文"
          :min-width="120"
          :max-width="200">
          <template #default="scope">
            <template v-if="!submitted">
              <el-input
                v-model="scope.row.my_en_contents"
                type="textarea"
                :autosize="{ minRows: 4, maxRows: 8 }"
                placeholder="请输入英文译文"
                resize="none"
              />
            </template>
            <template v-else>
              <span>{{ scope.row.my_en_contents }}</span>
            </template>
          </template>
        </el-table-column>
        <el-table-column
          v-if="submitted"
          prop="tips"
          label="优化建议"
          :min-width="180"
          :max-width="280">
          <template #default="scope">
            <span class="tips-cell">{{ scope.row.tips }}</span>
          </template>
        </el-table-column>
      </el-table>
      <div style="display: flex; justify-content: center; margin-top: 16px;" v-if="!submitted">
        <el-button type="primary" @click="handleSubmit" :loading="loading" :disabled="loading">提交</el-button>
      </div>
      <div style="display: flex; justify-content: center; margin-top: 16px;" v-if="submitted">
        <el-button type="primary" @click="handleExport">导出</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElLoading } from 'element-plus'
import axios from 'axios'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

const words = ref<string[]>([])
const submitted = ref(false)
const translations = ref<Array<{zh: string, my_en_contents: string, en?: string, tips?: string}>>([])
const vocabFileList = ref<any[]>([])
const transFileList = ref<any[]>([])
const loading = ref(false)

// 英文校验正则，只允许英文字母、数字、空格和常用英文标点
const englishPattern = /^[A-Za-z0-9\s.,;:'"?!()\\-]*$/

function handleEnInput(val: string, row: any) {
  // 只保留英文及常用英文标点
  const filtered = val.replace(/[^A-Za-z0-9\s.,;:'"?!()\\-]/g, '')
  if (val !== filtered) {
    ElMessage.warning('英文列只允许输入英文及常用英文标点！')
    row.en = filtered
  }
}

const beforeUpload = (file: File) => {
  const isPDF = file.type === 'application/pdf'
  if (!isPDF) {
    ElMessage.error('只能上传PDF文件！')
    return false
  }
  return true
}

const handleWordsSuccess = (response: any, file: any) => {
  if (response.words) {
    words.value = response.words
    ElMessage.success('词汇表上传成功！')
    vocabFileList.value = [file]
  }
}

const handleTranslationsSuccess = (response: any, file: any) => {
  if (response.translations) {
    translations.value = response.translations.map((item: any) => ({
      en: item.en || '',   // 保留后端返回的英文内容
      zh: item.zh,
      my_en_contents: ''
    }))
    submitted.value = false
    ElMessage.success('中英对照上传成功！')
    transFileList.value = [file]
  }
}

const handleError = (error: any) => {
  console.error('Upload error:', error)
  ElMessage.error(error.response?.data?.error || '上传失败，请重试！')
}

const handleRemove = (file: any, fileList: any) => {
  words.value = []
  translations.value = []
  vocabFileList.value = []
  transFileList.value = []
}

const handleSubmit = async () => {
  const incomplete = translations.value.some(row => !row.my_en_contents || !row.my_en_contents.trim())
  if (incomplete) {
    ElMessage.warning('请填写所有英文译文后再提交！')
    return
  }
  // 显示全局 loading
  const loadingInstance = ElLoading.service({
    lock: true,
    text: '正在提交并生成优化建议，请稍候...',
    background: 'rgba(255, 255, 255, 0.7)',
    target: document.querySelector('.translations-list') as HTMLElement || undefined // 只遮罩表格区域
  })
  loading.value = true
  const payload = translations.value.map(row => ({
    en: row.en, 
    zh: row.zh,
    my_en_contents: row.my_en_contents
  }))
  try {
    const res = await axios.post('/api/submit-translation', { data: payload })
    if(res.data && Array.isArray(res.data.data)) {
      translations.value = res.data.data
      submitted.value = true
    }
    ElMessage.success('提交成功！')
  } catch (e) {
    ElMessage.error('提交失败，请重试！')
  } finally {
    loading.value = false
    loadingInstance.close()
  }
}

const handleExport = () => {
  // 构造表头
  const headers = []
  if (submitted.value) {
    headers.push('英文')
  }
  headers.push('中文', '我的译文')
  if (submitted.value) {
    headers.push('优化建议')
  }

  // 构造数据
  const data = translations.value.map(row => {
    const arr = []
    if (submitted.value) arr.push(row.en || '')
    arr.push(row.zh || '')
    arr.push(row.my_en_contents || '')
    if (submitted.value) arr.push(row.tips || '')
    return arr
  })

  // 合并表头和数据
  const wsData = [headers, ...data]
  const ws = XLSX.utils.aoa_to_sheet(wsData)

  // 1. 设置所有单元格自动换行
  const ref = ws['!ref']
  if (ref) {
    const range = XLSX.utils.decode_range(ref)
    for (let R = range.s.r; R <= range.e.r; ++R) {
      for (let C = range.s.c; C <= range.e.c; ++C) {
        const cell_address = XLSX.utils.encode_cell({ r: R, c: C })
        if (!ws[cell_address]) continue
        if (!ws[cell_address].s) ws[cell_address].s = {}
        if (!ws[cell_address].s.alignment) ws[cell_address].s.alignment = {}
        ws[cell_address].s.alignment.wrapText = true
      }
    }
  }

  // 2. 设置列宽自适应
  ws['!cols'] = wsData[0].map((col, i) => {
    // 取每列最大长度
    const maxLen = wsData.reduce((max, row) => {
      const val = row[i] ? String(row[i]) : ''
      return Math.max(max, val.length)
    }, col.length)
    // 适当加大宽度系数
    return { wch: Math.min(Math.max(maxLen * 1.2, 10), 60) }
  })

  // 导出
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Sheet1')
  const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array', cellStyles: true })
  saveAs(new Blob([wbout], { type: 'application/octet-stream' }), '回译报告.xlsx')
}
</script>

<style scoped>
body, html, #app, .app-root, .main-container {
  margin: 0 !important;
  padding: 0 !important;
  width: 100% !important;
  min-width: 0 !important;
  box-sizing: border-box;
  background: #f6f8fa;
  overflow-x: hidden;
}

.main-container {
  width: 100%;
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0;
  background: #f6f8fa;
  overflow-x: hidden;
}

.page-title {
  text-align: center;
  font-size: 2.4rem;
  color: #409EFF;
  font-weight: bold;
  margin: 32px 0 24px 0;
  letter-spacing: 2px;
}

.upload-sections {
  width: 100%;
  max-width: 1200px; /* 或你需要的宽度 */
  margin: 0 auto 32px auto;
}

.upload-section {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  /* 保证上传区域和文件列表纵向排列 */
  flex: 1 1 0;
  min-width: 320px;
  max-width: 600px;
}

.words-block {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 24px;
}

.words-title {
  color: #409EFF;
  margin-bottom: 15px;
  font-size: 1.2rem;
  text-align: center;
}

.words-container {
  margin-left: auto;
  margin-right: auto;
  justify-content: flex-start;
  display: flex;
  flex-wrap: wrap;
  gap: 12px 16px; /* 行间距12px，列间距16px */
  max-width: 900px; /* 控制每行最大宽度，900px大约能放8-10个单词 */
  margin-top: 10px;
}

.word-link {
  display: inline-block;
  min-width: 80px;
  text-align: center;
  padding: 4px 12px;
  background-color: #ecf5ff;
  color: #409EFF;
  border: 1px solid #d9ecff;
  border-radius: 4px;
  text-decoration: none;
  font-size: 15px;
  transition: all 0.3s;
  margin-bottom: 4px;
}

.word-link:hover {
  background-color: #409EFF;
  color: white;
  border-color: #409EFF;
}

h3 {
  color: #409EFF;
  margin-bottom: 15px;
}

.upload-demo {
  width: 100%;
  max-width: 100%;
}

/* 添加上传组件相关样式 */
:deep(.el-upload-list) {
  width: 100%;
  overflow: visible !important;
  margin-top: 10px;
  padding-left: 0;
}

:deep(.el-upload-list__item) {
  display: flex !important;
  align-items: center;
  max-width: 320px; /* 限制每个文件项的最大宽度，可根据实际调整 */
  min-width: 0;
}

:deep(.el-upload-list__item .el-upload-list__item-name) {
  flex: 1 1 auto;
  min-width: 0;
  max-width: 180px; /* 文件名最大宽度，超出省略 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.el-upload-list__item .el-progress) {
  max-width: 60px; /* 进度条最大宽度 */
  min-width: 40px;
  margin: 0 4px;
}

:deep(.el-upload-list__item .el-upload-list__item-delete) {
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  width: 28px;         /* 统一宽度 */
  height: 28px;        /* 统一高度 */
  color: #909399 !important;
  font-size: 18px !important;
  margin-left: 8px;
  cursor: pointer !important;
  visibility: visible !important;
  opacity: 1 !important;
  flex-shrink: 0;
  border-radius: 50%;
  transition: background 0.2s;
}
:deep(.el-upload-list__item .el-upload-list__item-delete:hover) {
  background: #f2f6fc;
  color: #f56c6c !important;
}

.translations-list {
  width: 100%;
  max-width: 900px;      /* 或1100px/1200px，根据实际需要调整 */
  margin: 32px auto 0 auto; /* 居中且顶部留白 */
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px #0001;
  padding: 24px 32px 32px 32px;
  position: relative;
  min-height: 500px;
  overflow-x: auto;
}

.full-table {
  width: 100%;
  min-width: 800px;
  max-width: 100%;      /* 不允许超出容器 */
  overflow-x: auto;
}

.el-table__body-wrapper,
.el-table__header-wrapper {
  overflow-x: auto !important;
}

.el-table {
  min-width: 800px;
  width: 100%;
  max-width: 100%;
}

.el-textarea__inner {
  font-size: 15px;
  line-height: 1.6;
  padding: 8px 10px;
  background: #f8fafc;
  border-radius: 6px;
  border: 1px solid #dcdfe6;
  transition: border-color 0.2s;
}
.el-textarea__inner:focus {
  border-color: #409EFF;
  background: #fff;
}

.el-table__cell {
  white-space: pre-line !important;
  word-break: break-all !important;
  word-wrap: break-word !important;
}

/* .relative-submit-btn {
  position: absolute;
  right: 40px;
  bottom: 32px;
  z-index: 10;
} */

.zh-cell {
  display: block;
  max-width: 600px;
  white-space: pre-line;
  word-break: break-all;
  overflow-wrap: break-word;
  /* 让内容不会超出单元格 */
}

.tips-cell {
  display: block;
  white-space: pre-line;
  word-break: break-all;
  word-wrap: break-word;
  max-width: 280px; /* 与:max-width一致 */
  overflow-wrap: break-word;
}
</style> 