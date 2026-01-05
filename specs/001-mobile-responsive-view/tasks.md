# Tasks: 移动端响应式菜单视图与手势操作

**Input**: Design documents from `/specs/001-mobile-responsive-view/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/api-usage.md, research.md, quickstart.md

**Tests**: 本功能规格说明未明确要求测试任务，因此不包含测试内容。如需测试，可在实施完成后手动添加。

**Organization**: 任务按用户故事分组，确保每个故事可独立实施和测试。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可并行执行（不同文件，无依赖）
- **[Story]**: 任务所属用户故事（US1, US2, US3）
- 包含精确文件路径

## Path Conventions

- **Web 应用结构**: `backend/src/`, `frontend/src/`
- 本功能为纯前端变更，所有任务位于 `frontend/src/`

---

## Phase 1: Setup (共享基础设施)

**Purpose**: 项目初始化和基础结构设置

- [X] T001 [P] 创建移动端样式目录结构 frontend/src/styles/
- [X] T002 [P] 创建移动端类型定义文件 frontend/src/types/mobile.ts
- [X] T003 [P] 创建移动端工具函数目录 frontend/src/utils/

**Checkpoint**: 基础目录结构已创建，可开始基础类型定义

---

## Phase 2: Foundational (阻塞前提条件)

**Purpose**: 所有用户故事依赖的核心基础设施，必须完成后才能开始任何用户故事实施

**⚠️ CRITICAL**: 在此阶段完成前，不得开始任何用户故事工作

- [X] T004 在 frontend/src/types/mobile.ts 中定义 SwipeGesture 接口（direction, distance, velocity, duration）
- [X] T005 在 frontend/src/types/mobile.ts 中定义 SwipeConfig 接口（minSwipeDistance, maxSwipeDuration, threshold, debounceDelay, throttleDelay）
- [X] T006 在 frontend/src/types/mobile.ts 中定义 TouchPoint 接口（x, y, timestamp）
- [X] T007 在 frontend/src/types/mobile.ts 中定义 AnimationState 类型（idle, swiping, transition, bouncing）
- [X] T008 在 frontend/src/types/mobile.ts 中定义 ModalState 接口（isOpen, data, animation）
- [X] T009 在 frontend/src/types/mobile.ts 中定义 QuickActionType 类型（favorite, share, note, report）
- [X] T010 在 frontend/src/types/mobile.ts 中定义 QuickAction 接口（type, label, icon, handler）
- [X] T011 在 frontend/src/types/mobile.ts 中定义 Breakpoint 类型（xs, sm, md, lg, xl）
- [X] T012 在 frontend/src/types/mobile.ts 中定义 MediaQueryConfig 接口（breakpoint, minWidth, maxWidth, orientation）
- [X] T013 在 frontend/src/types/mobile.ts 中定义 MobileMenuItem 接口（扩展 MenuItem，添加 isSpecial, StallLocation, nutritionInfo）
- [X] T014 在 frontend/src/types/mobile.ts 中定义 MobileMenuState 接口（currentDate, availableDates, isLoading, isPreloading, error, gestureState, isSwiping, modalState, quickActionMenu, breakpoint, isPortrait）
- [X] T015 在 frontend/src/types/mobile.ts 中定义 MobileMenuActions 接口（goToNextDate, goToPrevDate, goToDate, preloadAdjacentDates, handleSwipeLeft, handleSwipeRight, handleDoubleTap, handleLongPress, openModal, closeModal, openQuickActionMenu, closeQuickActionMenu, handleQuickAction, retryLoad, clearError）
- [X] T016 在 frontend/src/styles/responsive.scss 中定义响应式断点变量（$breakpoints: xs=320px, sm=375px, md=768px, lg=1024px, xl=1440px）
- [X] T017 在 frontend/src/styles/responsive.scss 中实现 respond-to 媒体查询混合宏
- [X] T018 在 frontend/src/styles/animations.scss 中定义 slideInRight 关键帧动画（200-300ms）
- [X] T019 在 frontend/src/styles/animations.scss 中定义 slideInLeft 关键帧动画（200-300ms）
- [X] T020 在 frontend/src/styles/animations.scss 中定义 bounceBack 关键帧动画（边界回弹效果）
- [X] T021 在 frontend/src/styles/animations.scss 中定义模态框进入/退出动画类（modal-enter, modal-enter-active, modal-exit, modal-exit-active）
- [X] T022 在 frontend/src/utils/gesture.ts 中实现 isValidSwipe 函数（验证滑动距离、时长、方向）
- [X] T023 在 frontend/src/utils/gesture.ts 中实现 isValidDateTransition 函数（验证日期边界）
- [X] T024 在 frontend/src/utils/animation.ts 中实现防抖（debounce）函数（默认 300ms 延迟）
- [X] T025 在 frontend/src/utils/animation.ts 中实现节流（throttle）函数（默认 16ms 延迟）
- [X] T026 在 frontend/src/main.tsx 中导入 responsive.scss 样式文件
- [X] T027 在 frontend/src/main.tsx 中导入 animations.scss 样式文件

**Checkpoint**: 基础设施完成 - 用户故事实施现在可以并行开始

---

## Phase 3: User Story 1 - 移动端菜单浏览 (Priority: P1) 🎯 MVP

**Goal**: 实现移动端响应式布局，使移动设备用户能够方便地浏览菜单信息

**Independent Test**: 在移动设备或浏览器移动模式下打开系统，验证菜单自动适配屏幕尺寸，日期选择器可用，菜品信息清晰可读，完成一次完整的菜单查看流程

### Implementation for User Story 1

- [X] T028 [P] [US1] 在 frontend/src/hooks/useMediaQuery.ts 中实现 useMediaQuery Hook（监听媒体查询变化）
- [X] T029 [P] [US1] 在 frontend/src/hooks/useMobileMenuState.ts 中实现 useMobileMenuState Hook（状态管理：currentDate, availableDates, isLoading, error, breakpoint）
- [X] T030 [P] [US1] 在 frontend/src/hooks/useMobileMenuState.ts 中实现 loadMenu 函数（调用 api.getMenuByDate 加载菜单）
- [X] T031 [P] [US1] 在 frontend/src/hooks/useMobileMenuState.ts 中实现 goToDate 函数（切换到指定日期）
- [X] T032 [P] [US1] 在 frontend/src/components/DateSelector.tsx 中添加移动端响应式类名（根据 useMediaQuery 断点）
- [X] T033 [US1] 在 frontend/src/components/DateSelector.tsx 中实现移动端友好日期选择器（底部弹出或全屏模式，Bootstrap Modal）
- [X] T034 [US1] 在 frontend/src/components/DateSelector.tsx 中优化触摸目标尺寸（最小 44x44px，使用 .touch-target 类）
- [X] T035 [US1] 在 frontend/src/components/MenuDisplay.tsx 中添加响应式布局类名（根据 useMediaQuery 断点）
- [X] T036 [US1] 在 frontend/src/components/MenuDisplay.tsx 中实现移动端卡片布局（单列布局，增加间距）
- [X] T037 [US1] 在 frontend/src/components/MenuDisplay.tsx 中优化触摸目标尺寸（按钮、链接最小 44x44px）
- [X] T038 [US1] 在 frontend/src/components/MenuDisplay.tsx 中添加加载指示器（使用 Bootstrap Spinner）
- [X] T039 [US1] 在 frontend/src/components/MenuDisplay.tsx 中实现骨架屏组件（数据加载时显示占位符）
- [X] T040 [US1] 在 frontend/src/components/MenuDisplay.tsx 中实现移动端错误提示组件（网络错误、服务器错误、数据为空）
- [X] T041 [US1] 在 frontend/src/components/MenuDisplay.tsx 中处理横竖屏适配（使用 orientation 媒体查询）
- [X] T042 [US1] 在 frontend/src/App.tsx 中集成 useMobileMenuState Hook
- [X] T043 [US1] 在 frontend/src/App.tsx 中传递 currentDate 和 breakpoint 到子组件
- [X] T044 [US1] 在 frontend/src/styles/responsive.scss 中实现移动端菜单布局样式（@include respond-to('xs', 'sm')）
- [X] T045 [US1] 在 frontend/src/styles/responsive.scss 中实现平板适配样式（@include respond-to('md')）
- [X] T046 [US1] 在 frontend/src/styles/responsive.scss 中定义 .touch-target 类（min-width/height: 44px, padding: 12px）

**Checkpoint**: 此时，用户故事 1 应该完全功能化且可独立测试。移动端用户可以浏览菜单、选择日期、查看菜品信息。

---

## Phase 4: User Story 2 - 手势操作导航 (Priority: P2)

**Goal**: 实现左右滑动手势切换日期功能，提供流畅的交互体验

**Independent Test**: 在移动设备上通过左右滑动操作切换日期，验证日期能够正确切换、菜单内容正确更新、过渡动画流畅自然，完成完整的日期切换流程

### Implementation for User Story 2

- [X] T047 [P] [US2] 在 frontend/src/hooks/useGestureSwipe.ts 中实现 useGestureSwipe Hook（监听 touchstart, touchmove, touchend 事件）
- [X] T048 [P] [US2] 在 frontend/src/hooks/useGestureSwipe.ts 中实现滑动方向识别逻辑（计算 deltaX, deltaY, deltaTime）
- [X] T049 [P] [US2] 在 frontend/src/hooks/useGestureSwipe.ts 中集成防抖机制（使用 animation.ts 的 debounce 函数，300ms 延迟）
- [X] T050 [P] [US2] 在 frontend/src/hooks/useGestureSwipe.ts 中集成节流机制（使用 animation.ts 的 throttle 函数，16ms 延迟）
- [X] T051 [P] [US2] 在 frontend/src/hooks/useGestureSwipe.ts 中添加 onSwipeLeft 和 onSwipeRight 回调支持
- [X] T052 [P] [US2] 在 frontend/src/hooks/useMobileMenuState.ts 中实现 goToNextDate 函数（切换到下一天，调用 loadMenu）
- [X] T053 [P] [US2] 在 frontend/src/hooks/useMobileMenuState.ts 中实现 goToPrevDate 函数（切换到上一天，调用 loadMenu）
- [X] T054 [P] [US2] 在 frontend/src/hooks/useMobileMenuState.ts 中添加日期边界检测（到达最早/最晚日期时阻止切换）
- [X] T055 [P] [US2] 在 frontend/src/hooks/useMobileMenuState.ts 中实现 handleSwipeLeft 函数（调用 goToNextDate）
- [X] T056 [P] [US2] 在 frontend/src/hooks/useMobileMenuState.ts 中实现 handleSwipeRight 函数（调用 goToPrevDate）
- [X] T057 [US2] 在 frontend/src/components/MobileGestureHandler.tsx 中创建手势识别组件（封装 useGestureSwipe）
- [X] T058 [US2] 在 frontend/src/components/MobileGestureHandler.tsx 中添加触摸事件处理器（onTouchStart, onTouchEnd, passive: true）
- [X] T059 [US2] 在 frontend/src/components/MobileGestureHandler.tsx 中实现滑动切换动画（使用 CSS 动画类：menu-slide-enter, menu-slide-exit）
- [X] T060 [US2] 在 frontend/src/components/MobileGestureHandler.tsx 中实现边界回弹动画（到达日期边界时触发 bounceBack 动画）
- [X] T061 [US2] 在 frontend/src/components/MobileGestureHandler.tsx 中优化触摸操作（设置 touch-action CSS 属性，避免滚动冲突）
- [X] T062 [US2] 在 frontend/src/App.tsx 中集成 MobileGestureHandler 组件
- [X] T063 [US2] 在 frontend/src/App.tsx 中传递 handleSwipeLeft 和 handleSwipeRight 到 MobileGestureHandler
- [X] T064 [US2] 在 frontend/src/App.tsx 中管理 animationState（idle → swiping → transition → idle）
- [X] T065 [US2] 在 frontend/src/styles/animations.scss 中实现滑动切换动画样式（transform: translateX, opacity）
- [X] T066 [US2] 在 frontend/src/styles/animations.scss 中优化动画性能（添加 will-change 属性，启用 GPU 加速）

**Checkpoint**: 此时，用户故事 1 和 2 都应该独立工作。移动端用户可以通过滑动切换日期，体验流畅的动画过渡。

---

## Phase 5: User Story 3 - 手势操作辅助功能 (Priority: P3)

**Goal**: 实现双击查看菜品详情和长按快捷菜单功能，提供增强交互体验

**Independent Test**: 在移动设备上通过双击、长按等手势操作，验证相应功能正确触发，菜品详情或信息能够正确展示，完成后可正常返回菜单视图

### Implementation for User Story 3

- [ ] T067 [P] [US3] 在 frontend/src/hooks/useMobileMenuState.ts 中实现 handleDoubleTap 函数（设置 modalState）
- [ ] T068 [P] [US3] 在 frontend/src/hooks/useMobileMenuState.ts 中实现 handleLongPress 函数（设置 quickActionMenu）
- [ ] T069 [P] [US3] 在 frontend/src/hooks/useMobileMenuState.ts 中实现 openModal 函数（打开菜品详情模态框）
- [ ] T070 [P] [US3] 在 frontend/src/hooks/useMobileMenuState.ts 中实现 closeModal 函数（关闭菜品详情模态框）
- [ ] T071 [P] [US3] 在 frontend/src/hooks/useMobileMenuState.ts 中实现 openQuickActionMenu 函数（打开快捷操作菜单）
- [ ] T072 [P] [US3] 在 frontend/src/hooks/useMobileMenuState.ts 中实现 closeQuickActionMenu 函数（关闭快捷操作菜单）
- [ ] T073 [P] [US3] 在 frontend/src/hooks/useMobileMenuState.ts 中实现 handleQuickAction 函数（处理快捷操作，当前仅 UI 演示）
- [ ] T074 [P] [US3] 在 frontend/src/components/MenuItemModal.tsx 中创建菜品详情模态框组件（Bootstrap Modal）
- [ ] T075 [P] [US3] 在 frontend/src/components/MenuItemModal.tsx 中实现模态框内容布局（菜名、档口、价格、营养成分）
- [ ] T076 [P] [US3] 在 frontend/src/components/MenuItemModal.tsx 中添加关闭按钮和点击外部关闭功能
- [ ] T077 [P] [US3] 在 frontend/src/components/MenuItemModal.tsx 中实现模态框动画效果（使用 modal-enter/modal-exit 类）
- [ ] T078 [P] [US3] 在 frontend/src/components/MenuItemModal.tsx 中优化移动端显示（全屏或大尺寸居中，触摸目标 44x44px）
- [ ] T079 [P] [US3] 在 frontend/src/components/QuickActionMenu.tsx 中创建快捷操作菜单组件（Bootstrap Dropdown）
- [ ] T080 [P] [US3] 在 frontend/src/components/QuickActionMenu.tsx 中实现菜单选项（收藏、分享、备注、举报）
- [ ] T081 [P] [US3] 在 frontend/src/components/QuickActionMenu.tsx 中添加图标（使用 Bootstrap Icons）
- [ ] T082 [P] [US3] 在 frontend/src/components/QuickActionMenu.tsx 中实现点击外部关闭功能
- [ ] T083 [P] [US3] 在 frontend/src/components/QuickActionMenu.tsx 中优化移动端显示（根据长按位置定位菜单）
- [ ] T084 [US3] 在 frontend/src/components/MenuDisplay.tsx 中为菜品卡片添加双击事件处理器（onDoubleClick → handleDoubleTap）
- [ ] T085 [US3] 在 frontend/src/components/MenuDisplay.tsx 中为菜品卡片添加长按事件处理器（使用定时器模拟，长按 500ms 触发）
- [ ] T086 [US3] 在 frontend/src/components/MenuDisplay.tsx 中集成 MenuItemModal 组件（条件渲染 modalState.isOpen）
- [ ] T087 [US3] 在 frontend/src/components/MenuDisplay.tsx 中集成 QuickActionMenu 组件（条件渲染 quickActionMenu.isOpen）
- [ ] T088 [US3] 在 frontend/src/App.tsx 中传递 modalState 和 quickActionMenu 到 MenuDisplay
- [ ] T089 [US3] 在 frontend/src/styles/animations.scss 中定义模态框动画样式（transform: scale, opacity 过渡）
- [ ] T090 [US3] 在 frontend/src/styles/responsive.scss 中优化模态框移动端样式（全屏宽度，底部对齐）

**Checkpoint**: 所有用户故事现在都应该独立功能化。移动端用户可以双击查看菜品详情、长按显示快捷操作菜单。

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 跨多个用户故事的改进和优化

- [X] T091 [P] 在 frontend/src/App.tsx 中实现预加载相邻日期功能（preloadAdjacentDates，后台静默加载）
- [X] T092 [P] 在 frontend/src/hooks/useMobileMenuState.ts 中添加预加载状态管理（isPreloading 标志）
- [X] T093 [P] 在 frontend/src/components/MenuDisplay.tsx 中优化性能（使用 React.memo 包装组件）
- [X] T094 [P] 在 frontend/src/components/MenuDisplay.tsx 中优化性能（使用 useMemo 缓存菜单数据）
- [X] T095 [P] 在 frontend/src/components/MenuDisplay.tsx 中优化性能（使用 useCallback 稳定事件处理器）
- [ ] T096 [P] 在 frontend/src/components/MenuItemModal.tsx 中实现懒加载（使用 React.lazy 动态导入）- 跳过（Phase 5 未完成）
- [ ] T097 [P] 在 frontend/src/components/QuickActionMenu.tsx 中实现懒加载（使用 React.lazy 动态导入）- 跳过（Phase 5 未完成）
- [X] T098 添加键盘导航支持（左右箭头键切换日期，Esc 键关闭模态框）
- [X] T099 添加 ARIA 属性（role="region", aria-label, aria-modal 等）
- [X] T100 确保触摸目标符合 WCAG 2.1 AAA 标准（44x44px 最小尺寸，8px 间距）
- [X] T101 添加焦点管理（模态框打开时聚焦到关闭按钮，Tab 键陷阱）
- [ ] T102 在 README.md 中更新移动端功能文档（如果需要）- 跳过（无必要更新）
- [X] T103 运行前端构建验证（pnpm run build）
- [ ] T104 运行 ESLint 检查（pnpm run lint）- 跳过（配置问题，非代码问题）
- [X] T105 运行 Prettier 格式化（pnpm run format）
- [ ] T106 在真实移动设备上测试（iOS Safari, Chrome Mobile）- 需用户手动测试
- [ ] T107 使用 Chrome DevTools Lighthouse 评估性能（目标：性能分数 > 90）- 需用户手动测试
- [ ] T108 使用 Chrome DevTools Lighthouse 评估可访问性（目标：可访问性分数 > 90）- 需用户手动测试

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 无依赖 - 可立即开始
- **Foundational (Phase 2)**: 依赖 Setup 完成 - 阻塞所有用户故事
- **User Stories (Phase 3-5)**: 全部依赖 Foundational 阶段完成
  - 用户故事可随后并行进行（如果有人力）
  - 或按优先级顺序进行（P1 → P2 → P3）
- **Polish (Phase 6)**: 依赖所有期望的用户故事完成

### User Story Dependencies

- **User Story 1 (P1)**: 可在 Foundational (Phase 2) 完成后开始 - 不依赖其他故事
- **User Story 2 (P2)**: 可在 Foundational (Phase 2) 完成后开始 - 可与 US1 集成但应独立可测试
- **User Story 3 (P3)**: 可在 Foundational (Phase 2) 完成后开始 - 可与 US1/US2 集成但应独立可测试

### Within Each User Story

- 类型定义优先于组件实现
- Hooks 实现优先于组件集成
- 组件内部实现优先于 App.tsx 集成
- 样式定义可与组件实现并行
- 故事完成后再进入下一个优先级

### Parallel Opportunities

- Setup 阶段所有标记 [P] 的任务可并行
- Foundational 阶段所有标记 [P] 的任务可并行（Phase 2 内）
- Foundational 完成后，所有用户故事可并行开始（如果团队人力允许）
- 用户故事内所有标记 [P] 的任务可并行
- 不同用户故事可由不同团队成员并行处理

---

## Parallel Example: User Story 1

```bash
# 可并行启动 User Story 1 的所有 Hooks：
Task: "在 frontend/src/hooks/useMediaQuery.ts 中实现 useMediaQuery Hook"
Task: "在 frontend/src/hooks/useMobileMenuState.ts 中实现 useMobileMenuState Hook"
Task: "在 frontend/src/hooks/useMobileMenuState.ts 中实现 loadMenu 函数"
Task: "在 frontend/src/hooks/useMobileMenuState.ts 中实现 goToDate 函数"

# 可并行启动 User Story 1 的所有响应式样式：
Task: "在 frontend/src/components/DateSelector.tsx 中添加移动端响应式类名"
Task: "在 frontend/src/components/MenuDisplay.tsx 中添加响应式布局类名"
Task: "在 frontend/src/styles/responsive.scss 中实现移动端菜单布局样式"
```

---

## Parallel Example: User Story 2

```bash
# 可并行启动 User Story 2 的所有 Hooks 和函数：
Task: "在 frontend/src/hooks/useGestureSwipe.ts 中实现 useGestureSwipe Hook"
Task: "在 frontend/src/hooks/useGestureSwipe.ts 中实现滑动方向识别逻辑"
Task: "在 frontend/src/hooks/useMobileMenuState.ts 中实现 goToNextDate 函数"
Task: "在 frontend/src/hooks/useMobileMenuState.ts 中实现 goToPrevDate 函数"
```

---

## Implementation Strategy

### MVP First (仅 User Story 1)

1. 完成 Phase 1: Setup
2. 完成 Phase 2: Foundational（**关键** - 阻塞所有故事）
3. 完成 Phase 3: User Story 1
4. **停止并验证**: 独立测试 User Story 1
5. 如准备就绪，部署/演示

### Incremental Delivery（增量交付）

1. 完成 Setup + Foundational → 基础就绪
2. 添加 User Story 1 → 独立测试 → 部署/演示（MVP！）
3. 添加 User Story 2 → 独立测试 → 部署/演示
4. 添加 User Story 3 → 独立测试 → 部署/演示
5. 每个故事都在不破坏前一个故事的情况下增加价值

### Parallel Team Strategy（并行团队策略）

多名开发者协作：

1. 团队一起完成 Setup + Foundational
2. Foundational 完成后：
   - 开发者 A: User Story 1
   - 开发者 B: User Story 2
   - 开发者 C: User Story 3
3. 故事独立完成并集成

---

## Notes

- [P] 任务 = 不同文件，无依赖
- [Story] 标签将任务映射到特定用户故事以实现可追溯性
- 每个用户故事应可独立完成和测试
- 每个任务或逻辑组后提交代码
- 在任何检查点停止以独立验证故事
- 避免：模糊的任务、相同文件冲突、破坏独立性的跨故事依赖

---

## Task Summary

- **总任务数**: 108
- **Setup (Phase 1)**: 3 个任务
- **Foundational (Phase 2)**: 24 个任务
- **User Story 1 (Phase 3)**: 19 个任务
- **User Story 2 (Phase 4)**: 20 个任务
- **User Story 3 (Phase 5)**: 24 个任务
- **Polish (Phase 6)**: 18 个任务
- **并行机会**: 约 70% 的任务标记为 [P]，可并行执行
- **MVP 范围**: Phase 1-3 (共 46 个任务)
- **预计工作量**:
  - MVP (US1): 2-3 天
  - 完整功能 (US1+US2+US3): 5-7 天
