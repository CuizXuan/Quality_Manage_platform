from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, field_serializer
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.tenant_middleware import get_current_tenant_id
from app.models.case import TestCase
from app.models.case_folder import CaseFolder

router = APIRouter(prefix="/api/case-folders", tags=["case-folders"])

ROOT_FOLDER_NAME = "根目录"
ROOT_FOLDER_PATH = f"/{ROOT_FOLDER_NAME}"
TERMINAL_FOLDER_NAME = "终端导入"


def get_tenant_id(request: Request) -> int:
    tenant_id = get_current_tenant_id(request)
    if tenant_id is None:
        raise HTTPException(status_code=403, detail="需要租户权限")
    return tenant_id


class FolderCreate(BaseModel):
    name: str
    parent_id: int | None = None
    sort_order: int = 0


class FolderUpdate(BaseModel):
    name: str | None = None
    parent_id: int | None = None
    sort_order: int | None = None


class FolderResponse(BaseModel):
    id: int
    name: str
    parent_id: int | None
    sort_order: int
    is_fixed: bool = False
    created_at: datetime
    updated_at: datetime | None

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, dt: datetime | None) -> str | None:
        return dt.isoformat() if dt else None


class FolderTreeResponse(BaseModel):
    id: int
    name: str
    parent_id: int | None
    sort_order: int
    children: List["FolderTreeResponse"] = []
    is_fixed: bool = False

    @field_serializer("children")
    def serialize_children(self, children: List["FolderTreeResponse"]) -> List[dict]:
        return [child.model_dump() for child in children]


def is_system_folder(folder: CaseFolder) -> bool:
    return folder.name in {ROOT_FOLDER_NAME, TERMINAL_FOLDER_NAME}


def folder_response(folder: CaseFolder) -> FolderResponse:
    return FolderResponse(
        id=folder.id,
        name=folder.name,
        parent_id=folder.parent_id,
        sort_order=folder.sort_order,
        is_fixed=is_system_folder(folder),
        created_at=folder.created_at,
        updated_at=folder.updated_at,
    )


def build_folder_tree(
    folders: List[CaseFolder],
    parent_id: int | None = None,
) -> List[FolderTreeResponse]:
    tree = []
    for folder in folders:
        if folder.parent_id != parent_id:
            continue
        tree.append(FolderTreeResponse(
            id=folder.id,
            name=folder.name,
            parent_id=folder.parent_id,
            sort_order=folder.sort_order,
            children=build_folder_tree(folders, folder.id),
            is_fixed=is_system_folder(folder),
        ))
    tree.sort(key=lambda item: (item.sort_order, item.id))
    return tree


def ensure_root_folder(db: Session, tenant_id: int) -> CaseFolder:
    root = db.query(CaseFolder).filter(
        CaseFolder.tenant_id == tenant_id,
        CaseFolder.name == ROOT_FOLDER_NAME,
    ).first()
    if root:
        return root

    root = CaseFolder(
        name=ROOT_FOLDER_NAME,
        parent_id=None,
        sort_order=-100,
        tenant_id=tenant_id,
    )
    db.add(root)
    db.flush()
    return root


def normalize_root_children(db: Session, tenant_id: int, root_id: int) -> None:
    db.query(CaseFolder).filter(
        CaseFolder.tenant_id == tenant_id,
        CaseFolder.parent_id.is_(None),
        CaseFolder.id != root_id,
    ).update({CaseFolder.parent_id: root_id}, synchronize_session=False)


def normalize_uncategorized_cases(db: Session, tenant_id: int) -> None:
    db.query(TestCase).filter(
        TestCase.tenant_id == tenant_id,
        or_(
            TestCase.folder_path.is_(None),
            TestCase.folder_path.in_(["", "/"]),
        ),
    ).update({TestCase.folder_path: ROOT_FOLDER_PATH}, synchronize_session=False)


def prepare_root_folder(db: Session, tenant_id: int) -> CaseFolder:
    root = ensure_root_folder(db, tenant_id)
    normalize_root_children(db, tenant_id, root.id)
    normalize_uncategorized_cases(db, tenant_id)
    db.commit()
    db.refresh(root)
    return root


@router.get("", response_model=List[FolderTreeResponse])
def list_folders(
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    prepare_root_folder(db, tenant_id)
    folders = db.query(CaseFolder).filter(
        CaseFolder.tenant_id == tenant_id,
    ).order_by(CaseFolder.sort_order, CaseFolder.id).all()
    return build_folder_tree(folders)


@router.get("/flat", response_model=List[FolderResponse])
def list_folders_flat(
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    prepare_root_folder(db, tenant_id)
    folders = db.query(CaseFolder).filter(
        CaseFolder.tenant_id == tenant_id,
    ).order_by(CaseFolder.sort_order, CaseFolder.id).all()
    return [folder_response(folder) for folder in folders]


@router.post("", response_model=FolderResponse, status_code=201)
def create_folder(
    data: FolderCreate,
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    root = prepare_root_folder(db, tenant_id)
    if data.name == ROOT_FOLDER_NAME:
        raise HTTPException(status_code=400, detail="根目录已存在")

    folder = CaseFolder(
        name=data.name,
        parent_id=data.parent_id or root.id,
        sort_order=data.sort_order,
        tenant_id=tenant_id,
    )
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder_response(folder)


@router.put("/{folder_id}", response_model=FolderResponse)
def update_folder(
    folder_id: int,
    data: FolderUpdate,
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    folder = get_folder_or_404(db, tenant_id, folder_id)
    if is_system_folder(folder):
        raise HTTPException(status_code=400, detail="系统目录无法编辑")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(folder, key, value)
    db.commit()
    db.refresh(folder)
    return folder_response(folder)


@router.delete("/{folder_id}", status_code=204)
def delete_folder(
    folder_id: int,
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    folder = get_folder_or_404(db, tenant_id, folder_id)
    if is_system_folder(folder):
        raise HTTPException(status_code=400, detail="系统目录无法删除")

    has_children = db.query(CaseFolder).filter(
        CaseFolder.parent_id == folder_id,
        CaseFolder.tenant_id == tenant_id,
    ).first()
    if has_children:
        raise HTTPException(status_code=400, detail="Folder has sub-folders, delete them first")

    db.delete(folder)
    db.commit()


@router.post("/ensure-root-folder", response_model=FolderResponse)
def ensure_root_folder_route(
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    root = prepare_root_folder(db, tenant_id)
    return folder_response(root)


@router.post("/ensure-terminal-folder", response_model=FolderResponse)
def ensure_terminal_folder(
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    root = prepare_root_folder(db, tenant_id)
    folder = db.query(CaseFolder).filter(
        CaseFolder.tenant_id == tenant_id,
        CaseFolder.name == TERMINAL_FOLDER_NAME,
    ).first()
    if not folder:
        folder = CaseFolder(
            name=TERMINAL_FOLDER_NAME,
            parent_id=root.id,
            sort_order=99,
            tenant_id=tenant_id,
        )
        db.add(folder)
        db.commit()
        db.refresh(folder)
    return folder_response(folder)


def get_folder_or_404(db: Session, tenant_id: int, folder_id: int) -> CaseFolder:
    folder = db.query(CaseFolder).filter(
        CaseFolder.id == folder_id,
        CaseFolder.tenant_id == tenant_id,
    ).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder
