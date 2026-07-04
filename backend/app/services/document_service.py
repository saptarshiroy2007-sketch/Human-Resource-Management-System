from fastapi import HTTPException, UploadFile, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.user import User, UserRole
from app.services.file_service import delete_file, save_upload


def upload_document(db: Session, user: User, doc_type: str, file: UploadFile) -> Document:
    file_url = save_upload(file, user.id)
    document = Document(user_id=user.id, doc_type=doc_type, file_url=file_url)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def list_user_documents(db: Session, user_id: int) -> list[Document]:
    query: Select[tuple[Document]] = (
        select(Document)
        .where(Document.user_id == user_id)
        .order_by(Document.uploaded_at.desc(), Document.id.desc())
    )
    return list(db.scalars(query))


def delete_document(db: Session, document_id: int, user: User) -> None:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    if document.user_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    delete_file(document.file_url)
    db.delete(document)
    db.commit()
