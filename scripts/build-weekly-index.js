// 生成 weekly/index.json —— 周报的轻量索引
// 用法: node scripts/build-weekly-index.js

import { readdir, readFile, writeFile } from 'fs/promises'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const weeklyDir = join(__dirname, '..', 'weekly')
const outputFile = join(weeklyDir, 'index.json')

const files = (await readdir(weeklyDir))
  .filter(file => /^\d{4}-W\d{2}\.json$/.test(file))
  .sort((a, b) => b.localeCompare(a))

const index = []

for (const file of files) {
  try {
    const data = JSON.parse(await readFile(join(weeklyDir, file), 'utf-8'))
    index.push({
      week: data.week,
      title: data.title || 'AI 一周要闻',
      date_range: data.date_range || '',
      published_at: data.published_at || '',
      summary: data.summary || '',
      total_stories: (data.stories || []).length,
      critical_count: (data.stories || []).filter(item => item.importance === 'critical').length,
      paper_count: (data.papers || []).length,
    })
  } catch (error) {
    console.warn(`跳过 ${file}: ${error.message}`)
  }
}

await writeFile(outputFile, JSON.stringify(index, null, 2) + '\n')
console.log(`✓ weekly/index.json 已生成：${index.length} 期周报`)
