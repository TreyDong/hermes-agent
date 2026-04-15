---
name: css-flex-height-debug
description: 调试 CSS Grid/Flex 布局中「子元素 height:100% 不生效」—— 当父容器没有固定高度时，百分比高度会失效，导致子元素被压缩或溢出。此 skill 记录典型场景和修复模式。
version: 1.0
category: frontend-debug
---

# CSS Flex/Grid 子元素 height:100% 不生效的调试方法

## 典型症状

- 父容器用了 `display: flex` 或 `display: grid`，子元素设置 `height: 100%`
- 子元素实际表现为 0 高度，或内容被挤出视口
- 其他子元素有的正常，有的不正常（不一致的渲染）
- `min-height: 0` 加了也没用

## 根因速查路径

```
父容器有固定高度吗？
  → 有：子元素是否被 flex 收缩？ → 加 min-height: 0
  → 没有：父容器是 block 元素吗？
           → 是：父容器自身没有高度 → 需要给父容器设高度
           → 是 grid/flex：父容器高度由内容决定（align-items: start 会导致高度为 0）
           → 修复：给父容器设固定 height，或用 align-items: stretch
```

## 典型场景：Grid 两列布局右列失效

```html
<!-- 有问题的写法 -->
<div style="display: grid; grid-template-columns: 1fr 1fr; align-items: start;">
  <div class="timeline">...</div>
  <div class="scene-display" style="height: 100%;"> <!-- 失效！基准是0 -->
    <img style="height: 80%;" />
    <div class="caption">...</div>
  </div>
</div>
```

**原因**：`align-items: start` + `grid-template-columns: 1fr 1fr` = 右列高度由内容决定，而内容还没渲染时高度为 0，所以 `height: 100%` = 0。

**修复**：
```css
.scene-outer {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2.5vw;
  height: 52vh;        /* 固定高度，让子元素有基准 */
  align-items: stretch; /* 两列等高 */
}
```

## 另一场景：Flex 父容器

```css
/* 有问题 */
.parent {
  display: flex;
  align-items: flex-start; /* ← 高度由内容决定 */
}
.child {
  height: 100%; /* 失效 */
}

/* 修复 */
.parent {
  display: flex;
  align-items: stretch; /* 两列等高 */
  height: 100vh;       /* 根容器有高度 */
}
```

## 调试步骤

1. 用浏览器 DevTools 检查右列 `scene-display` 的 computed height，确认是否为 0
2. 如果是 0：父容器没有固定高度约束
3. 给父容器设 `height`（px / vh / % 相对于更高层的固定高度元素）
4. 同时确认 `align-items` 不是 `start`（会导致列高度由内容撑起而不是等高）
5. 子元素如果是 flex 容器且被收缩，加 `min-height: 0`

## 关键规则

> **`height: 100%` 的基准是「最近的具有固定高度的祖先元素」，而不是父元素本身。**

当父容器没有固定高度（`auto` / `content` / `align-items: start`），百分比就找不到有效的计算基准。
