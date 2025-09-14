from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_user
from app.models.user import User
from app.models.video import Video, VideoLike, VideoView
from app.schemas.video import Video as VideoSchema
from app.schemas.video import VideoCreate, VideoUpdate
from fastapi import APIRouter, Depends, HTTPException, Request, status

router = APIRouter()


@router.get("/", response_model=list[VideoSchema])
async def get_videos(
    skip: int = 0,
    limit: int = 20,
    status_filter: str = None,
    db: Session = Depends(get_db),
):
    """Get list of videos with optional filtering."""
    query = db.query(Video).filter(Video.status == "ready")

    if status_filter:
        query = query.filter(Video.status == status_filter)

    videos = query.offset(skip).limit(limit).all()
    return videos


@router.get("/{video_id}", response_model=VideoSchema)
async def get_video(
    video_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get video by ID and record view."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    # Record view
    view = VideoView(
        video_id=video_id,
        viewer_id=current_user.id if current_user else None,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
    )
    db.add(view)

    # Increment view count
    video.views_count += 1

    db.commit()
    db.refresh(video)

    return video


@router.post("/", response_model=VideoSchema)
async def create_video(
    video_data: VideoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new video."""
    video = Video(**video_data.dict(), uploaded_by_id=current_user.id)

    db.add(video)
    db.commit()
    db.refresh(video)

    return video


@router.put("/{video_id}", response_model=VideoSchema)
async def update_video(
    video_id: str,
    video_update: VideoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update video information."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    # Check permissions
    if not current_user.is_staff and video.uploaded_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # Update only provided fields
    update_data = video_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(video, field, value)

    db.commit()
    db.refresh(video)
    return video


@router.delete("/{video_id}")
async def delete_video(
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete video."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    # Check permissions
    if not current_user.is_staff and video.uploaded_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    db.delete(video)
    db.commit()

    return {"message": "Video deleted successfully"}


@router.post("/{video_id}/like")
async def like_video(
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Like a video."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    # Check if already liked
    existing_like = (
        db.query(VideoLike)
        .filter(VideoLike.video_id == video_id, VideoLike.user_id == current_user.id)
        .first()
    )

    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Video already liked"
        )

    # Create like
    like = VideoLike(video_id=video_id, user_id=current_user.id)
    db.add(like)

    # Increment like count
    video.likes_count += 1

    db.commit()

    return {"message": "Video liked successfully"}


@router.delete("/{video_id}/like")
async def unlike_video(
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Unlike a video."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    # Find and remove like
    like = (
        db.query(VideoLike)
        .filter(VideoLike.video_id == video_id, VideoLike.user_id == current_user.id)
        .first()
    )

    if not like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Video not liked"
        )

    db.delete(like)

    # Decrement like count
    if video.likes_count > 0:
        video.likes_count -= 1

    db.commit()

    return {"message": "Video unliked successfully"}
