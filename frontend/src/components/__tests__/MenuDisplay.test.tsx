import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import MenuDisplay from '../MenuDisplay';
import { MenuData } from '../../types';

// 测试数据
const mockMenuData: MenuData = {
  date: '2024-12-15',
  meals: [
    {
      type: 'breakfast',
      time: '07:00',
      items: [
        {
          name: '小笼包',
          description: '鲜美多汁的小笼包',
          category: '点心',
          price: 8.0,
        },
        {
          name: '豆浆',
          description: '新鲜豆浆',
          category: '饮品',
        },
      ],
    },
    {
      type: 'lunch',
      time: '12:00',
      items: [
        {
          name: '红烧肉',
          description: '香甜软糯的红烧肉',
          category: '主菜',
          price: 15.0,
        },
      ],
    },
  ],
};

describe('MenuDisplay 组件', () => {
  test('应该正确渲染菜单数据', () => {
    render(
      <MenuDisplay
        menuData={mockMenuData}
        selectedDate="2024-12-15"
        loading={false}
      />
    );

    // 检查日期标题（使用更具体的选择器）
    expect(
      screen.getByRole('heading', { name: /2024年12月15日/ })
    ).toBeInTheDocument();

    // 检查餐次标题
    expect(screen.getByText('早餐')).toBeInTheDocument();
    expect(screen.getByText('午餐')).toBeInTheDocument();

    // 检查菜品名称
    expect(screen.getByText('小笼包')).toBeInTheDocument();
    expect(screen.getByText('红烧肉')).toBeInTheDocument();

    // 检查菜品描述
    expect(screen.getByText('鲜美多汁的小笼包')).toBeInTheDocument();
    expect(screen.getByText('香甜软糯的红烧肉')).toBeInTheDocument();
  });

  test('应该显示加载状态', () => {
    render(
      <MenuDisplay menuData={null} selectedDate="2024-12-15" loading={true} />
    );

    expect(screen.getByText('正在加载菜单数据...')).toBeInTheDocument();
  });

  test('应该显示无数据状态', () => {
    render(
      <MenuDisplay menuData={null} selectedDate="2024-12-15" loading={false} />
    );

    expect(screen.getByText('暂无菜单数据')).toBeInTheDocument();
    expect(screen.getByText(/暂无菜单信息/)).toBeInTheDocument();
  });

  test('应该显示今天没有菜单的特殊提示', () => {
    // 模拟今天的日期 - 使用本地时区
    const today = new Date();
    const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;

    render(
      <MenuDisplay menuData={null} selectedDate={todayStr} loading={false} />
    );

    expect(screen.getByText('今天暂无菜单')).toBeInTheDocument();
    expect(screen.getByText(/暂无菜单信息/)).toBeInTheDocument();
  });

  test('应该正确显示餐次时间', () => {
    render(
      <MenuDisplay
        menuData={mockMenuData}
        selectedDate="2024-12-15"
        loading={false}
      />
    );

    expect(screen.getByText('07:00')).toBeInTheDocument();
    expect(screen.getByText('12:00')).toBeInTheDocument();
  });

  test('应该显示菜品价格', () => {
    render(
      <MenuDisplay
        menuData={mockMenuData}
        selectedDate="2024-12-15"
        loading={false}
      />
    );

    expect(screen.getByText('¥8.00')).toBeInTheDocument();
    expect(screen.getByText('¥15.00')).toBeInTheDocument();
  });

  test('应该显示菜品分类', () => {
    render(
      <MenuDisplay
        menuData={mockMenuData}
        selectedDate="2024-12-15"
        loading={false}
      />
    );

    expect(screen.getByText('点心')).toBeInTheDocument();
    expect(screen.getByText('饮品')).toBeInTheDocument();
    expect(screen.getByText('主菜')).toBeInTheDocument();
  });

  test('应该显示统计信息', () => {
    render(
      <MenuDisplay
        menuData={mockMenuData}
        selectedDate="2024-12-15"
        loading={false}
      />
    );

    expect(screen.getByText(/共 2 个餐次/)).toBeInTheDocument();
    expect(screen.getByText(/3 道菜品/)).toBeInTheDocument();
  });

  test('应该处理空餐次数据', () => {
    const emptyMenuData: MenuData = {
      date: '2024-12-15',
      meals: [
        {
          type: 'breakfast',
          time: '07:00',
          items: [],
        },
      ],
    };

    render(
      <MenuDisplay
        menuData={emptyMenuData}
        selectedDate="2024-12-15"
        loading={false}
      />
    );

    expect(screen.getByText('暂无菜品信息')).toBeInTheDocument();
  });
});
