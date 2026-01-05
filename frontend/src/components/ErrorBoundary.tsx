import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    // 更新 state 使下一次渲染能够显示降级后的 UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // 记录错误信息
    console.error('ErrorBoundary 捕获到错误:', error, errorInfo);

    this.setState({
      error,
      errorInfo,
    });

    // 这里可以将错误信息发送到错误报告服务
    // reportErrorToService(error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      // 如果提供了自定义的 fallback UI，使用它
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // 默认的错误 UI
      return (
        <div className="error-boundary">
          <div className="container py-5">
            <div className="row justify-content-center">
              <div className="col-md-8 col-lg-6">
                <div className="card border-danger">
                  <div className="card-header bg-danger text-white">
                    <h5 className="card-title mb-0">
                      <i className="bi bi-exclamation-triangle me-2"></i>
                      应用程序错误
                    </h5>
                  </div>
                  <div className="card-body">
                    <div className="text-center mb-4">
                      <i className="bi bi-bug display-1 text-danger"></i>
                    </div>

                    <h6 className="text-danger mb-3">
                      很抱歉，应用程序遇到了意外错误
                    </h6>

                    <p className="text-muted mb-4">
                      我们已经记录了这个错误，开发团队会尽快修复。
                      您可以尝试刷新页面或稍后再试。
                    </p>

                    {/* 开发环境下显示详细错误信息 */}
                    {process.env.NODE_ENV === 'development' &&
                      this.state.error && (
                        <details className="mb-4">
                          <summary className="btn btn-outline-secondary btn-sm mb-2">
                            查看技术详情
                          </summary>
                          <div className="alert alert-secondary">
                            <h6>错误信息:</h6>
                            <pre className="small text-danger mb-2">
                              {this.state.error.toString()}
                            </pre>

                            {this.state.errorInfo && (
                              <>
                                <h6>组件堆栈:</h6>
                                <pre className="small text-muted">
                                  {this.state.errorInfo.componentStack}
                                </pre>
                              </>
                            )}
                          </div>
                        </details>
                      )}

                    <div className="d-flex gap-2 justify-content-center">
                      <button
                        className="btn btn-primary"
                        onClick={this.handleRetry}
                      >
                        <i className="bi bi-arrow-clockwise me-2"></i>
                        重试
                      </button>

                      <button
                        className="btn btn-outline-secondary"
                        onClick={() => window.location.reload()}
                      >
                        <i className="bi bi-arrow-repeat me-2"></i>
                        刷新页面
                      </button>
                    </div>
                  </div>

                  <div className="card-footer text-muted text-center">
                    <small>如果问题持续存在，请联系技术支持</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
