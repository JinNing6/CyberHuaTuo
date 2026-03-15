---
id: "nextjs-nextjs-14-app-router-001"
title: "NextJS 14 App Router 页面不刷新缓存坑"
title_en: "Next.js 14 App Router Page Cache Not Refreshing"
framework: "nextjs"
framework_version: "14"
language: "typescript"
tags:
  - "general"
  - "cache"
  - "app-router"
severity: "medium"
complexity: "moderate"
environment:
  python_version: ">=3.9"
  os: "any"
created_at: "2026-03-12"
updated_at: "2026-03-12"
contributors:
  - github: "JinNing6"
source_url: ""
related_cases: []
---

## 🏥 症状描述
Symptom Description

在使用 Next.js 14 的 App Router 开发网页时，发现页面数据更新后，浏览器一刷新页面内容还是旧的，数据看起来被"锁死"了，只有重启开发服务器或强制清除缓存才能看到新数据。

## 🔍 错误信息
Error Message

页面无明显报错，但浏览器显示的数据始终为旧数据。开发者工具 Network 面板中可以看到请求返回了缓存命中（`x-nextjs-cache: HIT`），而非重新从数据源获取。

## 🔬 根因分析
Root Cause Analysis

Next.js 14 的 App Router 默认对页面启用**静态渲染（Static Rendering）**策略，所有 `fetch` 调用均自动附加 `cache: 'force-cache'` 行为。这意味着在构建时或首次请求时生成的页面会被缓存，后续请求直接返回缓存内容，不会重新执行服务端数据获取逻辑。

## 💊 药方
Prescriptions

### 药方 1

在 `page.tsx` 文件的最顶部添加：

```typescript
export const dynamic = 'force-dynamic'
```

这会强制 Next.js 放弃对该页面的静态预渲染缓存，每次请求都会动态在服务端进行渲染，从而保证页面数据是最新的。

## 🔗 参考资料
References

- [Next.js Route Segment Config](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config)
