from api.models.database import SessionLocal, User, Issue, Trace, IssueStatus, IssueSeverity
from datetime import datetime

def test_database():
    # Create a new session
    db = SessionLocal()
    
    try:
        # Create a test user
        test_user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            hashed_password="hashed_password_here"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"Created test user with ID: {test_user.id}")
        
        # Create a test trace
        test_trace = Trace(
            user_id=test_user.id,
            file_name="test.txt",
            file_path="/path/to/test.txt",
            file_size=1024,
            file_type="text/plain",
            content="Test content",
            meta_data={"key": "value"},
            analysis_results={"result": "test"}
        )
        db.add(test_trace)
        db.commit()
        db.refresh(test_trace)
        print(f"Created test trace with ID: {test_trace.id}")
        
        # Create a test issue
        test_issue = Issue(
            title="Test Issue",
            description="This is a test issue",
            status=IssueStatus.OPEN,
            severity=IssueSeverity.MEDIUM,
            user_id=test_user.id,
            trace_id=test_trace.id
        )
        db.add(test_issue)
        db.commit()
        db.refresh(test_issue)
        print(f"Created test issue with ID: {test_issue.id}")
        
        # Query the data
        user = db.query(User).filter(User.email == "test@example.com").first()
        print(f"Found user: {user.email}")
        
        trace = db.query(Trace).filter(Trace.user_id == user.id).first()
        print(f"Found trace: {trace.file_name}")
        
        issue = db.query(Issue).filter(Issue.user_id == user.id).first()
        print(f"Found issue: {issue.title}")
        
        # Clean up
        db.delete(test_issue)
        db.delete(test_trace)
        db.delete(test_user)
        db.commit()
        print("Cleaned up test data")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_database() 