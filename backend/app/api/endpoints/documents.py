#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Documents API Endpoints
病历文档管理接口
"""

import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.response import success_response, error_response
from app.core.config import settings
from app.db.session import get_db
from app.schemas.document_schema import ScanLocalRequest, ScanLocalResponse, DocumentInfo
from app.services.document_service import DocumentService
from app.services.index_service import IndexService

router = APIRouter()


@router.post("/upload", response_model=dict)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传 PDF 病历文件
    上传后自动登记并索引
    """
    try:
        # 检查文件类型
        if not file.filename.lower().endswith('.pdf'):
            return error_response(message="仅支持 PDF 格式文件")

        # 确保上传目录存在
        upload_dir = os.path.join(settings.MEDICAL_RECORD_DIR)
        os.makedirs(upload_dir, exist_ok=True)

        # 保存文件
        file_path = os.path.join(upload_dir, file.filename)

        # 如果文件已存在，添加序号
        base_name = os.path.splitext(file.filename)[0]
        ext = os.path.splitext(file.filename)[1]
        counter = 1
        while os.path.exists(file_path):
            file_path = os.path.join(upload_dir, f"{base_name}_{counter}{ext}")
            counter += 1

        # 写入文件
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 登记到数据库
        document = DocumentService.register_document(db, file_path)

        # 自动索引
        IndexService.index_single_document(db, document.id)

        # 转换为响应格式
        document_info = DocumentInfo(
            id=document.id,
            file_name=document.file_name,
            file_path=document.file_path,
            file_hash=document.file_hash,
            parse_status=document.parse_status,
            index_status=document.index_status,
            source_type=document.source_type,
            created_at=document.created_at,
            updated_at=document.updated_at
        )

        return success_response(
            data=document_info.model_dump(),
            message=f"文件上传成功并已自动索引"
        )

    except Exception as e:
        return error_response(message=f"上传文件失败: {str(e)}")


@router.post("/scan-local", response_model=dict)
async def scan_local_directory(
    request: ScanLocalRequest,
    db: Session = Depends(get_db)
):
    """
    扫描本地病历目录
    发现并登记 PDF 文件到数据库，然后自动索引
    """
    try:
        total_found, new_added, already_exists, documents = DocumentService.scan_local_directory(
            db=db,
            directory=request.directory
        )

        # 自动索引新添加的文档
        if new_added > 0:
            IndexService.rebuild_index(db)

        # 转换为响应格式
        document_infos = [
            DocumentInfo(
                id=doc.id,
                file_name=doc.file_name,
                file_path=doc.file_path,
                file_hash=doc.file_hash,
                parse_status=doc.parse_status,
                index_status=doc.index_status,
                source_type=doc.source_type,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            )
            for doc in documents
        ]

        response_data = ScanLocalResponse(
            total_found=total_found,
            new_added=new_added,
            already_exists=already_exists,
            documents=document_infos
        )

        return success_response(
            data=response_data.model_dump(),
            message=f"扫描完成，发现 {total_found} 个文件，新增 {new_added} 个，已存在 {already_exists} 个，已自动索引"
        )

    except ValueError as e:
        return error_response(message=str(e))
    except Exception as e:
        return error_response(message=f"扫描目录失败: {str(e)}")


@router.get("/list", response_model=dict)
async def list_documents(db: Session = Depends(get_db)):
    """
    获取所有文档列表
    """
    try:
        documents = DocumentService.get_all_documents(db)

        document_infos = [
            DocumentInfo(
                id=doc.id,
                file_name=doc.file_name,
                file_path=doc.file_path,
                file_hash=doc.file_hash,
                parse_status=doc.parse_status,
                index_status=doc.index_status,
                source_type=doc.source_type,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            )
            for doc in documents
        ]

        return success_response(
            data={"documents": [doc.model_dump() for doc in document_infos]},
            message="获取文档列表成功"
        )

    except Exception as e:
        return error_response(message=f"获取文档列表失败: {str(e)}")


@router.get("/view/{document_id}")
async def view_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    查看 PDF 文档
    返回 PDF 文件供浏览器直接打开
    """
    try:
        # 获取文档信息
        document = DocumentService.get_document_by_id(db, document_id)

        if not document:
            raise HTTPException(status_code=404, detail=f"文档 ID {document_id} 不存在")

        # 检查文件是否存在
        if not os.path.exists(document.file_path):
            raise HTTPException(status_code=404, detail=f"文件不存在: {document.file_path}")

        # 返回 PDF 文件，设置为 inline 让浏览器直接打开
        return FileResponse(
            path=document.file_path,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{document.file_name}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查看文档失败: {str(e)}")
