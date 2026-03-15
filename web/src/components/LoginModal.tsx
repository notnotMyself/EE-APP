"use client";

import { useState } from "react";
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

interface LoginModalProps {
  onClose: () => void;
}

export default function LoginModal({ onClose }: LoginModalProps) {
  const { login } = useAuth();
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [account, setAccount] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleStart = async () => {
    setError("");
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
        <div className="glass-card-inner" style={{ padding: 34 }}>
          {/* Content stack */}
          <div className="flex flex-col items-center gap-[42px]">
            {/* Header row */}
            <div className="flex w-full items-center justify-between">
              <h2
                className="m-0 text-[24px] font-semibold text-black"
                style={{ fontFamily: "'OPPO Sans 4.0', sans-serif" }}
              >
                登录
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
              {/* Account input */}
              <div
                className="relative"
                style={{
                  width: 329.3,
                  height: 55.99,
                  borderRadius: 16,
                  backgroundColor: "#F8FAFC",
                  border: "0.62px solid #E2E8F0",
                }}
              >
                <div
                  className="pointer-events-none absolute"
                  style={{ left: 16, top: 18 }}
                >
                  <PhoneIcon />
                </div>
                <input
                  type="text"
                  value={account}
                  onChange={(e) => setAccount(e.target.value)}
                  placeholder="账号"
                  className="h-full w-full border-none bg-transparent text-[14px] text-black outline-none"
                  style={{
                    paddingLeft: 48,
                    paddingRight: 16,
                    borderRadius: 16,
                  }}
                />
              </div>

              {/* Password input */}
              <div
                className="relative"
                style={{
                  width: 329.3,
                  height: 55.99,
                  borderRadius: 16,
                  backgroundColor: "#F8FAFC",
                  border: "0.62px solid #E2E8F0",
                }}
              >
                <div
                  className="pointer-events-none absolute"
                  style={{ left: 16, top: 18 }}
                >
                  <LockIcon />
                </div>
                <input
                  type={passwordVisible ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleStart();
                    }
                  }}
                  placeholder="请输入密码"
                  className="h-full w-full border-none bg-transparent text-[14px] text-black outline-none"
                  style={{
                    paddingLeft: 48,
                    paddingRight: 48,
                    borderRadius: 16,
                  }}
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
            </div>

            {/* Error message */}
            {error && (
              <p className="m-0 text-[14px] text-red-500 text-center">{error}</p>
            )}

            {/* Start button */}
            <button
              onClick={handleStart}
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
                {isSubmitting ? "登录中..." : "开始"}
              </span>
              {!isSubmitting && <ArrowRightIcon />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
