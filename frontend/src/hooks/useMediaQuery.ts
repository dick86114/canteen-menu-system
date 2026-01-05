import { useState, useEffect } from 'react';
import type { Breakpoint } from '../types/mobile';

/**
 * 监听媒体查询变化的 Hook
 * @param query 媒体查询字符串（如 '(min-width: 768px)'）
 * @returns 是否匹配媒体查询
 *
 * @example
 * const isMobile = useMediaQuery('(max-width: 767px)')
 * const isTablet = useMediaQuery('(min-width: 768px) and (max-width: 1023px)')
 */
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      return window.matchMedia(query).matches;
    }
    return false;
  });

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    const mediaQueryList = window.matchMedia(query);
    const handleChange = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };

    // 现代浏览器使用 addEventListener
    if (mediaQueryList.addEventListener) {
      mediaQueryList.addEventListener('change', handleChange);
      return () => mediaQueryList.removeEventListener('change', handleChange);
    }
    // 旧浏览器兼容
    else if (mediaQueryList.addListener) {
      mediaQueryList.addListener(handleChange);
      return () => mediaQueryList.removeListener(handleChange);
    }
  }, [query]);

  return matches;
}

/**
 * 获取当前断点的 Hook
 * @returns 当前断点（xs, sm, md, lg, xl）
 *
 * @example
 * const breakpoint = useBreakpoint()
 * if (breakpoint === 'xs') {
 *   // 小屏手机布局
 * }
 */
export function useBreakpoint(): Breakpoint {
  const [breakpoint, setBreakpoint] = useState<Breakpoint>(() => {
    if (typeof window !== 'undefined') {
      const width = window.innerWidth;
      if (width < 375) return 'xs';
      if (width < 768) return 'sm';
      if (width < 1024) return 'md';
      if (width < 1440) return 'lg';
      return 'xl';
    }
    return 'md';
  });

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    const handleResize = () => {
      const width = window.innerWidth;
      let newBreakpoint: Breakpoint;

      if (width < 375) {
        newBreakpoint = 'xs';
      } else if (width < 768) {
        newBreakpoint = 'sm';
      } else if (width < 1024) {
        newBreakpoint = 'md';
      } else if (width < 1440) {
        newBreakpoint = 'lg';
      } else {
        newBreakpoint = 'xl';
      }

      setBreakpoint(newBreakpoint);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return breakpoint;
}

/**
 * 检查是否为移动设备（屏幕宽度 < 768px）
 * @returns 是否为移动设备
 */
export function useIsMobile(): boolean {
  return useMediaQuery('(max-width: 767px)');
}

/**
 * 检查屏幕方向
 * @returns 是否为竖屏模式
 */
export function useIsPortrait(): boolean {
  return useMediaQuery('(orientation: portrait)');
}
