from pgvector.sqlalchemy import Vector
from sqlalchemy import Computed
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import configure_mappers

from app.database.models import Base, DocumentChunk


def test_all_model_tables_are_registered() -> None:
    configure_mappers()

    assert set(Base.metadata.tables) == {
        "chat_messages",
        "chat_threads",
        "document_chunks",
        "message_citations",
        "source_documents",
        "users",
    }


def test_document_chunks_have_retrieval_columns() -> None:
    embedding = DocumentChunk.__table__.c.embedding
    search_vector = DocumentChunk.__table__.c.search_vector

    assert isinstance(embedding.type, Vector)
    assert embedding.type.dim == 1536
    assert isinstance(search_vector.type, TSVECTOR)
    assert isinstance(search_vector.computed, Computed)
    assert search_vector.computed.sqltext.text == "to_tsvector('english', content)"
    assert search_vector.computed.persisted is True
