# from fastapi import FastAPI
# from .routers import users, posts, comments
# # from . import models, database
# models.Base.metadata.create_all(bind=database.engine)

# app = FastAPI()
#
# app.include_router(users.router)
# app.include_router(posts.router)
# app.include_router(comments.router)


import uvicorn as uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from mangum import Mangum
from routers import users_controller, posts_controller, comments_controller
# from config.setting import settings
import models, database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="API SIMPLE BLOG",
              description="Simple Blog",
              version="1.0.0",
              # root_path=settings.root_path,
              debug=True)
handler = Mangum(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
def validation_exception_handler(request, err):
    base_error_message = f"Failed to execute: {request.method}: {request.url}"
    return JSONResponse(status_code=400, content={"message": f"{base_error_message}. Detail: {err}"})


app.include_router(users_controller.router)
app.include_router(posts_controller.router)
app.include_router(comments_controller.router)

if __name__ == "__main__":
    uvicorn.run("main:app",
                host='0.0.0.0',
                port=8000, reload=True)
