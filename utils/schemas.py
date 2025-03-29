from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class AdminRegisterRequest(BaseModel):
    username: str = Field(description="用户名，全局唯一", 
                        examples=["qqq"])
    password: str = Field(description="密码", 
                        examples=["qqq"])


class AdminLoginRequest(BaseModel):
    username: str = Field(description="用户名，全局唯一", 
                        examples=["qqq"])
    password: str = Field(description="密码", 
                        examples=["qqq"])


class UserChangePartyBranchRequest(BaseModel):
    name: str = Field(description="姓名",
                examples=["张三"])
    student_id: str = Field(description="学号",
                examples=["202500996677"])
    party_branch: str = Field(description="党支部名称",
                examples=["控制科学与工程学院党支部"])
    

class QuestionCreateRequest(BaseModel):
    type: int = Field(description="题目类型，0为单选，1为多选",
                    examples=[0])
    text: str = Field(description="题目内容",
                    examples=["中国共产党在哪一年成立？"])
    A: str = Field(description="选项A",
                    examples=["1920"])
    B: str = Field(description="选项B",
                    examples=["1921"])
    C: str = Field(description="选项C",
                    examples=["1922"])  
    D: str = Field(description="选项D",
                    examples=["1923"])
    answer: str = Field(description="正确答案，字符串格式，单选形如'A'，多选形如'ABD'",
                    examples=["B"])
    

class ProjectCreateRequest(BaseModel):
    name: str = Field(description="项目名称",
                    examples=["2026年第6期党建知识问答"])
    issue_num: int = Field(description="期号",
                    examples=[6])
    starttime: datetime = Field(description="项目开始时间",
                    examples=["2026-06-01 09:00:00"])
    deadline: datetime = Field(description="项目截止时间",
                    examples=["2026-06-30 18:00:00"])
    questions: list[QuestionCreateRequest] = Field(description="项目问题列表", 
                                                default_factory=list)


# class QuestionDetailResponse(QuestionCreateRequest):
#     id: int = Field(description="问题ID",
#                     examples=[1])


# class ProjectDetailResponseData(BaseModel):
#     uuid: UUID = Field(description="项目UUID",
#                     examples=["4ddc1160-0bcb-11f0-a3a7-a340c0b22593"])
#     name: str = Field(description="项目名称",
#                     examples=["2026年第6期党建知识问答"])
#     starttime: datetime = Field(description="项目开始时间",
#                     examples=["2026-06-01 09:00:00"])
#     deadline: datetime = Field(description="项目截止时间",
#                     examples=["2026-06-30 18:00:00"])
#     status: int = Field(description="项目状态，0为未开始，1为进行中，2为已结束",
#                     examples=[1])
#     questions: list[QuestionDetailResponse] = Field(description="项目问题列表",
#                                                     default_factory=list)


class ProjectUpdateRequest(BaseModel):
    name: str = Field(description="项目名称",
                    examples=["2026年第6期党建知识问答"])
    issue_num: int = Field(description="期号",
                    examples=[6])
    starttime: datetime = Field(description="项目开始时间",
                    examples=["2026-06-01 09:00:00"])
    deadline: datetime = Field(description="项目截止时间",
                    examples=["2026-06-30 18:00:00"])
    questions: list[QuestionCreateRequest] = Field(description="项目问题列表", 
                                                default_factory=list)
    

class CommitAnswer(BaseModel):
    question_id: int = Field(description="问题ID",
                    examples=[1])
    user_answer: str = Field(description="答案，字符串格式，单选形如'A'，多选形如'ABD'",
                    examples=["B"])
    

class CommitAnswerRequest(CommitAnswer):
    student_id: str = Field(description="学号", examples=["202500996677"])
    project_uuid: str = Field(description="项目ID", examples=["4ddc1160-0bcb-11f0-a3a7-a340c0b22593"])
    time_used_seconds: str = Field(description="用时（秒）", examples=["111.22"])
    correct_num: int = Field(description="答对数量", examples=[15])
    user_answers: list[CommitAnswer] = Field(description="答案列表", default_factory=list)