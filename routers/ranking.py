from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from sql.database import get_session
import sql.models as models
import utils.response_format as rf


router = APIRouter()


@router.get("/ranking",
            summary="获取当期排行榜")
async def get_ranking(student_id: str, session: Session=Depends(get_session)):
    statement = select(func.max(models.Project.issue_num))
    max_issue_num = session.exec(statement).first()
    if not max_issue_num:
        return rf.res_404(message="不存在任何项目")
    project = session.exec(select(models.Project).filter_by(issue_num=max_issue_num)).first()
    # print(max_issue_num)
    # print(project.records)
    ranking = []
    for record in project.records:
        if record.valid_flag: # 将有效作答的记录加入排行榜
            record_data = {
                "student_id": record.student_id,
                "name": record.student.name,
                "party_branch": record.student.party_branch,
                "correct_num": record.correct_num,
                "time_used_seconds": record.time_used_seconds,
            }
            ranking.append(record_data)
    ranking.sort(key=lambda x: (-x["correct_num"], x["time_used_seconds"]))
    self_ranking = {}
    for (i, student) in enumerate(ranking):
        student["rank"] = i + 1
        if student["student_id"] == student_id:
            self_ranking = student
    now_ranking_data = {
        "project_uuid": project.uuid,
        "project_name": project.name,
        "creater_name": project.creater.username,
        "issue_num": project.issue_num,
        "self_ranking": self_ranking,
        "ranking": ranking[:30]
    }
    return rf.res_200(message="获取当期排行榜成功", data=now_ranking_data)


@router.get("/ranking/all",
            summary="获取往期累计排行榜")
async def get_all_ranking(student_id: str, session: Session=Depends(get_session)):
    # 获取所有用户
    users = session.exec(select(models.User)).all()
    ranking = []
    for user in users:
        # 统计每个用户的总成绩
        user_total_correct_num = 0
        user_total_time_used_seconds = 0
        for record in user.records:
            if record.valid_flag: # 将有效作答的记录加入排行榜
                user_total_correct_num += record.correct_num
                user_total_time_used_seconds += record.time_used_seconds
        record_num = len(user.records)
        if record_num > 0:
            user_average_time_used_seconds = user_total_time_used_seconds / record_num
        else:
            user_average_time_used_seconds = 0
        user_data = {
            "student_id": user.student_id,
            "name": user.name,
            "party_branch": user.party_branch,
            "total_correct_num": user_total_correct_num,
            "average_time_used_seconds": user_average_time_used_seconds
        }
        ranking.append(user_data)
    ranking.sort(key=lambda x: (-x["total_correct_num"], x["average_time_used_seconds"]))
    self_ranking = {}
    for (i, student) in enumerate(ranking):
        student["rank"] = i + 1
        if student["student_id"] == student_id:
            self_ranking = student
    all_ranking_data = {
        "self_ranking": self_ranking,
        "ranking": ranking[:30]
    }
    return rf.res_200(message="获取往期累计排行榜成功", data=all_ranking_data)