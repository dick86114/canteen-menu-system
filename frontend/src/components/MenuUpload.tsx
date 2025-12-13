import React, { useState, useRef } from 'react';
import { uploadMenuFile, handleApiError, isNetworkError, isServerError } from '../services/api';
import { useNotifications } from './NotificationSystem';
import { UploadStatus } from '../types';

interface MenuUploadProps {
  onUploadSuccess: () => void;
}

const MenuUpload: React.FC<MenuUploadProps> = ({ onUploadSuccess }) => {
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [dragOver, setDragOver] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // 使用通知系统
  const { showError, showSuccess } = useNotifications();

  // 文件验证
  const validateFile = (file: File): boolean => {
    // 检查文件类型 - 更严格的验证
    const validExtensions = ['.xlsx'];
    const fileName = file.name.toLowerCase();
    const isValidExtension = validExtensions.some(ext => fileName.endsWith(ext));
    
    if (!isValidExtension) {
      setErrorMessage('请选择 .xlsx 格式的 Excel 文件。不支持 .xls 或其他格式。');
      return false;
    }

    // 检查 MIME 类型
    const validMimeTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/octet-stream' // 某些浏览器可能返回这个
    ];
    
    if (file.type && !validMimeTypes.includes(file.type)) {
      setErrorMessage('文件类型不正确，请选择有效的 Excel 文件');
      return false;
    }

    // 检查文件大小 (10MB 限制)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      setErrorMessage(`文件大小不能超过 10MB，当前文件大小：${(file.size / 1024 / 1024).toFixed(2)}MB`);
      return false;
    }

    // 检查文件是否为空
    if (file.size === 0) {
      setErrorMessage('文件不能为空，请选择有效的 Excel 文件');
      return false;
    }

    return true;
  };

  // 处理文件选择
  const handleFileSelect = (file: File) => {
    setErrorMessage('');
    setSuccessMessage('');
    
    if (validateFile(file)) {
      setSelectedFile(file);
      setSuccessMessage(`文件 "${file.name}" 已选择，可以开始上传`);
    }
  };

  // 处理文件上传
  const uploadFile = async () => {
    if (!selectedFile) return;

    // 再次验证文件（防止状态不一致）
    if (!validateFile(selectedFile)) {
      return;
    }

    setUploadStatus('uploading');
    setUploadProgress(0);
    setErrorMessage('');
    setSuccessMessage('');

    try {
      const response = await uploadMenuFile(selectedFile, (progress) => {
        // 使用真实的上传进度
        setUploadProgress(progress);
      });

      if (response.status === 'success') {
        setUploadStatus('success');
        const successMsg = `文件上传成功！已解析 ${response.data?.length || 0} 天的菜单数据`;
        setSuccessMessage(successMsg);
        showSuccess('上传成功', successMsg);
        
        // 显示成功消息更长时间，让用户看到反馈
        setTimeout(() => {
          onUploadSuccess();
          resetUpload();
        }, 1500);
      } else {
        setUploadStatus('error');
        const errorMsg = response.message || '上传失败，请重试';
        setErrorMessage(errorMsg);
        showError('上传失败', errorMsg);
      }
    } catch (error) {
      setUploadStatus('error');
      const errorMsg = handleApiError(error);
      setErrorMessage(errorMsg);
      
      // 根据错误类型显示不同的通知
      if (isNetworkError(error)) {
        showError('网络连接失败', '请检查网络连接后重试', true);
      } else if (isServerError(error)) {
        showError('服务器错误', '服务器暂时不可用，请稍后重试', true);
      } else {
        showError('上传失败', errorMsg);
      }
      
      // 清除进度条
      setUploadProgress(0);
    }
  };

  // 重置上传状态
  const resetUpload = () => {
    setSelectedFile(null);
    setUploadStatus('idle');
    setUploadProgress(0);
    setErrorMessage('');
    setSuccessMessage('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // 拖拽处理
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  // 点击选择文件
  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  return (
    <div className="card mb-4">
      <div className="card-header">
        <h5 className="card-title mb-0">
          <i className="bi bi-cloud-upload me-2"></i>
          上传菜单文件
        </h5>
      </div>
      <div className="card-body">
        {/* 文件上传区域 */}
        <div
          className={`upload-area ${dragOver ? 'dragover' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleClick}
          style={{ cursor: 'pointer' }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx"
            onChange={handleFileInputChange}
            style={{ display: 'none' }}
          />
          
          {uploadStatus === 'idle' && !selectedFile && (
            <div>
              <i className="bi bi-file-earmark-excel display-4 text-muted mb-3"></i>
              <p className="mb-2">点击选择或拖拽 Excel 文件到此处</p>
              <small className="text-muted">支持 .xlsx 格式，最大 10MB</small>
            </div>
          )}

          {selectedFile && uploadStatus === 'idle' && (
            <div>
              <i className="bi bi-file-earmark-excel display-4 text-success mb-3"></i>
              <p className="mb-2">已选择文件: {selectedFile.name}</p>
              <small className="text-muted">
                文件大小: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </small>
            </div>
          )}

          {uploadStatus === 'uploading' && (
            <div>
              <div className="loading-spinner mb-3"></div>
              <p className="mb-2">
                {uploadProgress < 50 ? '正在上传文件...' : 
                 uploadProgress < 85 ? '正在处理文件...' : 
                 '正在解析菜单数据...'}
              </p>
              <div className="progress" style={{ width: '250px', margin: '0 auto' }}>
                <div
                  className="progress-bar progress-bar-striped progress-bar-animated"
                  role="progressbar"
                  style={{ width: `${uploadProgress}%` }}
                  aria-valuenow={uploadProgress}
                  aria-valuemin={0}
                  aria-valuemax={100}
                >
                  {Math.round(uploadProgress)}%
                </div>
              </div>
              <small className="text-muted mt-2 d-block">
                文件: {selectedFile?.name}
              </small>
            </div>
          )}

          {uploadStatus === 'success' && (
            <div>
              <i className="bi bi-check-circle display-4 text-success mb-3"></i>
              <p className="text-success mb-0">
                {successMessage || '文件上传成功！'}
              </p>
            </div>
          )}
        </div>

        {/* 错误信息 */}
        {errorMessage && (
          <div className="alert alert-danger mt-3" role="alert">
            <i className="bi bi-exclamation-triangle me-2"></i>
            {errorMessage}
          </div>
        )}

        {/* 成功信息 */}
        {successMessage && uploadStatus !== 'success' && (
          <div className="alert alert-success mt-3" role="alert">
            <i className="bi bi-check-circle me-2"></i>
            {successMessage}
          </div>
        )}

        {/* 操作按钮 */}
        <div className="mt-3 d-flex gap-2 justify-content-center">
          {selectedFile && uploadStatus === 'idle' && (
            <>
              <button
                className="btn btn-primary"
                onClick={uploadFile}
                disabled={uploadStatus !== 'idle'}
              >
                <i className="bi bi-upload me-2"></i>
                上传文件
              </button>
              <button
                className="btn btn-outline-secondary"
                onClick={resetUpload}
              >
                <i className="bi bi-x-circle me-2"></i>
                取消
              </button>
            </>
          )}

          {uploadStatus === 'error' && (
            <button
              className="btn btn-outline-primary"
              onClick={resetUpload}
            >
              <i className="bi bi-arrow-clockwise me-2"></i>
              重新选择
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default MenuUpload;