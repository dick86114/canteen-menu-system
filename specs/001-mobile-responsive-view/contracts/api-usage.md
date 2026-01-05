# API Contracts: 移动端响应式菜单视图与手势操作

**Feature**: 移动端响应式菜单视图与手势操作
**Date**: 2026-01-05
**Phase**: Phase 1 - Design & Contracts

## 概述

本功能**不涉及后端 API 变更**，完全复用现有 RESTful API 端点。本文档描述前端如何使用现有 API 实现移动端功能。

---

## 现有 API 端点（复用）

### 1. 获取指定日期菜单

**端点**: `GET /api/menu?date={YYYY-MM-DD}`

**用途**: 获取指定日期的菜单数据（滑动切换日期时调用）

**请求示例**:
```http
GET /api/menu?date=2026-01-05 HTTP/1.1
Host: localhost:5000
Accept: application/json
```

**响应示例**:
```json
{
  "date": "2026-01-05",
  "meals": [
    {
      "type": "breakfast",
      "time": "07:00",
      "items": [
        {
          "name": "豆浆",
          "description": "现磨豆浆",
          "category": "饮品",
          "price": 2.0,
          "order": 0,
          "category_order": 0
        }
      ]
    },
    {
      "type": "lunch",
      "time": "11:30",
      "items": [
        {
          "name": "红烧肉",
          "description": "特色档口",
          "category": "热菜",
          "price": 12.0,
          "order": 0,
          "category_order": 0
        }
      ]
    }
  ],
  "fallback": false
}
```

**使用场景**:
- 用户滑动切换日期（左滑/右滑）
- 用户点击日期选择器选择日期
- 页面初始加载

**移动端优化**:
- 使用防抖（debounce 300ms）避免快速滑动导致过多请求
- 预加载相邻日期数据（后台静默加载）
- 显示加载指示器和骨架屏

---

### 2. 获取所有可用日期

**端点**: `GET /api/dates`

**用途**: 获取所有可用日期列表（用于日期导航和边界检测）

**请求示例**:
```http
GET /api/dates HTTP/1.1
Host: localhost:5000
Accept: application/json
```

**响应示例**:
```json
{
  "dates": [
    "2026-01-04",
    "2026-01-05",
    "2026-01-06",
    "2026-01-07",
    "2026-01-08"
  ],
  "dateRange": {
    "start": "2026-01-04",
    "end": "2026-01-08"
  }
}
```

**使用场景**:
- 应用初始化时获取日期列表
- 日期选择器渲染选项
- 检测日期边界（最早/最晚日期）

**移动端优化**:
- 缓存日期列表（减少重复请求）
- 使用 useMemo 缓存计算结果

---

### 3. 健康检查

**端点**: `GET /api/health`

**用途**: 检查服务可用性（网络状态监控）

**请求示例**:
```http
GET /api/health HTTP/1.1
Host: localhost:5000
Accept: application/json
```

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-05T12:00:00Z"
}
```

**使用场景**:
- 网络状态监控（复用现有 `useNetworkStatus` Hook）
- 连接失败后重试

---

## 前端 API 服务层

### API 服务文件

**文件**: `frontend/src/services/api.ts`（现有文件，**无变更**）

现有实现已提供：
```typescript
export const api = {
  getMenuByDate: (date: string): Promise<MenuResponse> => { /* ... */ },
  getAllDates: (): Promise<DatesResponse> => { /* ... */ },
  getHealth: (): Promise<HealthResponse> => { /* ... */ }
};
```

**移动端扩展**（可选，非必需）:
如果需要添加预加载功能，可在同一文件中扩展：
```typescript
export const mobileApi = {
  // 预加载相邻日期
  preloadAdjacentDates: (
    currentDate: string,
    dates: string[]
  ): Promise<{ prev?: MenuResponse; next?: MenuResponse }> => {
    const currentIndex = dates.indexOf(currentDate);
    const promises: Promise<void>[] = [];

    const results: { prev?: MenuResponse; next?: MenuResponse } = {};

    // 预加载前一天
    if (currentIndex > 0) {
      promises.push(
        api.getMenuByDate(dates[currentIndex - 1]).then(data => {
          results.prev = data;
        })
      );
    }

    // 预加载后一天
    if (currentIndex < dates.length - 1) {
      promises.push(
        api.getMenuByDate(dates[currentIndex + 1]).then(data => {
          results.next = data;
        })
      );
    }

    return Promise.all(promises).then(() => results);
  }
};
```

---

## API 使用契约

### 日期切换契约

**前置条件**:
1. 已获取可用日期列表 (`/api/dates`)
2. 当前日期在日期列表中
3. 网络连接正常（通过 `/api/health` 检测）

**操作流程**:
1. 用户执行左滑/右滑手势
2. 手势识别触发（`useGestureSwipe` Hook）
3. 计算目标日期（当前日期 ± 1 天）
4. 检查边界（目标日期必须在 `dates` 数组中）
5. 调用 `/api/menu?date={目标日期}`
6. 更新状态并触发动画过渡

**错误处理**:
- 网络错误: 显示移动端友好错误提示，提供重试按钮
- 边界错误: 显示弹性回弹动画，不发起 API 请求
- 数据为空: 显示"今日无菜单"占位符

**性能要求**:
- API 响应时间: < 200ms (P95)
- 如果预加载命中，无需等待网络请求
- 使用防抖（debounce 300ms）避免快速滑动

---

### 模态框数据契约

**菜品详情展示** (P3 功能):

**数据来源**: 从当前加载的菜单数据中获取，**无需额外 API 调用**

**前置条件**:
1. 当前日期菜单已加载
2. 用户双击某个菜品卡片

**操作流程**:
1. 用户双击菜品（`onDoubleClick` 事件）
2. 从 `MenuResponse` 中查找对应的 `MenuItem`
3. 设置模态框状态（`modalState.isOpen = true`, `modalState.data = item`）
4. 显示模态框并触发淡入动画

**数据结构**（来自现有 API）:
```typescript
interface MenuItem {
  name: string;
  description?: string;
  category?: string;
  price?: number;
  // 移动端扩展字段（可选）
  isSpecial?: boolean;
  nutritionInfo?: { ... };
}
```

**注意**: 无需调用 API，所有数据已在前端缓存中。

---

### 快捷操作契约

**长按操作** (P3 功能):

**当前实现**: 快捷操作功能（收藏、分享、备注）为 UI 层功能，**不涉及后端 API**

**原因**: 系统当前无用户认证和个人数据存储

**未来扩展**（如果需要后端支持）:
```typescript
// 未来可能的 API 设计（不在本次实现范围）
POST /api/favorites
{
  "date": "2026-01-05",
  "mealType": "lunch",
  "itemName": "红烧肉"
}

DELETE /api/favorites/{id}
```

**当前实现**: 快捷操作仅作为 UI 交互演示，不执行实际后端操作。

---

## 错误处理契约

### API 错误码映射

| HTTP 状态码 | 场景 | 移动端处理 |
|------------|------|-----------|
| 200 | 成功 | 正常渲染数据 |
| 404 | 日期无菜单数据 | 显示"今日无菜单"占位符 |
| 500 | 服务器错误 | 显示错误提示 + 重试按钮 |
| 503 | 服务不可用 | 显示"服务暂时不可用" + 健康检查轮询 |
| 网络超时 | 请求超时 (>5s) | 显示"网络连接超时" + 重试按钮 |

### 移动端错误提示设计

**错误模态框组件** (`MobileErrorMessage.tsx`):
```typescript
interface ErrorProps {
  type: 'network' | 'server' | 'empty' | 'boundary';
  message: string;
  retryable: boolean;
  onRetry?: () => void;
}
```

**错误状态示例**:
```typescript
// 网络错误
{
  type: 'network',
  message: '网络连接失败，请检查网络设置',
  retryable: true,
  onRetry: () => reloadMenu()
}

// 服务器错误
{
  type: 'server',
  message: '服务暂时不可用，请稍后重试',
  retryable: true,
  onRetry: () => reloadMenu()
}

// 日期无菜单
{
  type: 'empty',
  message: '今日暂无菜单',
  retryable: false
}

// 到达日期边界
{
  type: 'boundary',
  message: '已是最早/最晚日期',
  retryable: false
}
```

---

## 性能优化契约

### 请求优化

**防抖（Debounce）**:
```typescript
// 快速滑动时，只发送最后一次请求
const debouncedGetMenu = debounce(
  (date: string) => api.getMenuByDate(date),
  300  // 300ms 延迟
);
```

**预加载（Preload）**:
```typescript
// 后台预加载相邻日期
useEffect(() => {
  const preload = async () => {
    if (isPreloading) return;
    setIsPreloading(true);
    await mobileApi.preloadAdjacentDates(currentDate, dates);
    setIsPreloading(false);
  };

  preload();
}, [currentDate]);
```

**缓存策略**:
```typescript
// 内存缓存菜单数据（减少重复请求）
const menuCache = new Map<string, MenuResponse>();

const getMenuWithCache = (date: string): Promise<MenuResponse> => {
  if (menuCache.has(date)) {
    return Promise.resolve(menuCache.get(date)!);
  }
  return api.getMenuByDate(date).then(data => {
    menuCache.set(date, data);
    return data;
  });
};
```

### 响应优化

**骨架屏** (Skeleton Screen):
```typescript
// 数据加载时显示占位符
{isLoading ? (
  <MenuSkeleton />  // 骨架屏组件
) : (
  <MenuDisplay meals={meals} />
)}
```

**乐观更新** (Optimistic UI):
```typescript
// 先更新 UI（显示新日期），再请求数据
const handleSwipe = (direction: 'left' | 'right') => {
  const targetDate = getTargetDate(direction);

  // 立即更新日期显示
  setCurrentDate(targetDate);

  // 后台加载数据
  api.getMenuByDate(targetDate).then(data => {
    setMeals(data.meals);
  }).catch(error => {
    // 如果失败，回滚日期
    setCurrentDate(currentDate);
    showError(error);
  });
};
```

---

## API 契约总结

### 后端 API
- ✅ **无变更** - 复用现有 `/api/menu`, `/api/dates`, `/api/health` 端点
- ✅ 现有 API 完全满足移动端需求

### 前端服务层
- ✅ 现有 `api.ts` 无需修改（基础调用）
- 🔧 可选扩展 `mobileApi` 预加载功能（性能优化）

### 错误处理
- ✅ 移动端友好错误提示
- ✅ 重试机制
- ✅ 边界反馈（弹性回弹）

### 性能优化
- ✅ 防抖/节流（避免过多请求）
- ✅ 预加载（相邻日期）
- ✅ 内存缓存（减少重复请求）
- ✅ 骨架屏（提升感知性能）
- ✅ 乐观更新（即时反馈）

**API 契约设计完成** - 可进入快速开始文档编写阶段。
