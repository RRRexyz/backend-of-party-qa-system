from fastapi import FastAPI
from sql.database import create_db_and_tables
from routers import user, qa, ranking, sdulogin
from fastapi.middleware.cors import CORSMiddleware


tags_metadata = [
    {
        "name": "用户模块",
        "description": "用户更改党支部信息、查看个人历史成绩。"
    },
    {
        "name": "问答模块",
        "description": "官方发布题目、用户参与答题。"
    },
    {
        "name": "排位模块",
        "description": "生成当期与往期排行榜。"
    }
]


app = FastAPI(title="党建问答系统", version="0.1.0", 
            openapi_tags=tags_metadata)


app.include_router(user.router, tags=["用户模块"], prefix="/api")
app.include_router(qa.router, tags=["问答模块"], prefix="/api")
app.include_router(ranking.router, tags=["排位模块"], prefix="/api")
app.include_router(sdulogin.router, tags=["用户模块"], prefix="/api")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_db_and_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
    