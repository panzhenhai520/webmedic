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
        if document.parse_status == "done":
            from app.services.index_service import get_index_service
            try:
                index_service = await get_index_service()
                await index_service.index_document(db, document.id)
            except Exception as e:
                print(f"Failed to index document {document.id}: {e}")

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
        indexed_count = 0
        if new_added > 0:
            from app.services.index_service import get_index_service

            # 获取索引服务
            index_service = await get_index_service()

            # 索引所有新添加的文档（不限制状态）
            for doc in documents:
                # 只索引新添加的文档（已存在的跳过）
                if doc.index_status == "pending":
                    try:
                        await index_service.index_document(db, doc.id)
                        indexed_count += 1
                        print(f"Indexed document {doc.id}: {doc.file_name}")
                    except Exception as e:
                        print(f"Failed to index document {doc.id}: {e}")

            print(f"Total indexed: {indexed_count} documents")

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
            message=f"扫描完成，发现 {total_found} 个文件，新增 {new_added} 个，已存在 {already_exists} 个，已索引 {indexed_count} 个"
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


@router.delete("/{document_id}", response_model=dict)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    删除文档
    从数据库和向量数据库中删除文档记录
    """
    try:
        from app.models.similar_case_match import SimilarCaseMatch

        # 获取文档信息
        document = DocumentService.get_document_by_id(db, document_id)

        if not document:
            return error_response(message=f"文档 ID {document_id} 不存在")

        # 1. 删除相关的相似病历匹配记录（外键约束）
        db.query(SimilarCaseMatch).filter(
            SimilarCaseMatch.document_id == document_id
        ).delete()
        db.commit()

        # 2. 从向量数据库删除索引
        try:
            from app.services.index_service import get_index_service
            index_service = await get_index_service()
            await index_service.delete_document_index(db, document_id)
        except Exception as e:
            print(f"Failed to delete index for document {document_id}: {e}")

        # 3. 从数据库删除文档记录
        db.delete(document)
        db.commit()

        return success_response(
            data={"document_id": document_id},
            message=f"文档删除成功"
        )

    except Exception as e:
        db.rollback()
        return error_response(message=f"删除文档失败: {str(e)}")
