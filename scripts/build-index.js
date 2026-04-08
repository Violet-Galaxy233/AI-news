// 生成 data/index.json —— 所有新闻条目的轻量元数据索引
// 用法: node scripts/build-index.js
// 每次生成新的日报后运行一次，让 TimelineViewer 能感知新数据

import { readdir, readFile, writeFile } from 'fs/promises'
import { join, basename, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const dataDir = join(__dirname, '..', 'data')
const outputFile = join(dataDir, 'index.json')

const files = (await readdir(dataDir))
  .filter(f => /^\d{4}-\d{2}-\d{2}\.json$/.test(f))
  .sort()

const index = []

for (const file of files) {
  try {
    const raw = await readFile(join(dataDir, file), 'utf-8')
    const data = JSON.parse(raw)
    const date = basename(file, '.json')
    for (const item of data.news || []) {
      index.push({
        date,
        id: item.id,
        title: item.title || '',
        keywords: item.keywords || [],
        category: item.category || '',
        importance: item.importance || 'medium',
      })
    }
  } catch (e) {
    console.warn(`跳过 ${file}: ${e.message}`)
  }
}

await writeFile(outputFile, JSON.stringify(index))
console.log(`✓ index.json 已生成：${index.length} 条新闻，来自 ${files.length} 个日期文件`)
