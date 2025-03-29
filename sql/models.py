from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, time


class User(SQLModel, table=True):
    student_id: str = Field(primary_key=True, unique=True)
    name: str
    party_branch: str
    records: list["Record"] = Relationship(back_populates="student", cascade_delete=True)


class Admin(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    hashed_password: str
    projects: list["Project"] = Relationship(back_populates="creater", cascade_delete=True)


class Project(SQLModel, table=True):
    uuid: str = Field(primary_key=True)
    name: str
    starttime: datetime
    deadline: datetime
    status: int = Field(default=0)  # 0为未开始，1为进行中，2为已结束
    questions: list["Question"] = Relationship(back_populates="project", cascade_delete=True)
    records: list["Record"] = Relationship(back_populates="project", cascade_delete=True)
    participate_num: int = Field(default=0)
    creater_id: int = Field(foreign_key="admin.id", ondelete="CASCADE")
    creater: Admin = Relationship(back_populates="projects")


class Question(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    type: int = Field(description="题目类型，0为单选，1为多选")
    text: str
    A: str
    B: str
    C: str
    D: str
    answer: str
    project_uuid: str = Field(foreign_key="project.uuid", ondelete="CASCADE")
    project: Project = Relationship(back_populates="questions")


class Record(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    student_id: str = Field(foreign_key="user.student_id", ondelete="CASCADE")
    student: User = Relationship(back_populates="records")
    project_uuid: str = Field(foreign_key="project.uuid", ondelete="CASCADE")
    project: Project = Relationship(back_populates="records")
    answer: str
    correct_num: int
    time_used_seconds: float
    
