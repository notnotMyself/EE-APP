"""
法律文档API - Legal Documents API

提供隐私政策和用户协议的查询和同意记录功能
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/legal", tags=["legal"])

# 全局supabase客户端引用，由main.py注入
supabase_client = None


def set_supabase_client(client):
    """设置Supabase客户端"""
    global supabase_client
    supabase_client = client


# ============================================
# 数据模型 (Pydantic Schemas)
# ============================================


class LegalDocumentResponse(BaseModel):
    """法律文档响应模型"""

    id: str
    document_type: str  # 'privacy_policy' | 'terms_of_service'
    version: str
    title: str
    content: str  # Markdown格式
    effective_date: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class ConsentCreate(BaseModel):
    """用户同意请求模型"""

    document_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class ConsentResponse(BaseModel):
    """用户同意响应模型"""

    id: str
    user_id: str
    document_id: str
    document_type: str
    document_version: str
    consented_at: str

    class Config:
        from_attributes = True


# ============================================
# 辅助函数
# ============================================


def get_current_user_id(request: Request) -> str:
    """从JWT token中提取用户ID（简化实现）"""
    # 从请求头获取Bearer token
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization token")

    token = auth_header.replace("Bearer ", "")

    # 使用Supabase验证token并获取用户
    try:
        user = supabase_client.auth.get_user(token)
        if not user or not user.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user.user.id
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise HTTPException(status_code=401, detail="Token validation failed")


# ============================================
# API端点
# ============================================


@router.get("/documents/{document_type}", response_model=LegalDocumentResponse)
async def get_legal_document(document_type: str):
    """
    获取法律文档

    支持的文档类型:
    - privacy_policy: 隐私政策
    - terms_of_service: 用户协议

    返回当前有效版本的文档（is_active=true）
    """
    if not supabase_client:
        raise HTTPException(status_code=500, detail="Database not configured")

    if document_type not in ["privacy_policy", "terms_of_service"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid document type. Must be 'privacy_policy' or 'terms_of_service'",
        )

    try:
        # 查询当前有效版本的文档
        result = (
            supabase_client.table("legal_documents")
            .select("*")
            .eq("document_type", document_type)
            .eq("is_active", True)
            .order("effective_date", desc=True)
            .limit(1)
            .execute()
        )

        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=404, detail=f"Document not found: {document_type}"
            )

        document = result.data[0]

        return LegalDocumentResponse(**document)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching legal document: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch document")


@router.post("/consent", response_model=ConsentResponse)
async def create_consent(consent_data: ConsentCreate, request: Request):
    """
    记录用户同意

    用户首次登录时，必须同意隐私政策和用户协议。
    此端点记录用户的同意行为。
    """
    if not supabase_client:
        raise HTTPException(status_code=500, detail="Database not configured")

    # 获取当前用户ID
    user_id = get_current_user_id(request)

    try:
        # 1. 验证文档是否存在
        document_result = (
            supabase_client.table("legal_documents")
            .select("id, document_type, version")
            .eq("id", consent_data.document_id)
            .single()
            .execute()
        )

        if not document_result.data:
            raise HTTPException(status_code=404, detail="Document not found")

        document = document_result.data

        # 2. 检查是否已经同意过此文档
        existing_consent = (
            supabase_client.table("user_consents")
            .select("id")
            .eq("user_id", user_id)
            .eq("document_id", consent_data.document_id)
            .execute()
        )

        if existing_consent.data and len(existing_consent.data) > 0:
            # 已经同意过，返回现有记录
            consent_id = existing_consent.data[0]["id"]
            consent_result = (
                supabase_client.table("user_consents")
                .select("*")
                .eq("id", consent_id)
                .single()
                .execute()
            )
            return ConsentResponse(**consent_result.data)

        # 3. 创建新的同意记录
        consent_record = {
            "user_id": user_id,
            "document_id": consent_data.document_id,
            "document_type": document["document_type"],
            "document_version": document["version"],
            "ip_address": consent_data.ip_address,
            "user_agent": consent_data.user_agent,
        }

        result = supabase_client.table("user_consents").insert(consent_record).execute()

        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to create consent record")

        logger.info(
            f"User {user_id} consented to {document['document_type']} v{document['version']}"
        )

        return ConsentResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating consent: {e}")
        raise HTTPException(status_code=500, detail="Failed to create consent")


@router.get("/my-consents", response_model=List[ConsentResponse])
async def get_my_consents(request: Request):
    """
    查询当前用户的所有同意记录

    返回用户已同意的所有法律文档列表
    """
    if not supabase_client:
        raise HTTPException(status_code=500, detail="Database not configured")

    # 获取当前用户ID
    user_id = get_current_user_id(request)

    try:
        result = (
            supabase_client.table("user_consents")
            .select("*")
            .eq("user_id", user_id)
            .order("consented_at", desc=True)
            .execute()
        )

        consents = [ConsentResponse(**consent) for consent in result.data]

        return consents

    except Exception as e:
        logger.error(f"Error fetching user consents: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch consents")


@router.get("/check-consent-status")
async def check_consent_status(request: Request):
    """
    检查用户是否已同意所有必需的法律文档

    返回:
    {
      "privacy_policy_consented": bool,
      "terms_of_service_consented": bool,
      "all_consented": bool
    }

    用于在应用启动时检查是否需要显示协议同意页面
    """
    if not supabase_client:
        raise HTTPException(status_code=500, detail="Database not configured")

    # 获取当前用户ID
    user_id = get_current_user_id(request)

    try:
        # 获取用户的所有同意记录
        result = (
            supabase_client.table("user_consents")
            .select("document_type")
            .eq("user_id", user_id)
            .execute()
        )

        consented_types = set(consent["document_type"] for consent in result.data)

        privacy_policy_consented = "privacy_policy" in consented_types
        terms_of_service_consented = "terms_of_service" in consented_types
        all_consented = privacy_policy_consented and terms_of_service_consented

        return {
            "privacy_policy_consented": privacy_policy_consented,
            "terms_of_service_consented": terms_of_service_consented,
            "all_consented": all_consented,
        }

    except Exception as e:
        logger.error(f"Error checking consent status: {e}")
        raise HTTPException(status_code=500, detail="Failed to check consent status")
