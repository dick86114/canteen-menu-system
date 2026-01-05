import { render, screen, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../../App';

// Mock API 调用
jest.mock('../../services/api', () => ({
  getAvailableDates: jest.fn().mockResolvedValue({ dates: [] }),
  getMenuByDate: jest.fn().mockResolvedValue({ date: '', meals: [] }),

  handleApiError: jest.fn().mockReturnValue('测试错误'),
}));

describe('App 组件', () => {
  test('应该渲染导航栏中的应用标题', async () => {
    await act(async () => {
      render(<App />);
    });
    expect(screen.getByRole('navigation')).toBeInTheDocument();
    expect(screen.getAllByText('食堂菜单系统')).toHaveLength(2); // 导航栏和页脚各一个
  });

  test('应该显示无数据提示', async () => {
    await act(async () => {
      render(<App />);
    });
    expect(screen.getByText('暂无菜单数据')).toBeInTheDocument();
    expect(
      screen.getByText('系统中暂时没有菜单信息，请联系管理员添加菜单数据')
    ).toBeInTheDocument();
  });

  test('应该包含导航栏', async () => {
    await act(async () => {
      render(<App />);
    });
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });
});
