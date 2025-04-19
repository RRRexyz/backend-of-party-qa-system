from fastapi import APIRouter, Depends, HTTPException, status
# from idna import valid_contextj
from sqlmodel import Session, select, func
import utils.schemas as schemas
from sql.database import get_session
from utils.authorization import *
from uuid import uuid1
import utils.response_format as rf
import ast
from datetime import datetime
from sqlalchemy.exc import IntegrityError


router = APIRouter()


def check_project_status(project_in_db, starttime, deadline, now_status, session):
    now_time = datetime.now()
    if now_time < starttime:
        truth_status = 0  # 未开始
    elif now_time > deadline:
        truth_status = 2  # 已结束
    else:
        truth_status = 1  # 进行中
    if truth_status != now_status:  # 状态发生变化，需要更新
        project_in_db.status = truth_status
        session.add(project_in_db)
        session.commit()
        session.refresh(project_in_db)


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
        issue_num=project.issue_num,
        starttime=project.starttime,
        deadline=project.deadline,
        status=project_status,
        creater_id=admin.id
    )
    try:
        session.add(project_for_db)
        session.commit()
        session.refresh(project_for_db)
    except IntegrityError:
        return rf.res_400(message="该期号项目已经存在")
    
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
    check_project_status(project, project.starttime, project.deadline, project.status, session)
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
    """前端把修改后的整个项目信息（不论单个字段是否做了更改）重新发一遍
    """
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
        issue_num=project.issue_num,
        starttime=project.starttime,
        deadline=project.deadline,
        status=project_status,
        creater_id=admin.id
    )
    try:
        session.add(project_for_db)
        session.commit()
        session.refresh(project_for_db)
    except IntegrityError:
        return rf.res_400(message="该期号项目已经存在")
    
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


@router.get("/admin/projects",
            summary="管理员获取其创建的所有项目列表")
async def get_projects(session: Session=Depends(get_session),
admin=Depends(admin_verify_token)):
    projects = session.exec(select(models.Project).filter_by(creater_id=admin.id)).all()
    projects_data = []
    for project in projects:
        check_project_status(project, project.starttime, project.deadline, project.status, session)
        project_data = {
            "project_uuid": project.uuid,
            "name": project.name,
            "issue_num": project.issue_num,
            "starttime": project.starttime.strftime("%Y-%m-%d %H:%M:%S"),
            "deadline": project.deadline.strftime("%Y-%m-%d %H:%M:%S"),
            "status": project.status,
            "participate_num": len(project.records),
        }
        projects_data.append(project_data)
    return rf.res_200(message="项目列表获取成功", data=projects_data)


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
async def user_get_project(project_uuid: str, 
student_id: str,
session: Session=Depends(get_session)):
    """如果用户没有答题记录，返回题目与答案；

    如果用户有答题记录，还会返回其作答情况；
    """
    #* 如果project_uuid为latest，则返回最新发布的项目
    if project_uuid == "latest":
        statement = select(func.max(models.Project.issue_num))
        max_issue_num = session.exec(statement).first()
        if not max_issue_num:
            return rf.res_404(message="不存在任何项目")
        project = session.exec(select(models.Project).filter_by(issue_num=max_issue_num)).first()
    
    #* 正常情况
    else:
        project = session.get(models.Project, project_uuid)
        if not project:
            return rf.res_404(message="项目不存在")
    project_uuid = project.uuid
    check_project_status(project, project.starttime, project.deadline, project.status, session)
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
    record = session.exec(select(models.Record).filter_by(student_id=student_id, project_uuid=project_uuid)).first()
    if record: #. 用户已经答过题，还要返回其作答情况
        project_data["participate_status"] = 1  # 答题参与状态，0为尚未参与，1为已参与
        project_data["record"] = ast.literal_eval(record.answer)
        project_data["correct_num"] = record.correct_num
        project_data["time_used_seconds"] = record.time_used_seconds
    else: #. 用户还没有答过题，只返回题目与答案
        project_data["participate_status"] = 0  # 答题参与状态，0为尚未参与，1为已参与
    return rf.res_200(message="项目详情获取成功", data=project_data)
    # return project


@router.post("/user/project",
            summary="用户提交答案")
async def commit_answer(commit_data: schemas.CommitAnswerRequest, 
session: Session=Depends(get_session)):
    project = session.get(models.Project, commit_data.project_uuid)
    if not project:
        return rf.res_404(message="项目不存在")
    student = session.get(models.User, commit_data.student_id)
    if not student:
        return rf.res_404(message="请先设置党支部信息")
    record = session.exec(select(models.Record).filter_by(student_id=commit_data.student_id, project_uuid=commit_data.project_uuid)).first()
    if record:
        return rf.res_400(message="已经有答题记录，无法再次提交")
    answers = []
    for a in commit_data.user_answers:
        answers.append(a.model_dump())
    answer_data = str(answers)
    if project.status == 2: # 作答已经结束的项目，不参与排位
        valid_flag = False
    else:
        valid_flag = True
    record_for_db = models.Record(
        student_id=commit_data.student_id,
        project_uuid=commit_data.project_uuid,
        correct_num=commit_data.correct_num,
        time_used_seconds=commit_data.time_used_seconds,
        answer=answer_data,
        valid_flag=valid_flag
    )
    session.add(record_for_db)
    session.commit()
    session.refresh(record_for_db)
    # 项目参与人数+1
    project.participate_num += 1
    session.add(project)
    session.commit()
    session.refresh(project)
    return rf.res_201(message="答案提交成功")


@router.get("/user/projects/all",
            summary="用户获取所有已开始的项目列表")
async def user_get_all_projects(session: Session=Depends(get_session)):
    projects = session.exec(select(models.Project).where(models.Project.status>0)).all()
    projects_data = []
    for project in projects:
        check_project_status(project, project.starttime, project.deadline, project.status, session)
        project_data = {
            "project_uuid": project.uuid,
            "name": project.name,
            "issue_num": project.issue_num,
            "starttime": project.starttime.strftime("%Y-%m-%d %H:%M:%S"),
            "deadline": project.deadline.strftime("%Y-%m-%d %H:%M:%S"),
            "status": project.status,
            "participate_num": len(project.records),
            "creater_username": project.creater.username
        }
        projects_data.append(project_data)
    return rf.res_200(message="项目列表获取成功", data=projects_data)


@router.get("/user/projects",
            summary="用户获取参与过的所有项目预览")
async def user_get_projects(student_id: str, 
session: Session=Depends(get_session)):
    student = session.get(models.User, student_id)
    if not student:
        return rf.res_404(message="请先设置党支部信息")
    records = session.exec(select(models.Record).filter_by(student_id=student_id)).all()
    projects = []
    for record in records:
        project = {
            "project_uuid": record.project_uuid,
            "name": record.project.name,
            "issue_num": record.project.issue_num,
            "starttime": record.project.starttime.strftime("%Y-%m-%d %H:%M:%S"),
            "deadline": record.project.deadline.strftime("%Y-%m-%d %H:%M:%S"),
            "status": record.project.status,
            "correct_num": record.correct_num,
            "time_used_seconds": record.time_used_seconds,
            "creater_username": record.project.creater.username
        }
        projects.append(project)
    return rf.res_200(message="项目列表获取成功", data=projects)