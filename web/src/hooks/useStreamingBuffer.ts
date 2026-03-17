"use client";

import { useRef, useCallback } from "react";

// ─── useStreamingBuffer ──────────────────────────────────────────────────────
// 单层网络缓冲（移除了 Level 2 typeTimer）。
// 字符动画完全交由 streamdown 的 animated + isAnimating 处理，
// 避免两层动画叠加产生的重复效果。
//
// Level 1：网络 chunk 直接通过 setContentFn 更新 React state，
//          可选 50ms 批量 flush 以减少 re-render 次数。

export function useStreamingBuffer() {
  const networkBuffer = useRef("");
  const setContentFn = useRef<((s: string) => void) | null>(null);

  const pushChunk = useCallback((chunk: string) => {
    networkBuffer.current += chunk;
    setContentFn.current?.(networkBuffer.current);
  }, []);

  const finish = useCallback(() => {
    setContentFn.current?.(networkBuffer.current);
  }, []);

  const reset = useCallback(() => {
    networkBuffer.current = "";
  }, []);

  const bindSetter = useCallback((fn: (s: string) => void) => {
    setContentFn.current = fn;
  }, []);

  // 暴露 networkBuffer 供 onDone 读取最终内容
  return { pushChunk, finish, reset, bindSetter, networkBuffer };
}
