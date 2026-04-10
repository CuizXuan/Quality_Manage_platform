from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.case import TestCase

router = APIRouter(prefix="/api/folders", tags=["Folders"])


@router.get("")
def get_folder_tree(db: Session = Depends(get_db)):
    """获取用例的文件夹树结构"""
    rows = (
        db.query(TestCase.folder_path, func.count(TestCase.id).label("count"))
        .group_by(TestCase.folder_path)
        .order_by(TestCase.folder_path)
        .all()
    )
    tree = {}
    for path, count in rows:
        parts = [p for p in path.split("/") if p]
        node = tree
        for part in parts:
            if part not in node:
                node[part] = {"name": part, "children": {}, "count": 0}
            node = node[part]["children"]
        # 顶层累加
        root_key = parts[0] if parts else "/"
        if root_key not in tree and parts:
            tree[root_key] = {"name": root_key, "children": {}, "count": 0}

    def build_tree_dict(d, parent_path=""):
        result = []
        for name, info in sorted(d.items()):
            full_path = f"/{parent_path}/{name}".replace("//", "/") if parent_path else f"/{name}"
            children = build_tree_dict(info["children"], full_path)
            item = {"name": name, "path": full_path, "count": info["count"]}
            if children:
                item["children"] = children
            result.append(item)
        return result

    # 直接收集顶层
    result = []
    for path, count in rows:
        parts = [p for p in path.split("/") if p]
        if not parts:
            continue
        result.append({"name": parts[0], "path": f"/{parts[0]}", "count": sum(c for p, c in rows if p.startswith(f"/{parts[0]}"))})

    # 去重
    seen = {}
    for item in result:
        if item["path"] not in seen:
            seen[item["path"]] = item
    return list(seen.values())
