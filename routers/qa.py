from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
import utils.schemas as schemas
from sql.database import get_session
from utils.authorization import *
from uuid import uuid1
import utils.response_format as rf


router = APIRouter()


@router.post("/admin/project",
            summary="管理员发布一期问答项目")
async def create_project(project: schemas.ProjectCreateRequest, 
session: Session=Depends(get_session),
admin=Depends(admin_verify_token)):
    """管理员上传题目并发布一期问答项目

    需要验证token

    返回创建的项目的uuid
    """
    project_uuid = str(uuid1())
    now_time = datetime.now()
    project_status = 0
    if now_time < project.starttime:
        project_status = 0  # 未开始
    elif now_time > project.deadline:
        project_status = 2  # 已结束
    else:
        project_status = 1  # 进行中
    project_for_db = models.Project(
        uuid=project_uuid,
        name=project.name,
        starttime=project.starttime,
        deadline=project.deadline,
        status=project_status,
        creater_id=admin.id
    )
    session.add(project_for_db)
    session.commit()
    session.refresh(project_for_db)
    
    for question in project.questions:
        question_for_db = models.Question.model_validate(question,
                update={
                    "project_uuid": project_uuid
            })
        session.add(question_for_db)
        session.commit()
        session.refresh(question_for_db)
    
    return rf.res_201(message="项目创建成功", data={
        "project_uuid": project_uuid,
    })


@router.get("/admin/project/{project_uuid}",
            summary="管理员获取项目详情(问题与答案)",
            dependencies=[Depends(admin_verify_token)])
async def get_project(project_uuid: str, 
session: Session=Depends(get_session)):
    project = session.get(models.Project, project_uuid)
    if not project:
        return rf.res_404(message="项目不存在")
    project_data = project.model_dump()
    project_data["starttime"] = project_data["starttime"].strftime("%Y-%m-%d %H:%M:%S")
    project_data["deadline"] = project_data["deadline"].strftime("%Y-%m-%d %H:%M:%S")
    project_data["questions"] = [
        question.model_dump(exclude={"project_uuid"}) for question in project.questions
    ]
    return rf.res_200(message="项目详情获取成功", data=project_data)


@router.put("/admin/project/{project_uuid}",
            summary="管理员更新项目信息")
async def update_project(project_uuid: str, 
project: schemas.ProjectUpdateRequest, 
admin=Depends(admin_verify_token),
session: Session=Depends(get_session)):
    project_in_db = session.get(models.Project, project_uuid)
    if not project_in_db:
        return rf.res_404(message="项目不存在")
    project_uuid = project_in_db.uuid
    # 删除原项目
    session.delete(project_in_db)
    session.commit()
    # 创建新项目
    now_time = datetime.now()
    project_status = 0
    if now_time < project.starttime:
        project_status = 0  # 未开始
    elif now_time > project.deadline:
        project_status = 2  # 已结束
    else:
        project_status = 1  # 进行中
    project_for_db = models.Project(
        uuid=project_uuid,
        name=project.name,
        starttime=project.starttime,
        deadline=project.deadline,
        status=project_status,
        creater_id=admin.id
    )
    session.add(project_for_db)
    session.commit()
    session.refresh(project_for_db)
    
    for question in project.questions:
        question_for_db = models.Question.model_validate(question,
                update={
                    "project_uuid": project_uuid
            })
        session.add(question_for_db)
        session.commit()
        session.refresh(question_for_db)
    
    return rf.res_200(message="项目更新成功", data={
        "project_uuid": project_uuid,
    })


@router.delete("/admin/project/{project_uuid}",
            summary="管理员删除项目",
            dependencies=[Depends(admin_verify_token)])
async def delete_project(project_uuid: str, 
session: Session=Depends(get_session)):
    project = session.get(models.Project, project_uuid)
    if not project:
        return rf.res_404(message="项目不存在")
    session.delete(project)
    session.commit()
    return rf.res_204(message="项目删除成功")


@router.get("/user/project/{project_uuid}",
    summary="用户获取项目详情(问题与答案)")
async def get_project(project_uuid: str, 
student_id: str,
session: Session=Depends(get_session)):
    """如果用户没有答题记录，返回题目与答案；

    如果用户有答题记录，还会返回其作答情况；
    """
    project = session.get(models.Project, project_uuid)
    if not project:
        return rf.res_404(message="项目不存在")
    project_data = project.model_dump()
    project_data["starttime"] = project_data["starttime"].strftime("%Y-%m-%d %H:%M:%S")
    project_data["deadline"] = project_data["deadline"].strftime("%Y-%m-%d %H:%M:%S")
    project_data["questions"] = [
        question.model_dump(exclude={"project_uuid"}) for question in project.questions
    ]
    #* 先判断用户是否设置过党支部信息
    student = session.get(models.User, student_id)
    if not student:
        return rf.res_404(message="请先设置党支部信息")
    #todo 再判断用户是否已经答过题

    return rf.res_200(message="项目详情获取成功", data=project_data)
    # return project


