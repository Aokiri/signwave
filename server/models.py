from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from server.database import Base

class Sign (Base):
    __tablename__ = "sign"
    id: Column = Column(Integer,  primary_key=True, index=True)
    word: Column = Column(String, nullable=False)
    standard: Column = Column(String, default = "ASL")
    description: Column = Column(String, nullable= True)
    hand: Column = Column(String, nullable=False) #left, right, both
    
    samples = relationship("Sample", back_populates="sign", cascade="all, delete-orphan")
    
    
class Sample(Base):
    __tablename__ = "sample"
    id: Column = Column(Integer, primary_key=True, index=True)
    sign_id: Column = Column(Integer, ForeignKey("sign.id"), nullable=False)
    emg_signal: Column = Column(Text, nullable=True)
    image_url: Column = Column(String, nullable= True)
    recorded_at: Column = Column(DateTime, default=lambda: datetime.now(timezone.utc)) #using utc becuse sql needs utc time (to avoid errors)
    
    sign = relationship("Sign", back_populates="samples")