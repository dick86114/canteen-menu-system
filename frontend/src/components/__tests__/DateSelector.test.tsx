import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// 移除react-datepicker相关的mock，因为我们已经不使用它了

// Import DateSelector after mocking
import DateSelector from '../DateSelector';

describe('DateSelector 组件', () => {
  const mockOnDateChange = jest.fn();
  const defaultProps = {
    selectedDate: '2023-12-15',
    onDateChange: mockOnDateChange,
    availableDates: ['2023-12-14', '2023-12-15', '2023-12-16'],
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('应该正确渲染日期选择器', () => {
    render(<DateSelector {...defaultProps} />);
    
    // 检查是否显示当前日期（使用更具体的选择器）
    expect(screen.getByRole('heading', { name: /12月15日/ })).toBeInTheDocument();
    
    // 检查导航按钮
    expect(screen.getByTitle('前一天')).toBeInTheDocument();
    expect(screen.getByTitle('后一天')).toBeInTheDocument();
    expect(screen.getByTitle('今天或最近')).toBeInTheDocument();
  });

  test('应该显示正确的日期计数', () => {
    render(<DateSelector {...defaultProps} />);
    
    // 检查日期计数显示
    expect(screen.getByText(/第 2 天 \/ 共 3 天/)).toBeInTheDocument();
  });

  test('前一天按钮应该正常工作', () => {
    render(<DateSelector {...defaultProps} />);
    
    const prevButton = screen.getByTitle('前一天');
    fireEvent.click(prevButton);
    
    expect(mockOnDateChange).toHaveBeenCalledWith('2023-12-14');
  });

  test('后一天按钮应该正常工作', () => {
    render(<DateSelector {...defaultProps} />);
    
    const nextButton = screen.getByTitle('后一天');
    fireEvent.click(nextButton);
    
    expect(mockOnDateChange).toHaveBeenCalledWith('2023-12-16');
  });

  test('在第一天时前一天按钮应该被禁用', () => {
    const props = {
      ...defaultProps,
      selectedDate: '2023-12-14', // 第一天
    };
    
    render(<DateSelector {...props} />);
    
    const prevButton = screen.getByTitle('前一天');
    expect(prevButton).toBeDisabled();
  });

  test('在最后一天时后一天按钮应该被禁用', () => {
    const props = {
      ...defaultProps,
      selectedDate: '2023-12-16', // 最后一天
    };
    
    render(<DateSelector {...props} />);
    
    const nextButton = screen.getByTitle('后一天');
    expect(nextButton).toBeDisabled();
  });

  test('应该显示可用日期范围信息', () => {
    render(<DateSelector {...defaultProps} />);
    
    expect(screen.getByText(/可用日期：/)).toBeInTheDocument();
    expect(screen.getAllByText(/共 3 天/)).toHaveLength(2); // 出现在两个地方：日期计数和范围信息
  });

  test('无可用日期时应该显示提示信息', () => {
    const props = {
      ...defaultProps,
      availableDates: [],
    };
    
    render(<DateSelector {...props} />);
    
    expect(screen.getByText('请先上传菜单文件或刷新菜单数据')).toBeInTheDocument();
  });

  test('加载状态应该显示加载指示器', () => {
    const props = {
      ...defaultProps,
      loading: true,
    };
    
    render(<DateSelector {...props} />);
    
    expect(screen.getByText('正在加载日期...')).toBeInTheDocument();
    expect(screen.getByText('正在加载日期...').previousElementSibling).toHaveClass('loading-spinner');
  });

  test('月历按钮应该存在', () => {
    render(<DateSelector {...defaultProps} />);
    
    const calendarButton = screen.getByTitle('打开月历选择日期');
    expect(calendarButton).toBeInTheDocument();
    expect(calendarButton).toHaveTextContent('月历');
  });

  test('今天按钮应该导航到今天的日期', () => {
    // Mock Date.now to return a specific date
    const mockDate = new Date('2023-12-15T10:00:00Z');
    jest.spyOn(global, 'Date').mockImplementation(() => mockDate);
    
    render(<DateSelector {...defaultProps} />);
    
    const todayButton = screen.getByTitle('今天或最近');
    fireEvent.click(todayButton);
    
    expect(mockOnDateChange).toHaveBeenCalledWith('2023-12-15');
    
    // Restore Date
    jest.restoreAllMocks();
  });

  test('今天按钮应该直接跳转到今天的日期', () => {
    // 使用一个不在可用日期列表中的日期进行测试
    const props = {
      ...defaultProps,
      availableDates: ['2023-12-14', '2023-12-15', '2023-12-16'],
    };
    
    // Mock Date constructor to return a date not in available dates
    const originalDate = global.Date;
    const mockDate = new Date('2023-12-13T10:00:00Z'); // 今天是 2023-12-13
    
    // Mock Date constructor and static methods
    const mockDateConstructor = jest.fn(() => mockDate);
    (global as any).Date = mockDateConstructor;
    (global as any).Date.now = jest.fn(() => mockDate.getTime());
    
    render(<DateSelector {...props} />);
    
    const todayButton = screen.getByTitle('今天或最近');
    fireEvent.click(todayButton);
    
    // 现在应该直接跳转到今天（2023-12-13），不管是否有菜单
    expect(mockOnDateChange).toHaveBeenCalledWith('2023-12-13');
    
    // Restore Date
    (global as any).Date = originalDate;
  });
});