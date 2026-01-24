"""
应用版本管理 API

提供 APP 版本检查和更新功能
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import os

router = APIRouter(prefix="/app", tags=["应用管理"])


class DownloadSource(BaseModel):
    """下载源"""
    name: str = Field(..., description="下载源名称")
    url: str = Field(..., description="下载地址")
    speed: str = Field(default="medium", description="速度标识: fast/medium/slow")


class AppVersionInfo(BaseModel):
    """应用版本信息"""
    version_code: int = Field(..., description="版本号（数字）")
    version_name: str = Field(..., description="版本名称（如 0.1.0）")
    apk_url: str = Field(..., description="APK 下载地址")
    apk_size: int = Field(..., description="APK 文件大小（字节）")
    apk_md5: Optional[str] = Field(None, description="APK MD5 校验值")
    release_notes: str = Field(..., description="更新说明")
    force_update: bool = Field(default=False, description="是否强制更新")
    download_sources: List[DownloadSource] = Field(default=[], description="多个下载源")
    published_at: Optional[datetime] = Field(None, description="发布时间")


class CheckUpdateResponse(BaseModel):
    """检查更新响应"""
    has_update: bool = Field(..., description="是否有更新")
    latest_version: Optional[AppVersionInfo] = Field(None, description="最新版本信息")
    message: str = Field(..., description="提示信息")


@router.get("/version/latest", response_model=CheckUpdateResponse, summary="检查更新")
async def check_update(
    current_version: int = Query(..., description="当前版本号", ge=1),
    region: str = Query("cn", description="地区代码（cn/us/global）")
):
    """
    检查是否有新版本

    - **current_version**: 当前 APP 版本号
    - **region**: 用户地区（用于选择最优下载源）

    返回：
    - has_update: 是否有更新
    - latest_version: 最新版本信息（包含下载地址）
    """

    try:
        from supabase import create_client

        # Supabase 配置
        supabase_url = os.getenv("SUPABASE_URL", "https://dwesyojvzbltqtgtctpt.supabase.co")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

        if not supabase_key:
            # 如果没有配置，返回模拟数据
            return CheckUpdateResponse(
                has_update=False,
                latest_version=None,
                message="版本检查服务未配置"
            )

        supabase = create_client(supabase_url, supabase_key)

        # 查询最新的激活版本
        response = supabase.table("app_versions")\
            .select("*")\
            .eq("is_active", True)\
            .order("version_code", desc=True)\
            .limit(1)\
            .execute()

        if not response.data:
            return CheckUpdateResponse(
                has_update=False,
                latest_version=None,
                message="暂无可用版本"
            )

        latest = response.data[0]
        latest_version_code = latest["version_code"]

        # 检查是否有更新
        has_update = latest_version_code > current_version

        if not has_update:
            return CheckUpdateResponse(
                has_update=False,
                latest_version=None,
                message="已是最新版本"
            )

        # 构建下载源列表
        download_sources = []

        # 主下载源
        download_sources.append(DownloadSource(
            name="主线路",
            url=latest["apk_url"],
            speed="fast"
        ))

        # 备用下载源（如果有）
        if latest.get("apk_mirror_urls"):
            for idx, mirror_url in enumerate(latest["apk_mirror_urls"]):
                if isinstance(mirror_url, dict):
                    download_sources.append(DownloadSource(
                        name=mirror_url.get("name", f"备用线路 {idx+1}"),
                        url=mirror_url["url"],
                        speed=mirror_url.get("speed", "medium")
                    ))
                else:
                    download_sources.append(DownloadSource(
                        name=f"备用线路 {idx+1}",
                        url=str(mirror_url),
                        speed="medium"
                    ))

        # 构建版本信息
        version_info = AppVersionInfo(
            version_code=latest["version_code"],
            version_name=latest["version_name"],
            apk_url=latest["apk_url"],
            apk_size=latest.get("apk_size", 0),
            apk_md5=latest.get("apk_md5"),
            release_notes=latest.get("release_notes", ""),
            force_update=latest.get("force_update", False),
            download_sources=download_sources,
            published_at=latest.get("published_at")
        )

        # 检查是否需要强制更新
        min_support_version = latest.get("min_support_version")
        if min_support_version and current_version < min_support_version:
            version_info.force_update = True

        return CheckUpdateResponse(
            has_update=True,
            latest_version=version_info,
            message=f"发现新版本 {latest['version_name']}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"检查更新失败: {str(e)}"
        )


@router.get("/version/list", response_model=List[AppVersionInfo], summary="获取版本列表")
async def get_version_list(
    limit: int = Query(10, description="返回数量", ge=1, le=50),
    offset: int = Query(0, description="偏移量", ge=0)
):
    """
    获取历史版本列表

    用于版本管理和历史查看
    """
    try:
        from supabase import create_client

        supabase_url = os.getenv("SUPABASE_URL", "https://dwesyojvzbltqtgtctpt.supabase.co")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

        if not supabase_key:
            return []

        supabase = create_client(supabase_url, supabase_key)

        response = supabase.table("app_versions")\
            .select("*")\
            .order("version_code", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()

        versions = []
        for item in response.data:
            versions.append(AppVersionInfo(
                version_code=item["version_code"],
                version_name=item["version_name"],
                apk_url=item["apk_url"],
                apk_size=item.get("apk_size", 0),
                apk_md5=item.get("apk_md5"),
                release_notes=item.get("release_notes", ""),
                force_update=item.get("force_update", False),
                download_sources=[],
                published_at=item.get("published_at")
            ))

        return versions

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取版本列表失败: {str(e)}"
        )


@router.get("/version/{version_code}", response_model=AppVersionInfo, summary="获取指定版本")
async def get_version_by_code(version_code: int):
    """
    获取指定版本的详细信息
    """
    try:
        from supabase import create_client

        supabase_url = os.getenv("SUPABASE_URL", "https://dwesyojvzbltqtgtctpt.supabase.co")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

        if not supabase_key:
            raise HTTPException(status_code=503, detail="服务未配置")

        supabase = create_client(supabase_url, supabase_key)

        response = supabase.table("app_versions")\
            .select("*")\
            .eq("version_code", version_code)\
            .limit(1)\
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="版本不存在")

        item = response.data[0]

        return AppVersionInfo(
            version_code=item["version_code"],
            version_name=item["version_name"],
            apk_url=item["apk_url"],
            apk_size=item.get("apk_size", 0),
            apk_md5=item.get("apk_md5"),
            release_notes=item.get("release_notes", ""),
            force_update=item.get("force_update", False),
            download_sources=[],
            published_at=item.get("published_at")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取版本信息失败: {str(e)}"
        )
