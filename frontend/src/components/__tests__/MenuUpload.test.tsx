import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import MenuUpload from '../MenuUpload';
import { NotificationProvider } from '../NotificationSystem';
import { uploadMenuFile } from '../../services/api';

// Mock API 调用
jest.mock('../../services/api', () => ({
  uploadMenuFile: jest.fn(),
  handleApiError: jest.fn().mockReturnValue('测试错误'),
  isNetworkError: jest.fn().mockReturnValue(false),
  isServerError: jest.fn().mockReturnValue(false)
}));

const mockUploadMenuFile = uploadMenuFile as jest.MockedFunction<typeof uploadMenuFile>;

// 测试包装器组件
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <NotificationProvider>
    {children}
  </NotificationProvider>
);

describe('MenuUpload 组件', () => {
  const mockOnUploadSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('应该渲染上传组件标题', () => {
    render(
      <TestWrapper>
        <MenuUpload onUploadSuccess={mockOnUploadSuccess} />
      </TestWrapper>
    );
    expect(screen.getByText('上传菜单文件')).toBeInTheDocument();
  });

  test('应该显示文件选择提示', () => {
    render(
      <TestWrapper>
        <MenuUpload onUploadSuccess={mockOnUploadSuccess} />
      </TestWrapper>
    );
    expect(screen.getByText(/点击选择或拖拽 Excel 文件到此处/)).toBeInTheDocument();
  });

  test('应该显示文件格式要求', () => {
    render(
      <TestWrapper>
        <MenuUpload onUploadSuccess={mockOnUploadSuccess} />
      </TestWrapper>
    );
    expect(screen.getByText(/支持 \.xlsx 格式，最大 10MB/)).toBeInTheDocument();
  });

  test('应该验证文件格式 - 拒绝非xlsx文件', () => {
    render(
      <TestWrapper>
        <MenuUpload onUploadSuccess={mockOnUploadSuccess} />
      </TestWrapper>
    );
    
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const invalidFile = new File(['test'], 'test.txt', { type: 'text/plain' });
    
    // 模拟文件选择
    Object.defineProperty(fileInput, 'files', {
      value: [invalidFile],
      writable: false,
    });
    
    fireEvent.change(fileInput);
    
    expect(screen.getByText(/请选择 \.xlsx 格式的 Excel 文件/)).toBeInTheDocument();
  });

  test('应该验证文件大小 - 拒绝超大文件', () => {
    render(
      <TestWrapper>
        <MenuUpload onUploadSuccess={mockOnUploadSuccess} />
      </TestWrapper>
    );
    
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    // 创建一个超过10MB的文件
    const largeFile = new File(['x'.repeat(11 * 1024 * 1024)], 'large.xlsx', { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    });
    
    Object.defineProperty(fileInput, 'files', {
      value: [largeFile],
      writable: false,
    });
    
    fireEvent.change(fileInput);
    
    expect(screen.getByText(/文件大小不能超过 10MB/)).toBeInTheDocument();
  });

  test('应该接受有效的xlsx文件', () => {
    render(
      <TestWrapper>
        <MenuUpload onUploadSuccess={mockOnUploadSuccess} />
      </TestWrapper>
    );
    
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const validFile = new File(['test'], 'menu.xlsx', { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    });
    
    Object.defineProperty(fileInput, 'files', {
      value: [validFile],
      writable: false,
    });
    
    fireEvent.change(fileInput);
    
    expect(screen.getByText(/已选择文件: menu\.xlsx/)).toBeInTheDocument();
    expect(screen.getByText(/文件 "menu\.xlsx" 已选择，可以开始上传/)).toBeInTheDocument();
    expect(screen.getByText('上传文件')).toBeInTheDocument();
  });

  test('应该处理拖拽上传', () => {
    render(
      <TestWrapper>
        <MenuUpload onUploadSuccess={mockOnUploadSuccess} />
      </TestWrapper>
    );
    
    const uploadArea = screen.getByText(/点击选择或拖拽 Excel 文件到此处/).closest('.upload-area');
    const validFile = new File(['test'], 'menu.xlsx', { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    });
    
    // 模拟拖拽事件
    fireEvent.dragOver(uploadArea!);
    expect(uploadArea).toHaveClass('dragover');
    
    fireEvent.drop(uploadArea!, {
      dataTransfer: {
        files: [validFile]
      }
    });
    
    expect(screen.getByText(/已选择文件: menu\.xlsx/)).toBeInTheDocument();
  });

  test('应该显示上传进度', async () => {
    mockUploadMenuFile.mockResolvedValue({
      status: 'success',
      message: '上传成功',
      data: [{ date: '2023-12-01', meals: [] }]
    });

    render(
      <TestWrapper>
        <MenuUpload onUploadSuccess={mockOnUploadSuccess} />
      </TestWrapper>
    );
    
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const validFile = new File(['test'], 'menu.xlsx', { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    });
    
    Object.defineProperty(fileInput, 'files', {
      value: [validFile],
      writable: false,
    });
    
    fireEvent.change(fileInput);
    
    const uploadButton = screen.getByText('上传文件');
    fireEvent.click(uploadButton);
    
    // 应该显示上传进度
    expect(screen.getByText(/正在上传文件/)).toBeInTheDocument();
    
    // 等待上传完成和回调调用
    await waitFor(() => {
      expect(screen.getByText(/文件上传成功！已解析 1 天的菜单数据/)).toBeInTheDocument();
    }, { timeout: 3000 });
    
    // 等待onUploadSuccess回调被调用
    await waitFor(() => {
      expect(mockOnUploadSuccess).toHaveBeenCalled();
    }, { timeout: 2000 });
  });

  test('应该验证空文件', () => {
    render(
      <TestWrapper>
        <MenuUpload onUploadSuccess={mockOnUploadSuccess} />
      </TestWrapper>
    );
    
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const emptyFile = new File([], 'empty.xlsx', { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    });
    
    Object.defineProperty(fileInput, 'files', {
      value: [emptyFile],
      writable: false,
    });
    
    fireEvent.change(fileInput);
    
    expect(screen.getByText('文件不能为空，请选择有效的 Excel 文件')).toBeInTheDocument();
  });

  test('应该处理上传错误', async () => {
    mockUploadMenuFile.mockRejectedValue(new Error('网络错误'));

    render(
      <TestWrapper>
        <MenuUpload onUploadSuccess={mockOnUploadSuccess} />
      </TestWrapper>
    );
    
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const validFile = new File(['test'], 'menu.xlsx', { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    });
    
    Object.defineProperty(fileInput, 'files', {
      value: [validFile],
      writable: false,
    });
    
    fireEvent.change(fileInput);
    
    const uploadButton = screen.getByText('上传文件');
    fireEvent.click(uploadButton);
    
    // 等待错误显示
    await waitFor(() => {
      expect(screen.getAllByText('测试错误')).toHaveLength(2); // 组件内部和通知系统都会显示错误
    });
    
    // 应该显示重新选择按钮
    expect(screen.getByText('重新选择')).toBeInTheDocument();
  });
});