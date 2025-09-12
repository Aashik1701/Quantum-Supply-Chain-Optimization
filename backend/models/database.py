"""
Database models for supply chain optimization
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, Dict, Any
import uuid

from sqlalchemy import (
    String, Integer, Float, DateTime, Boolean, Text, JSON,
    ForeignKey, Enum, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

Base = declarative_base()


class OptimizationMethod(PyEnum):
    CLASSICAL = "classical"
    QUANTUM = "quantum"
    HYBRID = "hybrid"


class JobStatus(PyEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Warehouse(Base):
    __tablename__ = "warehouses"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    operating_cost: Mapped[float] = mapped_column(Float, default=0.0)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    assignments = relationship("Assignment", back_populates="warehouse")
    
    __table_args__ = (
        Index('idx_warehouse_location', 'latitude', 'longitude'),
        Index('idx_warehouse_capacity', 'capacity'),
    )


class Customer(Base):
    __tablename__ = "customers"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    demand: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    assignments = relationship("Assignment", back_populates="customer")
    
    __table_args__ = (
        Index('idx_customer_location', 'latitude', 'longitude'),
        Index('idx_customer_demand', 'demand'),
    )


class Route(Base):
    __tablename__ = "routes"
    
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    warehouse_id: Mapped[str] = mapped_column(
        String(50), 
        ForeignKey("warehouses.id"), 
        nullable=False
    )
    customer_id: Mapped[str] = mapped_column(
        String(50), 
        ForeignKey("customers.id"), 
        nullable=False
    )
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    transport_mode: Mapped[str] = mapped_column(String(50), default="truck")
    cost_per_km: Mapped[float] = mapped_column(Float, default=1.0)
    co2_per_km: Mapped[float] = mapped_column(Float, default=0.4)
    speed_kmh: Mapped[float] = mapped_column(Float, default=80.0)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    warehouse = relationship("Warehouse")
    customer = relationship("Customer")
    
    __table_args__ = (
        Index('idx_route_warehouse', 'warehouse_id'),
        Index('idx_route_customer', 'customer_id'),
        Index('idx_route_distance', 'distance_km'),
    )


class OptimizationJob(Base):
    __tablename__ = "optimization_jobs"
    
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    method: Mapped[OptimizationMethod] = mapped_column(
        Enum(OptimizationMethod), 
        nullable=False
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus), 
        default=JobStatus.PENDING
    )
    progress: Mapped[int] = mapped_column(Integer, default=0)
    
    # Input data
    input_data: Mapped[Dict[str, Any]] = mapped_column(JSON)
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Relationships
    result = relationship("OptimizationResult", back_populates="job", uselist=False)
    
    __table_args__ = (
        Index('idx_job_status', 'status'),
        Index('idx_job_method', 'method'),
        Index('idx_job_created', 'created_at'),
    )


class OptimizationResult(Base):
    __tablename__ = "optimization_results"
    
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    job_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("optimization_jobs.id"), 
        nullable=False, 
        unique=True
    )
    
    # Core metrics
    total_cost: Mapped[float] = mapped_column(Float, nullable=False)
    total_co2: Mapped[float] = mapped_column(Float, nullable=False)
    avg_delivery_time: Mapped[float] = mapped_column(Float, nullable=False)
    routes_used: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Performance metrics
    optimization_time: Mapped[float] = mapped_column(Float, nullable=False)
    iterations: Mapped[int] = mapped_column(Integer, default=0)
    convergence: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Detailed results
    routes_data: Mapped[Dict[str, Any]] = mapped_column(JSON)
    assignments_data: Mapped[Dict[str, Any]] = mapped_column(JSON)
    performance_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    job = relationship("OptimizationJob", back_populates="result")
    assignments = relationship("Assignment", back_populates="result")
    
    __table_args__ = (
        Index('idx_result_job', 'job_id'),
        Index('idx_result_cost', 'total_cost'),
        Index('idx_result_created', 'created_at'),
    )


class Assignment(Base):
    __tablename__ = "assignments"
    
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    result_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("optimization_results.id"), 
        nullable=False
    )
    warehouse_id: Mapped[str] = mapped_column(
        String(50), 
        ForeignKey("warehouses.id"), 
        nullable=False
    )
    customer_id: Mapped[str] = mapped_column(
        String(50), 
        ForeignKey("customers.id"), 
        nullable=False
    )
    
    # Assignment details
    demand: Mapped[int] = mapped_column(Integer, nullable=False)
    cost: Mapped[float] = mapped_column(Float, nullable=False)
    co2: Mapped[float] = mapped_column(Float, nullable=False)
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_time_hours: Mapped[float] = mapped_column(Float, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    result = relationship("OptimizationResult", back_populates="assignments")
    warehouse = relationship("Warehouse", back_populates="assignments")
    customer = relationship("Customer", back_populates="assignments")
    
    __table_args__ = (
        Index('idx_assignment_result', 'result_id'),
        Index('idx_assignment_warehouse', 'warehouse_id'),
        Index('idx_assignment_customer', 'customer_id'),
    )
