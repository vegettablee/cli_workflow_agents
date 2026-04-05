# models that mimic the ddl script, making it easier for insertions and other functionality because it is enforced

from sqlalchemy import Column, Integer, String, Text, Date, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship
from typing import Optional
from datetime import date

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'

    company_id = Column(Integer, primary_key=True, autoincrement=True)
    cname = Column(Text, unique=True, nullable=False)
    company_website = Column(Text)
    company_size = Column(Text)
    category = Column(Text)
    company_city = Column(Text)
    company_state = Column(String(2))
    company_description = Column(Text)
    contact_status = Column(
        Text,
        default='N/A',
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "contact_status IN ('N/A', 'Ghosted', 'NoInfo')",
            name='check_company_contact_status'
        ),
    )

    # Relationships
    emails = relationship("Email", back_populates="company", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")


class Email(Base):
    __tablename__ = 'emails'

    email = Column(Text, unique=True, primary_key=True, nullable=False)
    company_id = Column(Integer, ForeignKey('companies.company_id', ondelete='CASCADE'))
    num_sent = Column(Integer, default=0)
    num_replied = Column(Integer, default=0)
    template_id = Column(Integer)
    last_date_sent = Column(Date, nullable=True)
    contact_status = Column(
        Text,
        default='N/A',
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "contact_status IN ('N/A', 'Ghosted', 'Interested')",
            name='check_email_contact_status'
        ),
    )

    # Relationships
    company = relationship("Company", back_populates="emails")
    recruiter_email = relationship("RecruiterEmail", back_populates="email_ref", uselist=False)


class Recruiter(Base):
    __tablename__ = 'recruiters'

    recruiter_id = Column(Integer, primary_key=True, autoincrement=True)
    fname = Column(Text, nullable=False)
    lname = Column(Text, nullable=False)
    linkedin = Column(Text, default='Unknown')

    # Relationships
    recruiter_emails = relationship("RecruiterEmail", back_populates="recruiter")


class RecruiterEmail(Base):
    __tablename__ = 'recruiter_emails'

    id = Column(Integer, primary_key=True, autoincrement=True)
    recruiter_id = Column(Integer, ForeignKey('recruiters.recruiter_id'))
    email = Column(Text, ForeignKey('emails.email'), unique=True, nullable=False)

    # Relationships
    recruiter = relationship("Recruiter", back_populates="recruiter_emails")
    email_ref = relationship("Email", back_populates="recruiter_email")


class Job(Base):
    __tablename__ = 'jobs'

    job_id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.company_id', ondelete='CASCADE'))
    role_name = Column(Text, nullable=False)
    source_url = Column(Text, nullable=False)  # Removed unique constraint
    is_open = Column(Boolean, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="jobs")