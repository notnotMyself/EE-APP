"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";

function CloseIcon() {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 12 12"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M1 1l10 10M11 1L1 11"
        stroke="black"
        strokeWidth="1.2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function PhoneIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 20 20"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect
        x="5"
        y="2"
        width="10"
        height="16"
        rx="2"
        stroke="#90A1B9"
        strokeWidth="1.5"
      />
      <circle cx="10" cy="15" r="1" fill="#90A1B9" />
    </svg>
  );
}

function LockIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 20 20"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect
        x="4"
        y="9"
        width="12"
        height="9"
        rx="2"
        stroke="#90A1B9"
        strokeWidth="1.5"
      />
      <path
        d="M7 9V6a3 3 0 116 0v3"
        stroke="#90A1B9"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

function UserIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <circle cx="10" cy="7" r="3" stroke="#90A1B9" strokeWidth="1.5" />
      <path
        d="M4 17c0-3.314 2.686-6 6-6s6 2.686 6 6"
        stroke="#90A1B9"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

function EyeIcon({ visible }: { visible: boolean }) {
  if (visible) {
    return (
      <svg
        width="20"
        height="20"
        viewBox="0 0 20 20"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M1.5 10s3-6 8.5-6 8.5 6 8.5 6-3 6-8.5 6S1.5 10 1.5 10z"
          stroke="#90A1B9"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <circle
          cx="10"
          cy="10"
          r="2.5"
          stroke="#90A1B9"
          strokeWidth="1.5"
        />
      </svg>
    );
  }
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 20 20"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M1.5 10s3-6 8.5-6 8.5 6 8.5 6-3 6-8.5 6S1.5 10 1.5 10z"
        stroke="#90A1B9"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="10" cy="10" r="2.5" stroke="#90A1B9" strokeWidth="1.5" />
      <path
        d="M3 17L17 3"
        stroke="#90A1B9"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

function ArrowRightIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 20 20"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M4.167 10h11.666M10.833 5l5 5-5 5"
        stroke="white"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

// 前端验证，快速失败，减少无效网络请求
function validate(
  mode: "login" | "register",
  fields: {
    account: string;
    password: string;
    username: string;
    confirmPassword: string;
  }
): string | null {
  if (mode === "login") {
    if (!fields.account.trim()) return "请输入OPPO邮箱";
    if (!fields.password.trim()) return "请输入密码";
    return null;
  }
  const emailReg = /^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/;
  if (!emailReg.test(fields.account.trim())) return "请输入有效的邮箱地址";
  const uname = fields.username.trim();
  if (uname.length < 3 || uname.length > 20) return "用户名需为 3-20 个字符";
  if (!/^[a-zA-Z0-9_]+$/.test(uname)) return "用户名只能包含字母、数字和下划线";
  if (fields.password.trim().length < 8) return "密码至少需要 8 个字符";
  if (fields.password !== fields.confirmPassword) return "两次密码输入不一致";
  return null;
}

// 复用的输入框容器样式
const inputBoxStyle: React.CSSProperties = {
  width: 329.3,
  height: 55.99,
  borderRadius: 16,
  backgroundColor: "#F8FAFC",
  border: "0.62px solid #E2E8F0",
};

interface LoginModalProps {
  onClose: () => void;
}

export default function LoginModal({ onClose }: LoginModalProps) {
  const { login, register, resendConfirmation } = useAuth();

  // 登录/注册共用字段
  const [account, setAccount] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [passwordVisible, setPasswordVisible] = useState(false);

  // 注册专用字段
  const [mode, setMode] = useState<"login" | "register" | "email-sent">("login");
  const [username, setUsername] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [confirmPasswordVisible, setConfirmPasswordVisible] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [registeredEmail, setRegisteredEmail] = useState("");
  const [resendCooldown, setResendCooldown] = useState(0); // 倒计时秒数，>0 时禁用重发按钮

  const handleLogin = async () => {
    setError("");
    setSuccessMessage("");
    setIsSubmitting(true);
    try {
      await login(account, password);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRegister = async () => {
    setError("");
    const err = validate("register", { account, password, username, confirmPassword });
    if (err) { setError(err); return; }
    setIsSubmitting(true);
    try {
      await register(account, username, password);
      // 注册成功：记住邮箱，切换到邮箱验证引导页
      setRegisteredEmail(account);
      setAccount("");
      setUsername("");
      setPassword("");
      setConfirmPassword("");
      setMode("email-sent");
    } catch (err) {
      setError(err instanceof Error ? err.message : "注册失败，请重试");
    } finally {
      setIsSubmitting(false);
    }
  };

  const switchToRegister = () => {
    setMode("register");
    setError("");
    setSuccessMessage("");
  };

  const switchToLogin = () => {
    setMode("login");
    setError("");
  };

  // 重新发送确认邮件
  const handleResend = async () => {
    if (resendCooldown > 0) return;
    setError("");
    setIsSubmitting(true);
    try {
      await resendConfirmation(registeredEmail);
      // 启动 60 秒冷却，防止频繁请求
      setResendCooldown(60);
    } catch (err) {
      setError(err instanceof Error ? err.message : "发送失败，请稍后重试");
    } finally {
      setIsSubmitting(false);
    }
  };

  // 倒计时每秒递减
  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setTimeout(() => setResendCooldown((v) => v - 1), 1000);
    return () => clearTimeout(timer);
  }, [resendCooldown]);

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    /* Overlay - covers content area only (below TopBar, right of Sidebar) */
    <div
      className="absolute inset-0 top-[61px] z-50 flex items-center justify-center"
      style={{ backgroundColor: "rgba(0,0,0,0.3)" }}
      onClick={handleOverlayClick}
    >
      {/* Glass card wrapper */}
      <div className="glass-card-wrapper" style={{ width: 474 }}>
        <div
          className="glass-card-inner"
          style={{
            padding: 34,
            background: "#FFFFFF",
            backdropFilter: "none",
            WebkitBackdropFilter: "none",
          }}
        >
          {/* Content stack */}
          {mode === "email-sent" ? (
            /* ── 邮箱验证引导页 ── */
            <div className="flex flex-col items-center gap-[32px]">
              {/* Header row */}
              <div className="flex w-full items-center justify-between">
                <h2
                  className="m-0 text-[24px] font-semibold text-black"
                  style={{ fontFamily: "'OPPO Sans 4.0', sans-serif" }}
                >
                  验证您的邮箱
                </h2>
                <button
                  onClick={onClose}
                  className="flex h-[36px] w-[36px] cursor-pointer items-center justify-center rounded-full border-none"
                  style={{
                    background: "rgba(123,123,123,0.1)",
                    backdropFilter: "blur(28px)",
                    WebkitBackdropFilter: "blur(28px)",
                  }}
                >
                  <CloseIcon />
                </button>
              </div>

              {/* 邮件图标 */}
              <div
                className="flex items-center justify-center rounded-full"
                style={{
                  width: 72,
                  height: 72,
                  backgroundColor: "#F0F4FF",
                }}
              >
                <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
                  <rect x="4" y="8" width="28" height="20" rx="3" stroke="#0066FF" strokeWidth="1.8" />
                  <path d="M4 12l14 9 14-9" stroke="#0066FF" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>

              {/* 说明文字 */}
              <div className="flex flex-col items-center gap-[8px]" style={{ width: 329.3 }}>
                <p className="m-0 text-center text-[14px] text-black leading-relaxed">
                  验证邮件已发送至
                </p>
                <p
                  className="m-0 text-center text-[14px] font-semibold text-black"
                  style={{ wordBreak: "break-all" }}
                >
                  {registeredEmail}
                </p>
                <p className="m-0 text-center text-[13px] leading-relaxed" style={{ color: "rgba(0,0,0,0.54)" }}>
                  请点击邮件中的链接完成验证，验证后即可登录。如未收到，请检查垃圾邮件文件夹。
                </p>
              </div>

              {/* 错误提示 */}
              {error && (
                <p className="m-0 text-[14px] text-red-500 text-center">{error}</p>
              )}

              {/* 操作区 */}
              <div className="flex flex-col items-center gap-[12px]" style={{ width: 329.3 }}>
                {/* 重新发送按钮 */}
                <button
                  onClick={handleResend}
                  disabled={isSubmitting || resendCooldown > 0}
                  className="flex cursor-pointer items-center justify-center border-none transition-opacity hover:opacity-90 active:opacity-80 disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{
                    width: 329.3,
                    height: 55.99,
                    borderRadius: 40,
                    backgroundColor: "#000000",
                    boxShadow: "0px 6px 54px rgba(0,0,0,0.14)",
                  }}
                >
                  <span
                    className="text-[16px] font-semibold text-white"
                    style={{ fontFamily: "'Inter', sans-serif", letterSpacing: "-0.0195em" }}
                  >
                    {resendCooldown > 0
                      ? `重新发送（${resendCooldown}s）`
                      : isSubmitting ? "发送中..." : "重新发送邮件"}
                  </span>
                </button>

                {/* 返回登录 */}
                <button
                  type="button"
                  onClick={() => { setMode("login"); setError(""); setSuccessMessage("注册成功！请登录"); }}
                  className="text-[12px] bg-transparent border-none cursor-pointer p-0"
                  style={{ color: "#0066FF" }}
                >
                  返回登录
                </button>
              </div>
            </div>
          ) : (
            /* ── 登录 / 注册表单 ── */
            <div className="flex flex-col items-center gap-[42px]">
            {/* Header row */}
            <div className="flex w-full items-center justify-between">
              <h2
                className="m-0 text-[24px] font-semibold text-black"
                style={{ fontFamily: "'OPPO Sans 4.0', sans-serif" }}
              >
                {mode === "login" ? "登录" : "注册"}
              </h2>
              <button
                onClick={onClose}
                className="flex h-[36px] w-[36px] cursor-pointer items-center justify-center rounded-full border-none"
                style={{
                  background: "rgba(123,123,123,0.1)",
                  backdropFilter: "blur(28px)",
                  WebkitBackdropFilter: "blur(28px)",
                }}
              >
                <CloseIcon />
              </button>
            </div>

            {/* Input fields */}
            <div className="flex flex-col gap-[10px]" style={{ width: 329.3 }}>
              {/* 邮箱 / 账号 */}
              <div className="relative" style={inputBoxStyle}>
                <div className="pointer-events-none absolute" style={{ left: 16, top: 18 }}>
                  <PhoneIcon />
                </div>
                <input
                  type={mode === "register" ? "email" : "text"}
                  value={account}
                  onChange={(e) => setAccount(e.target.value)}
                  placeholder={mode === "register" ? "邮箱" : "OPPO邮箱"}
                  className="h-full w-full border-none bg-transparent text-[14px] text-black outline-none"
                  style={{ paddingLeft: 48, paddingRight: 16, borderRadius: 16 }}
                />
              </div>

              {/* 用户名（仅注册模式） */}
              {mode === "register" && (
                <div className="relative" style={inputBoxStyle}>
                  <div className="pointer-events-none absolute" style={{ left: 16, top: 18 }}>
                    <UserIcon />
                  </div>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="用户名（3-20 个字符，字母/数字/下划线）"
                    className="h-full w-full border-none bg-transparent text-[14px] text-black outline-none"
                    style={{ paddingLeft: 48, paddingRight: 16, borderRadius: 16 }}
                  />
                </div>
              )}

              {/* 密码 */}
              <div className="relative" style={inputBoxStyle}>
                <div className="pointer-events-none absolute" style={{ left: 16, top: 18 }}>
                  <LockIcon />
                </div>
                <input
                  type={passwordVisible ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && mode === "login") {
                      e.preventDefault();
                      handleLogin();
                    }
                  }}
                  placeholder="请输入密码"
                  className="h-full w-full border-none bg-transparent text-[14px] text-black outline-none"
                  style={{ paddingLeft: 48, paddingRight: 48, borderRadius: 16 }}
                />
                <button
                  type="button"
                  onClick={() => setPasswordVisible(!passwordVisible)}
                  className="absolute cursor-pointer border-none bg-transparent p-0"
                  style={{ right: 16, top: 18 }}
                >
                  <EyeIcon visible={passwordVisible} />
                </button>
              </div>

              {/* 确认密码（仅注册模式） */}
              {mode === "register" && (
                <div className="relative" style={inputBoxStyle}>
                  <div className="pointer-events-none absolute" style={{ left: 16, top: 18 }}>
                    <LockIcon />
                  </div>
                  <input
                    type={confirmPasswordVisible ? "text" : "password"}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        handleRegister();
                      }
                    }}
                    placeholder="确认密码"
                    className="h-full w-full border-none bg-transparent text-[14px] text-black outline-none"
                    style={{ paddingLeft: 48, paddingRight: 48, borderRadius: 16 }}
                  />
                  <button
                    type="button"
                    onClick={() => setConfirmPasswordVisible(!confirmPasswordVisible)}
                    className="absolute cursor-pointer border-none bg-transparent p-0"
                    style={{ right: 16, top: 18 }}
                  >
                    <EyeIcon visible={confirmPasswordVisible} />
                  </button>
                </div>
              )}
            </div>

            {/* 成功 / 错误消息 */}
            {successMessage && !error && (
              <p className="m-0 text-[14px] text-green-600 text-center">{successMessage}</p>
            )}
            {error && (
              <p className="m-0 text-[14px] text-red-500 text-center">{error}</p>
            )}

            {/* 提交按钮 */}
            <div className="flex flex-col items-center gap-[16px]">
              <button
                onClick={mode === "login" ? handleLogin : handleRegister}
                disabled={isSubmitting}
                className="flex cursor-pointer items-center justify-center gap-[32px] border-none transition-opacity hover:opacity-90 active:opacity-80 disabled:opacity-60 disabled:cursor-not-allowed"
                style={{
                  width: 329.3,
                  height: 55.99,
                  borderRadius: 40,
                  backgroundColor: "#000000",
                  boxShadow: "0px 6px 54px rgba(0,0,0,0.14)",
                }}
              >
                <span
                  className="text-[16px] font-semibold text-white"
                  style={{
                    fontFamily: "'Inter', sans-serif",
                    letterSpacing: "-0.0195em",
                  }}
                >
                  {isSubmitting
                    ? mode === "login" ? "登录中..." : "注册中..."
                    : mode === "login" ? "开始" : "注册"}
                </span>
                {!isSubmitting && <ArrowRightIcon />}
              </button>

              {/* 模式切换链接 */}
              <div className="flex justify-center">
                {mode === "login" ? (
                  <button
                    type="button"
                    onClick={switchToRegister}
                    className="text-[12px] bg-transparent border-none cursor-pointer p-0"
                    style={{ color: "#0066FF" }}
                  >
                    还没有账号？注册
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={switchToLogin}
                    className="text-[12px] bg-transparent border-none cursor-pointer p-0"
                    style={{ color: "#0066FF" }}
                  >
                    已有账号？登录
                  </button>
                )}
              </div>
            </div>
          </div>
          )}
        </div>
      </div>
    </div>
  );
}
