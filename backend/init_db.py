"""
Database initialization script
Creates tables and sample data
"""
import sys
from sqlalchemy.orm import Session

from database import init_db, SessionLocal, Camera


def create_sample_cameras(db: Session):
    """
    Create sample cameras for testing
    """
    cameras = [
        Camera(
            name="Front Entrance",
            location="Building A - Main Door",
            stream_url="0",  # Webcam
            is_active=False,
            fps=2
        ),
        Camera(
            name="Parking Lot",
            location="South Parking Area",
            stream_url="1",
            is_active=False,
            fps=2
        ),
        Camera(
            name="Lobby Camera",
            location="Main Lobby",
            stream_url="2",
            is_active=False,
            fps=2
        ),
        Camera(
            name="Back Entrance",
            location="Building A - Service Door",
            stream_url="3",
            is_active=False,
            fps=2
        )
    ]

    for camera in cameras:
        existing = db.query(Camera).filter(Camera.name == camera.name).first()
        if not existing:
            db.add(camera)

    db.commit()
    print(f"Created {len(cameras)} sample cameras")


def main():
    """
    Main initialization function
    """
    print("Initializing SentinTinel database...")

    # Create tables
    init_db()
    print("✓ Database tables created")

    # Create sample data
    db = SessionLocal()
    try:
        create_sample_cameras(db)
        print("✓ Sample data created")
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

    print("\n✅ Database initialization complete!")
    print("\nNext steps:")
    print("1. Update .env with your Gemini API key")
    print("2. Start the backend: python main.py")
    print("3. Start the frontend: cd frontend && npm start")


if __name__ == "__main__":
    main()
