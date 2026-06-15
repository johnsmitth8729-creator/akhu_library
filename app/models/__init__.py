# Aggregate imports for convenience
from app.models.role import Role
from app.models.faculty import Faculty
from app.models.user import User
from app.models.book import Book, Category, Author, PhysicalBook, DigitalBook, ReadingProgress, PDFBookmark, BookRead
from app.models.borrow import BorrowRequest, BorrowHistory, FavoriteBook
from app.models.activity import ActivityLog
from app.models.system import Notification, Settings, Announcement, Review, AuditLog, SiteBanner, ImpersonationLog
from app.models.category import QuestionCategory
from app.models.question import Question, QuestionOption, CompetitionQuestion
from app.models.competition import (
    ReadingCompetition,
    CompetitionBook,
    CompetitionFaculty,
    CompetitionGroup,
    QuizAttempt,
    QuizAttemptAnswer,
    QuizViolation,
    UserBadge,
    CompetitionCertificate,
)

__all__ = [
    "Role", "Faculty", "User", "Book", "PhysicalBook", "DigitalBook", "Category", "Author",
    "ReadingProgress", "PDFBookmark", "BookRead", "BorrowRequest", "BorrowHistory", "FavoriteBook",
    "ActivityLog", "Notification", "Settings", "Announcement", "Review", "AuditLog", "SiteBanner", "ImpersonationLog",
    "ReadingCompetition", "Question", "QuestionOption", "CompetitionQuestion",
    "QuizAttempt", "QuizAttemptAnswer", "QuizViolation", "UserBadge", "CompetitionCertificate",
    "QuestionCategory", "CompetitionBook", "CompetitionFaculty", "CompetitionGroup",
]
