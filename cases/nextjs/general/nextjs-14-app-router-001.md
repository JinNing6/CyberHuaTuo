---
id: "nextjs-nextjs-14-app-router-001"
title: "NextJS 14 App Router 页面不刷新缓存坑"
title_en: ""
framework: "nextjs"
framework_version: ""
language: "python"
tags:
  - "general"
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

在使用 Next.js 14 的 App Router 开发网页时，发现页面数据更新后，浏览器一刷新页面内容还是旧的，数据看起来被“锁死”了，只有重启开发服务器或强制清除缓存才能看到新数据。

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

- （请补充参考链接）
