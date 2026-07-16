from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)

    version = Column(Integer, nullable=False)

    heading = Column(String, nullable=False)

    level = Column(Integer, nullable=False)

    body = Column(Text)

    content_hash = Column(String)

    parent_id = Column(Integer, ForeignKey("nodes.id"))

    parent = relationship("Node", remote_side=[id])
    
class Selection(Base):

    __tablename__ = "selections"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    version = Column(Integer, nullable=False)

    node_ids = Column(Text, nullable=False)
    
class Generation(Base):

    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)

    selection_id = Column(Integer, ForeignKey("selections.id"))

    generated_text = Column(Text)

    version = Column(Integer)