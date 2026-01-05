# Quickstart: 移动端响应式菜单视图与手势操作

**Feature**: 移动端响应式菜单视图与手势操作
**Date**: 2026-01-05
**Phase**: Phase 1 - Design & Contracts

## 快速开始指南

本文档提供开发、测试和部署移动端响应式菜单视图功能的快速参考。

---

## 开发环境设置

### 前置要求

- Node.js 18+ (前端开发)
- Python 3.11+ (后端服务，无变更)
- pnpm (包管理器，**必须使用**)
- 现代浏览器（Chrome DevTools 移动模拟）

### 安装步骤

```bash
# 1. 切换到前端目录
cd frontend

# 2. 安装依赖（使用 pnpm）
pnpm install

# 3. 启动开发服务器
pnpm run dev

# 4. 在浏览器中打开
# 访问 http://localhost:3000
# 使用 DevTools 切换到移动设备模拟（F12 -> Toggle device toolbar）
```

### 后端服务启动

```bash
# 1. 切换到后端目录（另一个终端）
cd backend

# 2. 激活虚拟环境（如果未创建）
python setup_venv.py

# 3. 启动后端服务
python app.py

# 4. 验证 API 可用
# 访问 http://localhost:5000/api/health
```

---

## 项目结构概览

### 新增文件清单

```
frontend/
├── src/
│   ├── components/
│   │   ├── MobileGestureHandler.tsx     # ✨ 新增：手势识别组件
│   │   ├── MenuItemModal.tsx            # ✨ 新增：菜品详情模态框
│   │   ├── QuickActionMenu.tsx          # ✨ 新增：长按快捷菜单
│   │   ├── MenuDisplay.tsx              # 🔧 修改：添加响应式样式
│   │   └── DateSelector.tsx             # 🔧 修改：移动端友好选择器
│   ├── hooks/
│   │   ├── useGestureSwipe.ts           # ✨ 新增：滑动手势 Hook
│   │   ├── useMediaQuery.ts             # ✨ 新增：媒体查询 Hook
│   │   └── useMobileMenuState.ts        # ✨ 新增：移动端状态管理 Hook
│   ├── styles/
│   │   ├── responsive.scss              # ✨ 新增：响应式样式
│   │   └── animations.scss              # ✨ 新增：动画效果
│   ├── types/
│   │   └── mobile.ts                    # ✨ 新增：移动端类型定义
│   ├── utils/
│   │   ├── gesture.ts                   # ✨ 新增：手势工具函数
│   │   └── animation.ts                 # ✨ 新增：动画工具函数
│   ├── App.tsx                          # 🔧 修改：集成手势处理
│   └── main.tsx                         # 🔧 修改：导入样式
└── tests/                               # 📝 新增：集成测试

backend/                                   # 无变更
```

---

## 开发工作流

### 1. 创建功能分支

```bash
# 确保在 main 分支
git checkout main

# 拉取最新代码
git pull origin main

# 创建功能分支（已自动创建）
git checkout 001-mobile-responsive-view
```

### 2. 实现优先级

按照用户故事优先级逐步实现：

#### Phase 1: P1 - 移动端菜单浏览（MVP）

**目标**: 实现基础响应式布局

**任务清单**:
- [ ] 创建 `responsive.scss`，定义断点和移动端样式
- [ ] 修改 `MenuDisplay.tsx`，添加响应式类名
- [ ] 修改 `DateSelector.tsx`，实现移动端友好选择器
- [ ] 创建 `useMediaQuery.ts` Hook
- [ ] 测试不同屏幕尺寸（320px, 375px, 768px, 1024px）

**验收标准**:
- ✅ 移动端布局自动适配
- ✅ 触摸目标 ≥ 44x44px
- ✅ 菜单信息完整显示
- ✅ 日期选择器移动端友好

#### Phase 2: P2 - 手势操作导航

**目标**: 实现滑动切换日期

**任务清单**:
- [ ] 创建 `useGestureSwipe.ts` Hook
- [ ] 创建 `MobileGestureHandler.tsx` 组件
- [ ] 创建 `gesture.ts` 工具函数
- [ ] 集成到 `App.tsx`
- [ ] 添加滑动动画（`animations.scss`）
- [ ] 实现防抖/节流机制
- [ ] 处理边界情况（弹性回弹）

**验收标准**:
- ✅ 左滑切换到下一天
- ✅ 右滑切换到上一天
- ✅ 动画流畅（60fps）
- ✅ 边界反馈正确

#### Phase 3: P3 - 手势操作辅助功能

**目标**: 实现双击和长按功能

**任务清单**:
- [ ] 创建 `MenuItemModal.tsx` 组件（菜品详情）
- [ ] 创建 `QuickActionMenu.tsx` 组件（快捷菜单）
- [ ] 添加双击和长按事件处理
- [ ] 实现模态框动画效果

**验收标准**:
- ✅ 双击显示菜品详情
- ✅ 长按显示快捷菜单
- ✅ 模态框动画流畅

---

## 核心组件使用示例

### 1. 响应式布局 Hook

```typescript
// hooks/useMediaQuery.ts
import { useState, useEffect } from 'react';

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    setMatches(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setMatches(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [query]);

  return matches;
}

// 使用示例
function MenuDisplay() {
  const isMobile = useMediaQuery('(max-width: 768px)');

  return (
    <div className={isMobile ? 'menu-mobile' : 'menu-desktop'}>
      {/* 响应式内容 */}
    </div>
  );
}
```

### 2. 手势识别 Hook

```typescript
// hooks/useGestureSwipe.ts
import { useState, useRef, TouchEvent } from 'react';

interface SwipeConfig {
  minSwipeDistance?: number;
  maxSwipeDuration?: number;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
}

export function useGestureSwipe(config: SwipeConfig) {
  const [isSwiping, setIsSwiping] = useState(false);
  const touchStart = useRef<{ x: number; y: number; time: number } | null>(null);

  const onTouchStart = (e: TouchEvent) => {
    const touch = e.touches[0];
    touchStart.current = {
      x: touch.clientX,
      y: touch.clientY,
      time: Date.now()
    };
  };

  const onTouchEnd = (e: TouchEvent) => {
    if (!touchStart.current) return;

    const touch = e.changedTouches[0];
    const deltaX = touch.clientX - touchStart.current.x;
    const deltaY = touch.clientY - touchStart.current.y;
    const deltaTime = Date.now() - touchStart.current.time;

    const {
      minSwipeDistance = 50,
      maxSwipeDuration = 500,
      onSwipeLeft,
      onSwipeRight
    } = config;

    // 检测水平滑动
    if (
      Math.abs(deltaX) > minSwipeDistance &&
      Math.abs(deltaY) < Math.abs(deltaX) &&  // 水平滑动
      deltaTime < maxSwipeDuration
    ) {
      if (deltaX > 0 && onSwipeRight) {
        onSwipeRight();
      } else if (deltaX < 0 && onSwipeLeft) {
        onSwipeLeft();
      }
    }

    touchStart.current = null;
  };

  return {
    isSwiping,
    onTouchStart,
    onTouchEnd
  };
}

// 使用示例
function App() {
  const { onTouchStart, onTouchEnd } = useGestureSwipe({
    onSwipeLeft: () => goToNextDate(),
    onSwipeRight: () => goToPrevDate()
  });

  return (
    <div onTouchStart={onTouchStart} onTouchEnd={onTouchEnd}>
      {/* 菜单内容 */}
    </div>
  );
}
```

### 3. 移动端状态管理

```typescript
// hooks/useMobileMenuState.ts
import { useState, useCallback } from 'react';
import { api } from '../services/api';

export function useMobileMenuState() {
  const [currentDate, setCurrentDate] = useState<string>('');
  const [meals, setMeals] = useState<Meal[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadMenu = useCallback(async (date: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.getMenuByDate(date);
      setMeals(response.meals);
      setCurrentDate(date);
    } catch (err) {
      setError('加载失败，请重试');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const goToNextDate = useCallback(() => {
    // 实现切换到下一天
  }, [currentDate]);

  const goToPrevDate = useCallback(() => {
    // 实现切换到上一天
  }, [currentDate]);

  return {
    currentDate,
    meals,
    isLoading,
    error,
    loadMenu,
    goToNextDate,
    goToPrevDate
  };
}
```

---

## 样式开发指南

### 响应式断点定义

```scss
// styles/responsive.scss
$breakpoints: (
  'xs': 320px,   // 小屏手机
  'sm': 375px,   // 中大屏手机
  'md': 768px,   // 平板
  'lg': 1024px,  // 桌面
  'xl': 1440px   // 大屏桌面
);

// 媒体查询混合宏
@mixin respond-to($breakpoint) {
  @if map-has-key($breakpoints, $breakpoint) {
    @media (min-width: map-get($breakpoints, $breakpoint)) {
      @content;
    }
  }
}

// 使用示例
.menu-container {
  padding: 16px;

  // 移动端（默认）
  font-size: 14px;

  // 平板及以上
  @include respond-to('md') {
    padding: 24px;
    font-size: 16px;
  }
}
```

### 触摸目标优化

```scss
// 确保触摸目标 ≥ 44x44px
.touch-target {
  min-width: 44px;
  min-height: 44px;
  padding: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
```

### 动画效果

```scss
// styles/animations.scss
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideInLeft {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

// 使用示例
.menu-slide-enter {
  animation: slideInRight 250ms ease-out;
}

.menu-slide-exit {
  animation: slideInLeft 250ms ease-out;
}
```

---

## 测试指南

### 单元测试

```typescript
// components/__tests__/useGestureSwipe.test.ts
import { renderHook, act } from '@testing-library/react';
import { useGestureSwipe } from '../useGestureSwipe';

describe('useGestureSwipe', () => {
  it('should detect left swipe', () => {
    const onSwipeLeft = jest.fn();
    const { result } = renderHook(() =>
      useGestureSwipe({ onSwipeLeft })
    );

    // 模拟左滑触摸事件
    act(() => {
      result.current.onTouchStart({
        touches: [{ clientX: 100, clientY: 50 }]
      } as any);

      result.current.onTouchEnd({
        changedTouches: [{ clientX: 20, clientY: 50 }]
      } as any);
    });

    expect(onSwipeLeft).toHaveBeenCalled();
  });
});
```

### 集成测试

```typescript
// tests/mobile-menu.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import App from '../src/App';

describe('Mobile Menu', () => {
  it('should display menu on mobile devices', () => {
    // 模拟移动设备视口
    window.innerWidth = 375;
    window.dispatchEvent(new Event('resize'));

    render(<App />);

    // 验证响应式布局
    expect(screen.getByTestId('mobile-menu')).toBeInTheDocument();
  });

  it('should handle swipe gestures', async () => {
    render(<App />);

    const menuContainer = screen.getByTestId('menu-container');

    // 模拟左滑手势
    fireEvent.touchStart(menuContainer, {
      touches: [{ clientX: 100, clientY: 50 }]
    });

    fireEvent.touchEnd(menuContainer, {
      changedTouches: [{ clientX: 20, clientY: 50 }]
    });

    // 验证日期切换
    await waitFor(() => {
      expect(screen.getByText('下一天菜单')).toBeInTheDocument();
    });
  });
});
```

### 手动测试

**测试设备**:
- 真实移动设备（iOS Safari, Chrome Mobile）
- 浏览器 DevTools 移动模拟（F12 -> Toggle device toolbar）

**测试清单**:
- [ ] 布局适配（320px, 375px, 768px）
- [ ] 触摸目标尺寸（≥44x44px）
- [ ] 滑动切换日期（左滑/右滑）
- [ ] 动画流畅度（60fps）
- [ ] 边界反馈（弹性回弹）
- [ ] 网络错误处理
- [ ] 键盘导航（可访问性）

---

## 性能优化清单

### 性能指标

- [ ] 手势响应时间 < 100ms
- [ ] FCP < 3s (4G 网络)
- [ ] 动画帧率 60fps
- [ ] Lighthouse 分数 > 90

### 优化措施

- [ ] 使用 `React.memo` 包装纯组件
- [ ] 使用 `useMemo` 缓存计算结果
- [ ] 使用 `useCallback` 稳定函数引用
- [ ] 实现防抖/节流（避免过多请求）
- [ ] 实现预加载（相邻日期）
- [ ] 使用骨架屏（提升感知性能）
- [ ] 懒加载模态框组件（`React.lazy`）

---

## 部署指南

### 生产构建

```bash
# 1. 构建前端
cd frontend
pnpm run build

# 2. 验证构建输出
ls -lh dist/
# 应该看到 index.html, assets/*.js, assets/*.css

# 3. 复制到后端静态目录
# （现有构建流程自动处理）
# dist/ -> backend/static/

# 4. 重新构建 Docker 镜像
cd ..
docker build -t canteen-menu-system:mobile-support .

# 5. 运行容器
docker run -d -p 1214:5000 -v $(pwd)/menu:/app/menu canteen-menu-system:mobile-support
```

### 环境变量

**无需新增环境变量** - 复用现有配置：
```bash
FLASK_ENV=production
TZ=Asia/Shanghai
```

### 验证部署

```bash
# 1. 检查容器健康状态
docker ps

# 2. 检查健康端点
curl http://localhost:1214/api/health

# 3. 使用移动设备访问
# http://localhost:1214
# 验证响应式布局和手势功能
```

---

## 故障排查

### 常见问题

**Q: 手势不响应？**
- 检查 `touch-action` CSS 属性是否冲突
- 使用 `console.log` 调试触摸事件
- 验证 `passive: true` 事件监听器

**Q: 动画卡顿？**
- 使用 Chrome DevTools Performance 分析
- 检查是否触发布局重排
- 使用 `will-change` 优化动画元素

**Q: 日期切换不生效？**
- 检查 API 响应数据格式
- 验证防抖/节流配置
- 查看浏览器控制台错误日志

**Q: 触摸目标太小？**
- 使用 Chrome DevTools 检查元素尺寸
- 调整 `padding` 确保达到 44x44px
- 测试不同设备尺寸

---

## 下一步

### 完成开发后

1. **代码审查**: 提交 PR 进行代码审查
2. **测试验证**: 在真实移动设备上测试
3. **性能优化**: 使用 Lighthouse 评估性能
4. **文档更新**: 更新 README 和用户文档

### 扩展功能（未来）

- [ ] PWA 支持（离线访问）
- [ ] 手势教程（首次使用引导）
- [ ] 用户偏好记忆（最后查看日期）
- [ ] 无障碍增强（语音导航）

---

**快速开始文档完成** - 开发者可按此指南开始实施功能。
