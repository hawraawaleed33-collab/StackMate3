from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
from email.message import EmailMessage

import certifi
import shutil
import subprocess
import uuid
import random
import smtplib
import os
import re

import cloudinary
import cloudinary.uploader

app = FastAPI()

cloudinary.config(
    cloud_name="drjpfr75p",
    api_key="318563638924659",
    api_secret="tycwgqDQV70EqM-xuHw_DfA7OrE"
)
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(
            file.file,
            resource_type="image",
            folder="stackmate/images"
        )
        return {"url": result["secure_url"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-video")
async def upload_video_to_cloud(file: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(
            file.file,
            resource_type="video",
            folder="stackmate/videos"
        )
        return {"url": result["secure_url"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ===============================
# MongoDB Connection
# ===============================
uri = "mongodb+srv://hawraawaleed33_db_user:k0c6YSVbOChqqyOn@cluster0.qk8xvxh.mongodb.net/test?retryWrites=true&w=majority"

client = MongoClient(
    uri,
    tls=True,
    tlsAllowInvalidCertificates=True,
    tlsCAFile=certifi.where()
)

db = client["test"]

developers_collection = db["developers"]
projects_collection = db["projects"]
videos_collection = db["videos"]
follows_collection = db["follows"]
accounts_collection = db["accounts"]
reset_codes_collection = db["reset_codes"]
notifications_collection = db["notifications"]

video_likes_collection = db["video_likes"]
video_dislikes_collection = db["video_dislikes"]
video_saves_collection = db["video_saves"]

# ===============================
# Chat Collections
# ===============================
conversations_collection = db["conversations"]
messages_collection = db["messages"]

# ===============================
# AI Chat Collections
# ===============================
ai_conversations_collection = db["ai_conversations"]
ai_messages_collection = db["ai_messages"]
# ===============================
# Groups Collections
# ===============================
groups_collection = db["groups"]
group_messages_collection = db["group_messages"]

# ===============================
# Channel Collections
# ===============================
channels_collection = db["channels"]
channel_messages_collection = db["channel_messages"]
channel_followers_collection = db["channel_followers"]
# ===============================
# Static Files
# ===============================
os.makedirs("videos", exist_ok=True)
os.makedirs("thumbnails", exist_ok=True)

app.mount("/media/videos", StaticFiles(directory="videos"), name="media_videos")
app.mount("/thumbnails", StaticFiles(directory="thumbnails"), name="thumbnails")

URL_BASE = "https://stackmate4.onrender.com"

# ===============================
# Email / SMTP Config
# ===============================
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "hawraamohsen58@gmail.com"
SMTP_PASS = "zqwqatvyydikoajm"
SMTP_FROM_EMAIL = SMTP_USER
# ===============================
# Models
# ===============================

class Developer(BaseModel):
    name: str
    skill: str
    bio: str
    avatar: str = ""
    job: str = ""
    location: str = ""
    experience: str = ""
    technologies: str = ""
    portfolio: str = ""


class Project(BaseModel):
    developer_id: str
    title: str
    description: str
    url: str
    technologies: str = ""
    image: str = ""
    status: str = "successful"
    tips: str = ""


class Video(BaseModel):
    developer_id: str
    title: str
    description: str = ""
    url: str = ""
    url_480: str = ""
    url_720: str = ""
    url_1080: str = ""
    thumbnail: str = ""
    views: int = 0


class Follow(BaseModel):
    follower: str
    following: str
    status: str = "accepted"


class FollowToggleRequest(BaseModel):
    follower_id: str
    following_id: str


class NotificationCreate(BaseModel):
    receiver_id: str
    sender_id: str
    sender_name: str = ""
    sender_image: str = ""
    sender_account_type: str = ""
    title: str = ""
    message: str
    type: str = "follow"


class Account(BaseModel):
    email: str
    username: str
    password: str
    account_type: str  # developer or user (user = student)

    name: str = ""
    description: str = ""
    profile_image: str = ""
    phone: str = ""

    job: str = ""
    location: str = ""
    experience: str = ""
    skills: str = ""
    technologies: str = ""
    portfolio: str = ""

    # Student Fields
    student_id: str = ""
    university_name: str = ""
    college_name: str = ""
    department_name: str = ""


class LoginData(BaseModel):
    email: str
    password: str


# ===============================
# AI Chat Models (NEW)
# ===============================
class AIMessageRequest(BaseModel):
    user_id: str
    prompt: str
    conversation_id: str = ""


class AIConversationCreate(BaseModel):
    user_id: str
class UpdateUserProfile(BaseModel):
    name: str = ""
    username: str = ""
    email: str = ""
    description: str = ""
    profile_image: str = ""

    job: str = ""
    location: str = ""
    experience: str = ""
    skills: str = ""
    technologies: str = ""
    portfolio: str = ""

    # ✅ Student Fields (مهم)
    student_id: str = ""
    university_name: str = ""
    college_name: str = ""
    department_name: str = ""


class ForgotPasswordRequest(BaseModel):
    email_or_phone: str


class VerifyResetCodeRequest(BaseModel):
    email_or_phone: str
    code: str


class ResetPasswordRequest(BaseModel):
    email_or_phone: str
    code: str
    new_password: str
# ===============================
# Chat Models
# ===============================
class ConversationCreate(BaseModel):
    sender_id: str
    receiver_id: str


class MessageCreate(BaseModel):
    conversation_id: str
    sender_id: str
    receiver_id: str

    text: str | None = None
    message_type: str = "text"   # text | image | video
    media_url: str | None = None


# ===============================
# Group Models
# ===============================
class GroupCreate(BaseModel):
    creator_id: str
    name: str
    member_ids: list[str]


class GroupMessageCreate(BaseModel):
    group_id: str
    sender_id: str

    text: str | None = None
    message_type: str = "text"   # text | image | video
    media_url: str | None = None
# ===============================
# Channel Models
# ===============================
class ChannelCreate(BaseModel):
    owner_id: str
    name: str
    description: str = ""
    image: str = ""
    is_public: bool = True


class ChannelMessageCreate(BaseModel):
    channel_id: str
    sender_id: str
    text: str | None = None
    message_type: str = "text"   # text | image | video
    media_url: str | None = None


class ChannelFollowToggle(BaseModel):
    user_id: str
    channel_id: str
# ===============================
# Video Interactions Models
# ===============================
class VideoLike(BaseModel):
    user_id: str
    video_id: str


class VideoDislike(BaseModel):
    user_id: str
    video_id: str


class VideoSave(BaseModel):
    user_id: str
    video_id: str
# ===============================
# Helper
# ===============================
def safe_object_id(value: str):
    try:
        return ObjectId(value)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")


def generate_otp():
    return f"{random.randint(100000, 999999)}"


def send_email_code(to_email: str, code: str):
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS or not SMTP_FROM_EMAIL:
        return False
    try:
        msg = EmailMessage()
        msg["Subject"] = "StackMate Password Reset Code"
        msg["From"] = SMTP_FROM_EMAIL
        msg["To"] = to_email
        msg.set_content(
            f"Your StackMate verification code is: {code}\n\n"
            f"This code will expire in 10 minutes."
        )

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        return True
    except Exception as e:
        print("Email sending error:", str(e))
        return False


def find_account_by_identifier(identifier: str):
    return accounts_collection.find_one({
        "$or": [
            {"email": identifier},
            {"phone": identifier}
        ]
    })


# ===============================
# Root
# ===============================
@app.get("/")
def home():
    return {"message": "Server is running ✅"}


@app.get("/health")
def health():
    return {"message": "Server is running ✅"}


@app.get("/db-check")
def db_check():
    try:
        client.admin.command("ping")
        return {"message": "Database connected successfully ✅"}
    except Exception as e:
        return {"error": str(e)}

# ===============================
# Auth / Accounts
# ===============================

@app.post("/signup")
def signup(account: Account):
    account_type = account.account_type.lower().strip()

    # فقط developer أو user (user = student)
    if account_type not in ["developer", "user"]:
        raise HTTPException(status_code=400, detail="Invalid account type")

    existing = accounts_collection.find_one({
        "$or": [
            {"email": account.email},
            {"username": account.username}
        ]
    })

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email or username already exists"
        )

    # إذا الحساب user نعتبره student ولازم بياناته الجامعية كاملة
    if account_type == "user":
        if (
            not account.student_id
            or not account.university_name
            or not account.college_name
            or not account.department_name
        ):
            raise HTTPException(
                status_code=400,
                detail="Student information is required"
            )

        if not re.fullmatch(r"\d{3}", account.student_id.strip()):
            raise HTTPException(
                status_code=400,
                detail="Student ID must be exactly 3 digits"
            )

    account_data = account.dict()
    account_data["account_type"] = account_type

    # Admin / Moderation Fields
    account_data["is_admin"] = False
    account_data["is_blocked"] = False
    account_data["is_verified_developer"] = False

    result = accounts_collection.insert_one(account_data)
    account_id = str(result.inserted_id)

    if account_type == "developer":
        developers_collection.insert_one({
            "account_id": account_id,
            "name": account.username,
            "skill": account.skills,
            "bio": account.description,
            "avatar": account.profile_image,
            "job": account.job,
            "location": account.location,
            "experience": account.experience,
            "technologies": account.technologies,
            "portfolio": account.portfolio
        })

    return {
        "message": "Account created successfully",
        "id": account_id,
        "account_type": account_type
    }


@app.post("/login")
def login(data: LoginData):
    account = accounts_collection.find_one({
        "email": data.email,
        "password": data.password
    })

    if not account:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if account.get("is_blocked", False):
        raise HTTPException(status_code=403, detail="Your account is blocked")

    return {
        "message": "Login successful",
        "id": str(account["_id"]),
        "email": account.get("email", ""),
        "username": account.get("username", ""),
        "account_type": account.get("account_type", ""),
        "name": account.get("name", ""),
        "description": account.get("description", ""),
        "profile_image": account.get("profile_image", ""),
        "job": account.get("job", ""),
        "location": account.get("location", ""),
        "experience": account.get("experience", ""),
        "skills": account.get("skills", ""),
        "technologies": account.get("technologies", ""),
        "portfolio": account.get("portfolio", ""),

        # Student fields
        "student_id": account.get("student_id", ""),
        "university_name": account.get("university_name", ""),
        "college_name": account.get("college_name", ""),
        "department_name": account.get("department_name", ""),

        # Admin / Moderation fields
        "is_admin": account.get("is_admin", False),
        "is_blocked": account.get("is_blocked", False),
        "is_verified_developer": account.get("is_verified_developer", False)
    }


@app.get("/accounts/{account_id}")
def get_account(account_id: str):
    account = accounts_collection.find_one({"_id": safe_object_id(account_id)})

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {
        "id": str(account["_id"]),
        "email": account.get("email", ""),
        "username": account.get("username", ""),
        "account_type": account.get("account_type", ""),
        "name": account.get("name", ""),
        "description": account.get("description", ""),
        "profile_image": account.get("profile_image", ""),
        "job": account.get("job", ""),
        "location": account.get("location", ""),
        "experience": account.get("experience", ""),
        "skills": account.get("skills", ""),
        "technologies": account.get("technologies", ""),
        "portfolio": account.get("portfolio", ""),

        # Student fields
        "student_id": account.get("student_id", ""),
        "university_name": account.get("university_name", ""),
        "college_name": account.get("college_name", ""),
        "department_name": account.get("department_name", ""),

        # Admin / Moderation fields
        "is_admin": account.get("is_admin", False),
        "is_blocked": account.get("is_blocked", False),
        "is_verified_developer": account.get("is_verified_developer", False)
    }


@app.put("/accounts/{account_id}/profile")
def update_user_profile(account_id: str, profile: UpdateUserProfile):
    existing = accounts_collection.find_one({"_id": safe_object_id(account_id)})

    if not existing:
        raise HTTPException(status_code=404, detail="Account not found")

    update_data = {
        "name": profile.name,
        "username": profile.username,
        "email": profile.email,
        "description": profile.description,
        "profile_image": profile.profile_image,
        "job": profile.job,
        "location": profile.location,
        "experience": profile.experience,
        "skills": profile.skills,
        "technologies": profile.technologies,
        "portfolio": profile.portfolio,

        # Student Fields
        "student_id": profile.student_id,
        "university_name": profile.university_name,
        "college_name": profile.college_name,
        "department_name": profile.department_name,
    }

    accounts_collection.update_one(
        {"_id": safe_object_id(account_id)},
        {"$set": update_data}
    )

    if existing.get("account_type") == "developer":
        developers_collection.update_one(
            {"account_id": account_id},
            {
                "$set": {
                    "account_id": account_id,
                    "name": profile.name,
                    "skill": profile.skills,
                    "bio": profile.description,
                    "avatar": profile.profile_image,
                    "job": profile.job,
                    "location": profile.location,
                    "experience": profile.experience,
                    "technologies": profile.technologies,
                    "portfolio": profile.portfolio
                }
            },
            upsert=True
        )

    return {"message": "Profile updated successfully"}
# ===============================
# Forgot Password / Verify / Reset
# ===============================
@app.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    identifier = data.email_or_phone.strip()

    if not identifier:
        raise HTTPException(status_code=400, detail="Email or phone is required")

    account = find_account_by_identifier(identifier)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    reset_codes_collection.update_many(
        {
            "account_id": str(account["_id"]),
            "used": False
        },
        {
            "$set": {"used": True}
        }
    )

    reset_codes_collection.insert_one({
        "account_id": str(account["_id"]),
        "email_or_phone": identifier,
        "code": code,
        "used": False,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at
    })

    account_email = account.get("email", "")

    if account_email:
        email_sent = send_email_code(account_email, code)

        if email_sent:
            return {
                "message": "Verification code sent successfully"
            }

        # للتجربة إذا SMTP مو مضبوط
        return {
            "message": "Verification code generated successfully (SMTP not configured)",
            "debug_code": code
        }

    raise HTTPException(
        status_code=400,
        detail="This account does not have a valid email for code delivery"
    )
@app.post("/verify-reset-code")
def verify_reset_code(data: VerifyResetCodeRequest):
    identifier = data.email_or_phone.strip()
    code = data.code.strip()

    if not identifier or not code:
        raise HTTPException(status_code=400, detail="Missing data")

    account = find_account_by_identifier(identifier)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    reset_record = reset_codes_collection.find_one({
        "account_id": str(account["_id"]),
        "email_or_phone": identifier,
        "code": code,
        "used": False
    })

    if not reset_record:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    expires_at = reset_record.get("expires_at")
    if expires_at and datetime.utcnow() > expires_at:
        raise HTTPException(status_code=400, detail="Verification code has expired")

    return {"message": "Code verified successfully"}


@app.post("/reset-password")
def reset_password(data: ResetPasswordRequest):
    identifier = data.email_or_phone.strip()
    code = data.code.strip()
    new_password = data.new_password.strip()

    if not identifier or not code or not new_password:
        raise HTTPException(status_code=400, detail="Missing data")

    if len(new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters"
        )

    account = find_account_by_identifier(identifier)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    reset_record = reset_codes_collection.find_one({
        "account_id": str(account["_id"]),
        "email_or_phone": identifier,
        "code": code,
        "used": False
    })

    if not reset_record:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    expires_at = reset_record.get("expires_at")
    if expires_at and datetime.utcnow() > expires_at:
        raise HTTPException(status_code=400, detail="Verification code has expired")

    accounts_collection.update_one(
        {"_id": account["_id"]},
        {"$set": {"password": new_password}}
    )

    reset_codes_collection.update_one(
        {"_id": reset_record["_id"]},
        {"$set": {"used": True}}
    )

    return {"message": "Password reset successfully"}


# ===============================
# Developers
# ===============================

@app.post("/developers")
def add_developer(dev: Developer):
    developers_collection.insert_one({
        "account_id": "",
        "name": dev.name,
        "skill": dev.skill,
        "bio": dev.bio,
        "avatar": dev.avatar,
        "job": dev.job,
        "location": dev.location,
        "experience": dev.experience,
        "technologies": dev.technologies,
        "portfolio": dev.portfolio
    })
    return {"message": "Developer added"}


@app.get("/developers")
def get_developers():
    developers = developers_collection.find()
    result = []

    for dev in developers:
        account_id = dev.get("account_id", "")

        followers_count = follows_collection.count_documents({
            "following": account_id,
            "status": "accepted"
        })

        result.append({
            "id": str(dev["_id"]),
            "account_id": account_id,
            "name": dev.get("name", ""),
            "skill": dev.get("skill", ""),
            "bio": dev.get("bio", ""),
            "avatar": dev.get("avatar", ""),
            "job": dev.get("job", ""),
            "location": dev.get("location", ""),
            "experience": dev.get("experience", ""),
            "technologies": dev.get("technologies", ""),
            "portfolio": dev.get("portfolio", ""),
            "followers_count": followers_count
        })

    return result


@app.get("/developers/search")
def search_developers(q: str):
    developers = developers_collection.find({
        "$or": [
            {"name": {"$regex": q, "$options": "i"}},
            {"skill": {"$regex": q, "$options": "i"}}
        ]
    })

    result = []
    for dev in developers:
        account_id = dev.get("account_id", "")

        followers_count = follows_collection.count_documents({
            "following": account_id,
            "status": "accepted"
        })

        result.append({
            "id": str(dev["_id"]),
            "account_id": account_id,
            "name": dev.get("name", ""),
            "skill": dev.get("skill", ""),
            "bio": dev.get("bio", ""),
            "avatar": dev.get("avatar", ""),
            "job": dev.get("job", ""),
            "location": dev.get("location", ""),
            "experience": dev.get("experience", ""),
            "technologies": dev.get("technologies", ""),
            "portfolio": dev.get("portfolio", ""),
            "followers_count": followers_count
        })

    return result


@app.get("/developers/{developer_id}")
def get_developer(developer_id: str):
    dev = developers_collection.find_one({"_id": safe_object_id(developer_id)})
    if not dev:
        raise HTTPException(status_code=404, detail="Developer not found")

    account_id = dev.get("account_id", "")

    followers_count = follows_collection.count_documents({
        "following": account_id,
        "status": "accepted"
    })

    following_count = follows_collection.count_documents({
        "follower": account_id,
        "status": "accepted"
    })

    return {
        "id": str(dev["_id"]),
        "account_id": account_id,
        "name": dev.get("name", ""),
        "job": dev.get("job", ""),
        "location": dev.get("location", ""),
        "experience": dev.get("experience", ""),
        "skill": dev.get("skill", ""),
        "technologies": dev.get("technologies", ""),
        "portfolio": dev.get("portfolio", ""),
        "bio": dev.get("bio", ""),
        "avatar": dev.get("avatar", ""),
        "followers_count": followers_count,
        "following_count": following_count
    }
# ===============================
# Projects
# ===============================
@app.post("/projects")
def add_project(project: Project):
    projects_collection.insert_one(project.dict())
    return {"message": "Project added"}


@app.get("/developers/{developer_id}/projects")
def get_projects(developer_id: str):
    projects = list(projects_collection.find({"developer_id": developer_id}))

    return [
        {
            "id": str(p["_id"]),
            "title": p.get("title", ""),
            "description": p.get("description", ""),
            "url": p.get("url", ""),
            "technologies": p.get("technologies", ""),
            "image": p.get("image", ""),
            "status": p.get("status", "successful"),
            "tips": p.get("tips", "")
        }
        for p in projects
    ]


# ===============================
# Videos
# ===============================
@app.post("/videos")
def add_video(video: Video):
    videos_collection.insert_one(video.dict())
    return {"message": "Video added"}


@app.post("/videos/upload")
def upload_video(
    title: str = Form(...),
    description: str = Form(""),
    developer_id: str = Form(...),
    file: UploadFile = File(...),
    thumbnail: UploadFile = File(None)
):
    dev = developers_collection.find_one({"account_id": developer_id})
    if not dev:
        raise HTTPException(status_code=404, detail="Developer not found")

    try:
        video_result = cloudinary.uploader.upload(
            file.file,
            resource_type="video",
            folder="stackmate/videos"
        )

        thumbnail_url = ""
        if thumbnail:
            thumbnail_result = cloudinary.uploader.upload(
                thumbnail.file,
                resource_type="image",
                folder="stackmate/thumbnails"
            )
            thumbnail_url = thumbnail_result.get("secure_url", "")

        videos_collection.insert_one({
            "developer_id": str(dev["_id"]),
            "title": title,
            "description": description,
            "url": video_result.get("secure_url", ""),
            "thumbnail": thumbnail_url,
            "views": 0
        })

        return {"message": "Video uploaded successfully ✅"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/developers/{developer_id}/videos")
def get_videos(developer_id: str):
    videos = list(videos_collection.find({"developer_id": developer_id}))
    result = []
    dev = developers_collection.find_one({"_id": safe_object_id(developer_id)})

    for v in videos:
        result.append({
            "id": str(v["_id"]),
            "developer_id": v.get("developer_id", ""),
            "title": v.get("title", ""),
            "description": v.get("description", ""),
            "url": v.get("url", ""),
            "thumbnail": v.get("thumbnail", ""),
            "developer_name": dev.get("name", "") if dev else "",
            "developer_avatar": dev.get("avatar", "") if dev else "",
            "views": v.get("views", 0)
        })

    return result


@app.get("/videos/search")
def search_videos(q: str):
    videos = list(videos_collection.find({
        "title": {"$regex": q, "$options": "i"}
    }))

    result = []

    for v in videos:
        developer_id = v.get("developer_id", "")
        dev = None

        if developer_id:
            try:
                dev = developers_collection.find_one({"_id": safe_object_id(developer_id)})
            except Exception:
                dev = None

        result.append({
            "id": str(v["_id"]),
            "developer_id": developer_id,
            "title": v.get("title", ""),
            "description": v.get("description", ""),
            "url": v.get("url", ""),
            "thumbnail": v.get("thumbnail", ""),
            "developer_name": dev.get("name", "") if dev else "",
            "developer_avatar": dev.get("avatar", "") if dev else "",
            "views": v.get("views", 0)
        })

    return result
@app.get("/videos/{video_id}")
def get_video_by_id(video_id: str):
    video = videos_collection.find_one({"_id": safe_object_id(video_id)})

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    developer_id = video.get("developer_id", "")
    dev = None

    if developer_id:
        try:
            dev = developers_collection.find_one(
                {"_id": safe_object_id(developer_id)}
            )
        except Exception:
            dev = None

    return {
        "id": str(video["_id"]),
        "developer_id": developer_id,
        "title": video.get("title", ""),
        "description": video.get("description", ""),
        "url": video.get("url", ""),
        "thumbnail": video.get("thumbnail", ""),
        "developer_name": dev.get("name", "") if dev else "",
        "developer_avatar": dev.get("avatar", "") if dev else "",
        "views": video.get("views", 0)
    }


@app.delete("/videos/{video_id}")
def delete_video(video_id: str):
    result = videos_collection.delete_one({"_id": safe_object_id(video_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Video not found")

    return {"message": "Video deleted"}
# ===============================
# Follow
# ===============================

@app.post("/follow")
def follow_user(follow: Follow):
    if follow.follower == follow.following:
        raise HTTPException(status_code=400, detail="You cannot follow yourself")

    existing = follows_collection.find_one({
        "follower": follow.follower,
        "following": follow.following,
        "status": "accepted"
    })

    if existing:
        return {"message": "Already following"}

    follows_collection.insert_one({
        "follower": follow.follower,
        "following": follow.following,
        "status": "accepted",
        "created_at": datetime.utcnow()
    })

    return {"message": "Followed successfully"}


@app.delete("/follow")
def unfollow_user(follower: str, following: str):
    result = follows_collection.delete_one({
        "follower": follower,
        "following": following,
        "status": "accepted"
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not following")

    return {"message": "Unfollowed successfully"}


@app.get("/follow")
def get_follow():
    follows = follows_collection.find()
    result = []

    for f in follows:
        result.append({
            "id": str(f["_id"]),
            "follower": f.get("follower", ""),
            "following": f.get("following", ""),
            "status": f.get("status", "accepted")
        })

    return result


@app.get("/follow/check")
def check_follow(follower: str, following: str):
    existing = follows_collection.find_one({
        "follower": follower,
        "following": following,
        "status": "accepted"
    })

    return {
        "is_following": True if existing else False
    }


@app.get("/follow/counts/{account_id}")
def get_follow_counts(account_id: str):
    followers_count = follows_collection.count_documents({
        "following": account_id,
        "status": "accepted"
    })

    following_count = follows_collection.count_documents({
        "follower": account_id,
        "status": "accepted"
    })

    return {
        "followers_count": followers_count,
        "following_count": following_count
    }


@app.get("/followers/{account_id}")
def get_followers(account_id: str):
    follows = follows_collection.find({
        "following": account_id,
        "status": "accepted"
    })

    result = []
    for f in follows:
        acc = accounts_collection.find_one({"_id": safe_object_id(f["follower"])})
        if acc:
            result.append({
                "id": str(acc["_id"]),
                "username": acc.get("username", ""),
                "name": acc.get("name", ""),
                "profile_image": acc.get("profile_image", "")
            })

    return result


@app.get("/following/{account_id}")
def get_following(account_id: str):
    follows = follows_collection.find({
        "follower": account_id,
        "status": "accepted"
    })

    result = []
    for f in follows:
        acc = accounts_collection.find_one({"_id": safe_object_id(f["following"])})
        if acc:
            result.append({
                "id": str(acc["_id"]),
                "username": acc.get("username", ""),
                "name": acc.get("name", ""),
                "profile_image": acc.get("profile_image", "")
            })

    return result


@app.get("/follow/status/{follower_id}/{following_id}")
def get_follow_status(follower_id: str, following_id: str):
    existing = follows_collection.find_one({
        "follower": follower_id,
        "following": following_id,
        "status": "accepted"
    })

    return {"followed": True if existing else False}


@app.post("/follow/toggle")
def toggle_follow(data: FollowToggleRequest):
    if data.follower_id == data.following_id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself")

    existing = follows_collection.find_one({
        "follower": data.follower_id,
        "following": data.following_id,
        "status": "accepted"
    })
    if existing:
        follows_collection.delete_one({
            "_id": existing["_id"]
        })
        return {
            "message": "Unfollowed successfully",
            "followed": False
        }

    follows_collection.insert_one({
        "follower": data.follower_id,
        "following": data.following_id,
        "status": "accepted",
        "created_at": datetime.utcnow()
    })

    return {
        "message": "Followed successfully",
        "followed": True
    }


@app.get("/follow/followers/{account_id}")
def get_followers_new(account_id: str):
    follows = follows_collection.find({
        "following": account_id,
        "status": "accepted"
    })

    result = []
    for f in follows:
        acc = accounts_collection.find_one({"_id": safe_object_id(f["follower"])})
        if acc:
            developer_profile_id = ""

            if acc.get("account_type") == "developer":
                dev = developers_collection.find_one({
                    "account_id": str(acc["_id"])
                })
                if dev:
                    developer_profile_id = str(dev["_id"])

            result.append({
                "id": str(acc["_id"]),
                "username": acc.get("username", ""),
                "name": acc.get("name", ""),
                "profile_image": acc.get("profile_image", ""),
                "account_type": acc.get("account_type", ""),
                "developer_profile_id": developer_profile_id
            })

    return result


@app.get("/follow/following/{account_id}")
def get_following_new(account_id: str):
    follows = follows_collection.find({
        "follower": account_id,
        "status": "accepted"
    })

    result = []
    for f in follows:
        acc = accounts_collection.find_one({"_id": safe_object_id(f["following"])})
        if acc:
            developer_profile_id = ""

            if acc.get("account_type") == "developer":
                dev = developers_collection.find_one({
                    "account_id": str(acc["_id"])
                })
                if dev:
                    developer_profile_id = str(dev["_id"])

            result.append({
                "id": str(acc["_id"]),
                "username": acc.get("username", ""),
                "name": acc.get("name", ""),
                "profile_image": acc.get("profile_image", ""),
                "account_type": acc.get("account_type", ""),
                "developer_profile_id": developer_profile_id
            })

    return result


@app.post("/notifications/follow")
def create_follow_notification(data: NotificationCreate):
    notifications_collection.insert_one({
        "receiver_id": data.receiver_id,
        "sender_id": data.sender_id,
        "sender_name": data.sender_name,
        "sender_image": data.sender_image,
        "sender_account_type": data.sender_account_type,
        "title": data.title,
        "message": data.message,
        "type": data.type,
        "is_read": False,
        "created_at": datetime.utcnow()
    })

    return {"message": "Notification created successfully"}


@app.get("/notifications/{user_id}")
def get_notifications(user_id: str):
    notifications = notifications_collection.find({
        "receiver_id": user_id
    }).sort("created_at", -1)

    result = []
    for n in notifications:
        result.append({
            "id": str(n["_id"]),
            "receiver_id": n.get("receiver_id", ""),
            "sender_id": n.get("sender_id", ""),
            "sender_name": n.get("sender_name", ""),
            "sender_image": n.get("sender_image", ""),
            "sender_account_type": n.get("sender_account_type", ""),
            "title": n.get("title", ""),
            "message": n.get("message", ""),
            "type": n.get("type", ""),
            "is_read": n.get("is_read", False),
            "created_at": str(n.get("created_at", ""))
        })

    return result
# ===============================
# TEST FFMPEG
# ===============================
@app.get("/ffmpeg-check")
def ffmpeg_check():
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True
        )
        return {
            "message": "ffmpeg installed ✅",
            "output": result.stdout[:200]
        }
    except Exception as e:
        return {"error": str(e)}# ===============================
# Chat
# ===============================

@app.post("/chat/conversation")
def create_or_get_conversation(data: ConversationCreate):
    if data.sender_id == data.receiver_id:
        raise HTTPException(status_code=400, detail="You cannot chat with yourself")

    sender = accounts_collection.find_one({"_id": safe_object_id(data.sender_id)})
    receiver = accounts_collection.find_one({"_id": safe_object_id(data.receiver_id)})

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="Sender or receiver not found")

    existing_conversation = conversations_collection.find_one({
        "participants": {"$all": [data.sender_id, data.receiver_id]},
        "$expr": {"$eq": [{"$size": "$participants"}, 2]}
    })

    if existing_conversation:
        return {
            "message": "Conversation already exists",
            "conversation_id": str(existing_conversation["_id"])
        }

    now = datetime.utcnow()

    conversation_data = {
        "participants": [data.sender_id, data.receiver_id],
        "last_message": "",
        "last_message_time": None,
        "created_at": now,
        "updated_at": now
    }

    result = conversations_collection.insert_one(conversation_data)

    return {
        "message": "Conversation created successfully",
        "conversation_id": str(result.inserted_id)
    }


@app.get("/chat/conversations/{user_id}")
def get_user_conversations(user_id: str):
    conversations = conversations_collection.find({
        "participants": user_id
    }).sort("updated_at", -1)

    result = []

    for conv in conversations:
        participants = conv.get("participants", [])
        other_user_id = ""

        for participant in participants:
            if participant != user_id:
                other_user_id = participant
                break

        other_user = None
        if other_user_id:
            try:
                other_user = accounts_collection.find_one({
                    "_id": safe_object_id(other_user_id)
                })
            except Exception:
                other_user = None

        unread_count = messages_collection.count_documents({
            "conversation_id": str(conv["_id"]),
            "receiver_id": user_id,
            "is_read": False
        })

        result.append({
            "conversation_id": str(conv["_id"]),
            "other_user_id": other_user_id,
            "name": other_user.get("name", "") if other_user else "",
            "username": other_user.get("username", "") if other_user else "",
            "profile_image": other_user.get("profile_image", "") if other_user else "",
            "account_type": other_user.get("account_type", "") if other_user else "",
            "last_message": conv.get("last_message", ""),
            "last_message_time": conv.get("last_message_time").isoformat() + "Z"
            if conv.get("last_message_time") else "",
            "unread_count": unread_count
        })

    return result


@app.get("/chat/messages/{conversation_id}")
def get_conversation_messages(conversation_id: str, viewer_id: str = ""):
    conversation = conversations_collection.find_one({
        "_id": safe_object_id(conversation_id)
    })

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if viewer_id:
        messages_collection.update_many(
            {
                "conversation_id": conversation_id,
                "receiver_id": viewer_id,
                "is_read": False
            },
            {
                "$set": {
                    "is_read": True
                }
            }
        )

    messages = messages_collection.find({
        "conversation_id": conversation_id
    }).sort("created_at", 1)

    result = []
    for msg in messages:
        result.append({
            "id": str(msg["_id"]),
            "conversation_id": msg.get("conversation_id", ""),
            "sender_id": msg.get("sender_id", ""),
            "receiver_id": msg.get("receiver_id", ""),
            "text": msg.get("text", ""),
            "message_type": msg.get("message_type", "text"),
            "media_url": msg.get("media_url", ""),
            "is_read": msg.get("is_read", False),
            "created_at": msg.get("created_at").isoformat() + "Z"
            if msg.get("created_at") else ""
        })

    return result


@app.post("/chat/message")
def send_message(data: MessageCreate):
    conversation = conversations_collection.find_one({
        "_id": safe_object_id(data.conversation_id)
    })

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    sender = accounts_collection.find_one({"_id": safe_object_id(data.sender_id)})
    receiver = accounts_collection.find_one({"_id": safe_object_id(data.receiver_id)})

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="Sender or receiver not found")

    message_type = (data.message_type or "text").strip().lower()
    text_value = (data.text or "").strip() if data.text else ""
    media_url = (data.media_url or "").strip() if data.media_url else ""

    if message_type not in ["text", "image", "video"]:
        raise HTTPException(status_code=400, detail="Invalid message type")

    if message_type == "text" and not text_value:
        raise HTTPException(status_code=400, detail="Message text cannot be empty")

    if message_type in ["image", "video"] and not media_url:
        media_url = text_value

    if message_type in ["image", "video"] and not media_url:
        raise HTTPException(status_code=400, detail="Media URL is required")

    now = datetime.utcnow()

    if message_type == "text":
        saved_text = text_value
        last_message_preview = text_value
    elif message_type == "image":
        saved_text = ""
        last_message_preview = "📷 Image"
    else:
        saved_text = ""
        last_message_preview = "🎥 Video"

    message_data = {
        "conversation_id": data.conversation_id,
        "sender_id": data.sender_id,
        "receiver_id": data.receiver_id,
        "text": saved_text,
        "message_type": message_type,
        "media_url": media_url,
        "is_read": False,
        "created_at": now
    }

    result = messages_collection.insert_one(message_data)

    conversations_collection.update_one(
        {"_id": safe_object_id(data.conversation_id)},
        {
            "$set": {
                "last_message": last_message_preview,
                "last_message_time": now,
                "updated_at": now
            }
        }
    )

    return {
        "message": "Message sent successfully",
        "message_id": str(result.inserted_id),
        "message_type": message_type,
        "media_url": media_url,
        "created_at": now.isoformat() + "Z"
    }
@app.post("/chat/upload-image")
async def chat_upload_image(file: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(
            file.file,
            resource_type="image",
            folder="stackmate/chat_images"
        )
        return {"url": result["secure_url"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/upload-video")
async def chat_upload_video(file: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(
            file.file,
            resource_type="video",
            folder="stackmate/chat_videos"
        )
        return {"url": result["secure_url"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ===============================
# Video Player Interactions
# ===============================

@app.get("/video-interactions/status")
def get_video_interaction_status(video_id: str, user_id: str):
    liked = video_likes_collection.find_one({
        "video_id": video_id,
        "user_id": user_id
    })

    disliked = video_dislikes_collection.find_one({
        "video_id": video_id,
        "user_id": user_id
    })

    saved = video_saves_collection.find_one({
        "video_id": video_id,
        "user_id": user_id
    })

    return {
        "liked": True if liked else False,
        "disliked": True if disliked else False,
        "saved": True if saved else False
    }


# ===============================
# LIKE
# ===============================
@app.post("/video-interactions/like")
def toggle_like(data: VideoLike):
    video = videos_collection.find_one({"_id": safe_object_id(data.video_id)})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    existing_like = video_likes_collection.find_one({
        "video_id": data.video_id,
        "user_id": data.user_id
    })

    if existing_like:
        video_likes_collection.delete_one({"_id": existing_like["_id"]})
        return {"message": "Like removed", "liked": False}

    # نحذف dislike إذا موجود
    video_dislikes_collection.delete_many({
        "video_id": data.video_id,
        "user_id": data.user_id
    })

    video_likes_collection.insert_one({
        "video_id": data.video_id,
        "user_id": data.user_id,
        "created_at": datetime.utcnow()
    })

    return {"message": "Video liked", "liked": True}


# ===============================
# DISLIKE
# ===============================
@app.post("/video-interactions/dislike")
def toggle_dislike(data: VideoDislike):
    video = videos_collection.find_one({"_id": safe_object_id(data.video_id)})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    existing_dislike = video_dislikes_collection.find_one({
        "video_id": data.video_id,
        "user_id": data.user_id
    })

    if existing_dislike:
        video_dislikes_collection.delete_one({"_id": existing_dislike["_id"]})
        return {"message": "Dislike removed", "disliked": False}

    # نحذف like إذا موجود
    video_likes_collection.delete_many({
        "video_id": data.video_id,
        "user_id": data.user_id
    })

    video_dislikes_collection.insert_one({
        "video_id": data.video_id,
        "user_id": data.user_id,
        "created_at": datetime.utcnow()
    })

    return {"message": "Video disliked", "disliked": True}


# ===============================
# SAVE
# ===============================
@app.post("/video-interactions/save")
def save_video(data: VideoSave):
    video = videos_collection.find_one({"_id": safe_object_id(data.video_id)})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    existing_save = video_saves_collection.find_one({
        "video_id": data.video_id,
        "user_id": data.user_id
    })

    if existing_save:
        return {"message": "Already saved", "saved": True}

    video_saves_collection.insert_one({
        "video_id": data.video_id,
        "user_id": data.user_id,
        "created_at": datetime.utcnow()
    })

    return {"message": "Saved", "saved": True}


# ===============================
# UNSAVE (بدل DELETE)
# ===============================
@app.post("/video-interactions/unsave")
def unsave_video(data: VideoSave):
    result = video_saves_collection.delete_one({
        "video_id": data.video_id,
        "user_id": data.user_id
    })

    if result.deleted_count == 0:
        return {"message": "Not saved", "saved": False}

    return {"message": "Unsaved", "saved": False}
# ===============================
# VIEWS
# ===============================
@app.post("/videos/{video_id}/view")
def increment_video_view(video_id: str):
    video = videos_collection.find_one({"_id": safe_object_id(video_id)})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    videos_collection.update_one(
        {"_id": safe_object_id(video_id)},
        {"$inc": {"views": 1}}
    )

    updated_video = videos_collection.find_one({"_id": safe_object_id(video_id)})

    return {
        "message": "View added",
        "views": updated_video.get("views", 0)
    }
# ===============================
# AI Search Endpoint (DB VERSION)
# ===============================

def is_arabic_text(text: str) -> bool:
    return bool(re.search(r"[\u0600-\u06FF]", text or ""))


def normalize_text(value: str) -> str:
    if not value:
        return ""
    return str(value).strip().lower()


def fallback_related_terms(prompt: str) -> list[str]:
    p = normalize_text(prompt)

    mapping = {
        "شبكات": ["شبكات", "مهندس شبكات", "network", "networks", "networking", "cisco", "routing", "switching", "mikrotik"],
        "network": ["شبكات", "مهندس شبكات", "network", "networks", "networking", "cisco", "routing", "switching", "mikrotik"],

        "رياضيات": ["رياضيات", "math", "mathematics", "numerical analysis", "statistics", "algebra"],
        "math": ["رياضيات", "math", "mathematics", "numerical analysis", "statistics", "algebra"],

        "ذكاء اصطناعي": ["ذكاء اصطناعي", "ai", "artificial intelligence", "machine learning", "deep learning", "neural network"],
        "ai": ["ذكاء اصطناعي", "ai", "artificial intelligence", "machine learning", "deep learning", "neural network"],

        "frontend": ["frontend", "front-end", "react", "html", "css", "javascript", "واجهات"],
        "backend": ["backend", "back-end", "python", "fastapi", "node", "api", "خلفية"],
        "mobile": ["mobile", "flutter", "react native", "android", "ios", "تطبيقات"],
        "python": ["python", "fastapi", "django", "flask"],
        "flutter": ["flutter", "mobile", "android", "ios", "dart"],
        "react": ["react", "frontend", "javascript", "html", "css"],
    }

    expanded = set()
    expanded.add(p)

    for key, values in mapping.items():
        if key in p:
            for v in values:
                expanded.add(v.lower())

    if len(expanded) == 1:
        words = re.findall(r"[\w\u0600-\u06FF\-\+]+", p)
        for w in words:
            expanded.add(w.lower())

    return list(expanded)


@app.post("/ai-search")
async def ai_search(data: AIMessageRequest):
    try:
        user_id = data.user_id.strip()
        user_prompt = str(data.prompt).strip()
        conversation_id = data.conversation_id.strip()

        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")

        if not user_prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")

        account = accounts_collection.find_one({"_id": safe_object_id(user_id)})
        if not account:
            raise HTTPException(status_code=404, detail="User not found")

        # إذا ماكو محادثة، ننشئ وحدة جديدة
        if not conversation_id:
            conv_result = ai_conversations_collection.insert_one({
                "user_id": user_id,
                "title": user_prompt[:40],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            conversation_id = str(conv_result.inserted_id)
        else:
            existing_conv = ai_conversations_collection.find_one({
                "_id": safe_object_id(conversation_id),
                "user_id": user_id
            })
            if not existing_conv:
                raise HTTPException(status_code=404, detail="AI conversation not found")

        # نحفظ رسالة المستخدم
        ai_messages_collection.insert_one({
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": "user",
            "text": user_prompt,
            "created_at": datetime.utcnow()
        })

        language = "ar" if is_arabic_text(user_prompt) else "en"

        keywords = fallback_related_terms(user_prompt)
        main_query = user_prompt
        suggestions = keywords[:4]

        regex_conditions = []
        for kw in keywords:
            regex_conditions.extend([
                {"job": {"$regex": kw, "$options": "i"}},
                {"skill": {"$regex": kw, "$options": "i"}},
                {"technologies": {"$regex": kw, "$options": "i"}},
                {"bio": {"$regex": kw, "$options": "i"}},
                {"name": {"$regex": kw, "$options": "i"}},
            ])

        developers = list(developers_collection.find({"$or": regex_conditions}))

        ranked_developers = []

        for dev in developers:
            dev_id = str(dev["_id"])

            dev_videos = list(videos_collection.find({"developer_id": dev_id}))
            video_ids = [str(v["_id"]) for v in dev_videos]

            total_views = sum(v.get("views", 0) for v in dev_videos)

            total_likes = 0
            if video_ids:
                total_likes = video_likes_collection.count_documents({
                    "video_id": {"$in": video_ids}
                })

            score = total_views + (total_likes * 5)

            ranked_developers.append({
                "id": dev_id,
                "account_id": dev.get("account_id", ""),
                "name": dev.get("name", ""),
                "job": dev.get("job", ""),
                "skill": dev.get("skill", ""),
                "technologies": dev.get("technologies", ""),
                "bio": dev.get("bio", ""),
                "avatar": dev.get("avatar", ""),
                "location": dev.get("location", ""),
                "experience": dev.get("experience", ""),
                "views": total_views,
                "likes": total_likes,
                "score": score
            })

        ranked_developers.sort(key=lambda x: x["score"], reverse=True)
        top_developers = ranked_developers[:5]

        if not top_developers:
            if language == "ar":
                reply = (
                    f"لا يوجد حالياً مبرمجون مطابقون لبحث: {main_query}\n"
                    f"جربي البحث عن: {', '.join(suggestions)}"
                )
            else:
                reply = (
                    f"No developers found for: {main_query}\n"
                    f"Try searching for: {', '.join(suggestions)}"
                )
        else:
            if language == "ar":
                lines = [f"أفضل المبرمجين في مجال: {main_query}"]
                for i, dev in enumerate(top_developers, start=1):
                    title = dev.get("job") or dev.get("skill") or "مبرمج"
                    tech = dev.get("technologies", "")
                    lines.append(
                        f"{i}. {dev['name']} — {title} — {tech} "
                        f"(المشاهدات: {dev['views']}, الإعجابات: {dev['likes']})"
                    )
                reply = "\n".join(lines)
            else:
                lines = [f"Best developers for: {main_query}"]
                for i, dev in enumerate(top_developers, start=1):
                    title = dev.get("job") or dev.get("skill") or "Developer"
                    tech = dev.get("technologies", "")
                    lines.append(
                        f"{i}. {dev['name']} — {title} — {tech} "
                        f"(Views: {dev['views']}, Likes: {dev['likes']})"
                    )
                reply = "\n".join(lines)

        # نحفظ رد AI
        ai_messages_collection.insert_one({
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": "assistant",
            "text": reply,
            "developers": top_developers,
            "created_at": datetime.utcnow()
        })

        # نحدث وقت آخر محادثة
        ai_conversations_collection.update_one(
            {"_id": safe_object_id(conversation_id)},
            {
                "$set": {
                    "updated_at": datetime.utcnow(),
                    "last_message": user_prompt
                }
            }
        )
        return {
            "conversation_id": conversation_id,
            "reply": reply,
            "language": language,
            "keyword": main_query,
            "developers": top_developers,
            "suggestions": suggestions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # ===============================
# AI Chat History
# ===============================
@app.get("/ai-conversations/{user_id}")
def get_ai_conversations(user_id: str):
    conversations = ai_conversations_collection.find({
        "user_id": user_id
    }).sort("updated_at", -1)

    result = []
    for conv in conversations:
        result.append({
            "conversation_id": str(conv["_id"]),
            "title": conv.get("title", ""),
            "last_message": conv.get("last_message", ""),
            "updated_at": conv.get("updated_at").isoformat() + "Z" if conv.get("updated_at") else ""
        })

    return result


@app.get("/ai-messages/{conversation_id}")
def get_ai_messages(conversation_id: str):
    messages = ai_messages_collection.find({
        "conversation_id": conversation_id
    }).sort("created_at", 1)

    result = []
    for msg in messages:
        result.append({
            "id": str(msg["_id"]),
            "conversation_id": msg.get("conversation_id", ""),
            "user_id": msg.get("user_id", ""),
            "role": msg.get("role", ""),
            "text": msg.get("text", ""),
            "developers": msg.get("developers", []),
            "created_at": msg.get("created_at").isoformat() + "Z" if msg.get("created_at") else ""
        })

    return result
# ===============================
# Users Search (for Create Group)
# ===============================
@app.get("/users/search")
def search_users(q: str = "", current_user_id: str = ""):
    query = {}

    if q.strip():
        query = {
            "$or": [
                {"name": {"$regex": q, "$options": "i"}},
                {"username": {"$regex": q, "$options": "i"}},
                {"email": {"$regex": q, "$options": "i"}},
            ]
        }

    users = accounts_collection.find(query).limit(50)

    result = []
    for user in users:
        user_id = str(user["_id"])

        if current_user_id and user_id == current_user_id:
            continue

        result.append({
            "id": user_id,
            "name": user.get("name", ""),
            "username": user.get("username", ""),
            "profile_image": user.get("profile_image", ""),
            "account_type": user.get("account_type", "")
        })

    return result


# ===============================
# Groups
# ===============================
@app.post("/groups/create")
def create_group(data: GroupCreate):
    creator = accounts_collection.find_one({"_id": safe_object_id(data.creator_id)})
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    if not data.name.strip():
        raise HTTPException(status_code=400, detail="Group name is required")

    valid_member_ids = []

    for member_id in data.member_ids:
        try:
            member = accounts_collection.find_one({"_id": safe_object_id(member_id)})
            if member:
                valid_member_ids.append(member_id)
        except Exception:
            continue

    # نضمن أن منشئ الكروب موجود ضمن الأعضاء
    all_members = list(set([data.creator_id] + valid_member_ids))

    now = datetime.utcnow()

    group_data = {
        "name": data.name.strip(),
        "image": "",
        "creator_id": data.creator_id,
        "members": all_members,
        "last_message": "",
        "updated_at": now,
        "created_at": now
    }

    result = groups_collection.insert_one(group_data)

    return {
        "message": "Group created successfully",
        "group_id": str(result.inserted_id)
    }


@app.get("/groups/{user_id}")
def get_user_groups(user_id: str):
    groups = groups_collection.find({
        "members": user_id
    }).sort("updated_at", -1)

    result = []

    for group in groups:
        result.append({
            "group_id": str(group["_id"]),
            "name": group.get("name", "Group"),
            "image": group.get("image", ""),
            "last_message": group.get("last_message", ""),
            "updated_at": group.get("updated_at").isoformat() + "Z"
            if group.get("updated_at") else "",
            "members_count": len(group.get("members", []))
        })

    return result# ===============================
# Group Chat
# ===============================

@app.get("/group/{group_id}")
def get_group_details(group_id: str):
    group = groups_collection.find_one({"_id": safe_object_id(group_id)})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    members_data = []

    for member_id in group.get("members", []):
        acc = None
        try:
            acc = accounts_collection.find_one({"_id": safe_object_id(member_id)})
        except Exception:
            acc = None

        if acc:
            members_data.append({
                "id": str(acc["_id"]),
                "name": acc.get("name", "") or acc.get("username", ""),
                "username": acc.get("username", ""),
                "profile_image": acc.get("profile_image", ""),
                "account_type": acc.get("account_type", ""),
                "university_name": acc.get("university_name", ""),
                "college_name": acc.get("college_name", ""),
                "department_name": acc.get("department_name", "")
            })

    return {
        "group_id": str(group["_id"]),
        "name": group.get("name", "Group"),
        "image": group.get("image", ""),
        "creator_id": group.get("creator_id", ""),
        "members_count": len(group.get("members", [])),
        "members": members_data,
        "created_at": group.get("created_at").isoformat() + "Z"
        if group.get("created_at") else ""
    }


@app.get("/group/messages/{group_id}")
def get_group_messages(group_id: str, viewer_id: str = ""):
    group = groups_collection.find_one({"_id": safe_object_id(group_id)})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if viewer_id:
        group_messages_collection.update_many(
            {
                "group_id": group_id,
                "sender_id": {"$ne": viewer_id},
                "read_by": {"$ne": viewer_id}
            },
            {
                "$addToSet": {"read_by": viewer_id}
            }
        )

    messages = group_messages_collection.find({
        "group_id": group_id
    }).sort("created_at", 1)

    result = []

    members_count = len(group.get("members", []))

    for msg in messages:
        sender = None
        sender_id = msg.get("sender_id", "")

        if sender_id:
            try:
                sender = accounts_collection.find_one({
                    "_id": safe_object_id(sender_id)
                })
            except Exception:
                sender = None

        read_by = msg.get("read_by", [])
        delivered_to = msg.get("delivered_to", [])

        result.append({
            "id": str(msg["_id"]),
            "group_id": msg.get("group_id", ""),
            "sender_id": sender_id,
            "sender_name": (sender.get("name", "") or sender.get("username", "")) if sender else "",
            "sender_image": sender.get("profile_image", "") if sender else "",
            "sender_account_type": sender.get("account_type", "") if sender else "",
            "text": msg.get("text", ""),
            "message_type": msg.get("message_type", "text"),
            "media_url": msg.get("media_url", ""),
            "created_at": msg.get("created_at").isoformat() + "Z"
            if msg.get("created_at") else "",
            "read_by": read_by,
            "delivered_to": delivered_to,
            "read_count": len(read_by),
            "delivered_count": len(delivered_to),
            "members_count": members_count
        })

    return result


@app.post("/group/message")
def send_group_message(data: GroupMessageCreate):
    group = groups_collection.find_one({"_id": safe_object_id(data.group_id)})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    sender = accounts_collection.find_one({"_id": safe_object_id(data.sender_id)})
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")
    if data.sender_id not in group.get("members", []):
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    message_type = (data.message_type or "text").strip().lower()
    text_value = (data.text or "").strip()
    media_url = (data.media_url or "").strip()

    if message_type not in ["text", "image", "video"]:
        raise HTTPException(status_code=400, detail="Invalid message type")

    if message_type == "text" and not text_value:
        raise HTTPException(status_code=400, detail="Message text cannot be empty")

    if message_type in ["image", "video"] and not media_url:
        media_url = text_value

    if message_type in ["image", "video"] and not media_url:
        raise HTTPException(status_code=400, detail="Media URL is required")

    now = datetime.utcnow()

    members = group.get("members", [])
    delivered_to = [member_id for member_id in members if member_id != data.sender_id]
    read_by = [data.sender_id]

    if message_type == "text":
        saved_text = text_value
        last_message_preview = text_value
    elif message_type == "image":
        saved_text = ""
        last_message_preview = "📷 Image"
    else:
        saved_text = ""
        last_message_preview = "🎥 Video"

    message_data = {
        "group_id": data.group_id,
        "sender_id": data.sender_id,
        "text": saved_text,
        "message_type": message_type,
        "media_url": media_url,
        "delivered_to": delivered_to,
        "read_by": read_by,
        "created_at": now
    }

    result = group_messages_collection.insert_one(message_data)

    groups_collection.update_one(
        {"_id": safe_object_id(data.group_id)},
        {
            "$set": {
                "last_message": last_message_preview,
                "updated_at": now
            }
        }
    )

    return {
        "message": "Group message sent successfully",
        "message_id": str(result.inserted_id),
        "message_type": message_type,
        "media_url": media_url,
        "created_at": now.isoformat() + "Z"
    }


# ===============================
# Group Upload Media
# ===============================
@app.post("/group/upload-image")
async def group_upload_image(file: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(
            file.file,
            resource_type="image",
            folder="stackmate/group_images"
        )
        return {"url": result["secure_url"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/group/upload-video")
async def group_upload_video(file: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(
            file.file,
            resource_type="video",
            folder="stackmate/group_videos"
        )
        return {"url": result["secure_url"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ===============================
# Channels
# ===============================

@app.post("/channels/create")
def create_channel(data: ChannelCreate):
    owner = accounts_collection.find_one({"_id": safe_object_id(data.owner_id)})
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    if not data.name.strip():
        raise HTTPException(status_code=400, detail="Channel name is required")

    now = datetime.utcnow()

    channel_data = {
        "name": data.name.strip(),
        "description": (data.description or "").strip(),
        "image": (data.image or "").strip(),
        "owner_id": data.owner_id,
        "is_public": data.is_public,
        "followers_count": 1,
        "last_message": "",
        "created_at": now,
        "updated_at": now
    }

    result = channels_collection.insert_one(channel_data)

    channel_followers_collection.insert_one({
        "channel_id": str(result.inserted_id),
        "user_id": data.owner_id,
        "created_at": now
    })

    return {
        "message": "Channel created successfully",
        "channel_id": str(result.inserted_id)
    }


@app.get("/channels")
def get_channels(user_id: str = ""):
    channels = channels_collection.find().sort("updated_at", -1)

    result = []

    for channel in channels:
        channel_id = str(channel["_id"])

        owner = None
        try:
            owner = accounts_collection.find_one({
                "_id": safe_object_id(channel.get("owner_id", ""))
            })
        except Exception:
            owner = None

        is_following = False
        if user_id:
            is_following = channel_followers_collection.find_one({
                "channel_id": channel_id,
                "user_id": user_id
            }) is not None

        result.append({
            "channel_id": channel_id,
            "name": channel.get("name", "Channel"),
            "description": channel.get("description", ""),
            "image": channel.get("image", ""),
            "owner_id": channel.get("owner_id", ""),
            "owner_name": owner.get("name", "") if owner else "",
            "followers_count": channel.get("followers_count", 0),
            "last_message": channel.get("last_message", ""),
            "updated_at": channel.get("updated_at").isoformat() + "Z"
            if channel.get("updated_at") else "",
            "is_following": is_following,
            "is_owner": user_id == channel.get("owner_id", "")
        })

    return result


@app.get("/channels/{channel_id}")
def get_channel_details(channel_id: str, user_id: str = ""):
    channel = channels_collection.find_one({"_id": safe_object_id(channel_id)})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    owner = None
    try:
        owner = accounts_collection.find_one({
            "_id": safe_object_id(channel.get("owner_id", ""))
        })
    except Exception:
        owner = None

    is_following = False
    if user_id:
        is_following = channel_followers_collection.find_one({
            "channel_id": channel_id,
            "user_id": user_id
        }) is not None

    return {
        "channel_id": str(channel["_id"]),
        "name": channel.get("name", "Channel"),
        "description": channel.get("description", ""),
        "image": channel.get("image", ""),
        "owner_id": channel.get("owner_id", ""),
        "owner_name": owner.get("name", "") if owner else "",
        "followers_count": channel.get("followers_count", 0),
        "is_public": channel.get("is_public", True),
        "is_following": is_following,
        "is_owner": user_id == channel.get("owner_id", "")
    }


@app.post("/channels/follow-toggle")
def toggle_follow_channel(data: ChannelFollowToggle):
    channel = channels_collection.find_one({"_id": safe_object_id(data.channel_id)})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    user = accounts_collection.find_one({"_id": safe_object_id(data.user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = channel_followers_collection.find_one({
        "channel_id": data.channel_id,
        "user_id": data.user_id
    })

    if existing:
        channel_followers_collection.delete_one({"_id": existing["_id"]})
        channels_collection.update_one(
            {"_id": safe_object_id(data.channel_id)},
            {"$inc": {"followers_count": -1}}
        )
        return {"message": "Channel unfollowed", "is_following": False}

    channel_followers_collection.insert_one({
        "channel_id": data.channel_id,
        "user_id": data.user_id,
        "created_at": datetime.utcnow()
    })

    channels_collection.update_one(
        {"_id": safe_object_id(data.channel_id)},
        {"$inc": {"followers_count": 1}}
    )

    return {"message": "Channel followed", "is_following": True}


@app.get("/channel/messages/{channel_id}")
def get_channel_messages(channel_id: str):
    channel = channels_collection.find_one({"_id": safe_object_id(channel_id)})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    messages = channel_messages_collection.find({
        "channel_id": channel_id
    }).sort("created_at", 1)

    result = []

    for msg in messages:
        sender = None
        sender_id = msg.get("sender_id", "")

        if sender_id:
            try:
                sender = accounts_collection.find_one({
                    "_id": safe_object_id(sender_id)
                })
            except Exception:
                sender = None

        result.append({
            "id": str(msg["_id"]),
            "channel_id": msg.get("channel_id", ""),
            "sender_id": sender_id,
            "sender_name": (sender.get("name", "") or sender.get("username", "")) if sender else "",
            "sender_image": sender.get("profile_image", "") if sender else "",
            "text": msg.get("text", ""),
            "message_type": msg.get("message_type", "text"),
            "media_url": msg.get("media_url", ""),
            "created_at": msg.get("created_at").isoformat() + "Z"
            if msg.get("created_at") else ""
        })

    return result


@app.post("/channel/message")
def send_channel_message(data: ChannelMessageCreate):
    channel = channels_collection.find_one({"_id": safe_object_id(data.channel_id)})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    sender = accounts_collection.find_one({"_id": safe_object_id(data.sender_id)})
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")

    if data.sender_id != channel.get("owner_id", ""):
        raise HTTPException(status_code=403, detail="Only the channel owner can post")

    message_type = (data.message_type or "text").strip().lower()
    text_value = (data.text or "").strip() if data.text else ""
    media_url = (data.media_url or "").strip() if data.media_url else ""

    if message_type not in ["text", "image", "video"]:
        raise HTTPException(status_code=400, detail="Invalid message type")

    if message_type == "text" and not text_value:
        raise HTTPException(status_code=400, detail="Message text cannot be empty")

    if message_type in ["image", "video"] and not media_url:
        media_url = text_value

    if message_type in ["image", "video"] and not media_url:
        raise HTTPException(status_code=400, detail="Media URL is required")

    now = datetime.utcnow()

    if message_type == "text":
        saved_text = text_value
        last_message_preview = text_value
    elif message_type == "image":
        saved_text = ""
        last_message_preview = "📷 Image"
    else:
        saved_text = ""
        last_message_preview = "🎥 Video"
        message_data = {
        "channel_id": data.channel_id,
        "sender_id": data.sender_id,
        "text": saved_text,
        "message_type": message_type,
        "media_url": media_url,
        "created_at": now
    }

    result = channel_messages_collection.insert_one(message_data)

    channels_collection.update_one(
        {"_id": safe_object_id(data.channel_id)},
        {
            "$set": {
                "last_message": last_message_preview,
                "updated_at": now
            }
        }
    )

    return {
        "message": "Channel post created successfully",
        "message_id": str(result.inserted_id),
        "message_type": message_type,
        "media_url": media_url,
        "created_at": now.isoformat() + "Z"
    }


@app.post("/channel/upload-image")
async def channel_upload_image(file: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(
            file.file,
            resource_type="image",
            folder="stackmate/channel_images"
        )
        return {"url": result["secure_url"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/channel/upload-video")
async def channel_upload_video(file: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(
            file.file,
            resource_type="video",
            folder="stackmate/channel_videos"
        )
        return {"url": result["secure_url"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/make-me-admin/{user_id}")
def make_me_admin(user_id: str):
    accounts_collection.update_one(
        {"_id": safe_object_id(user_id)},
        {"$set": {"is_admin": True}}
    )
    return {"message": "You are now admin"}
