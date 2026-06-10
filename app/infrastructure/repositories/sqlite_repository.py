import sqlite3
import json
from typing import Optional, Tuple, List
from app.domain.interfaces.session_repository import ISessionRepository
from app.domain.schemas import (
    InterviewSession, 
    CandidateProfile, 
    JobRequirement, 
    SkillGap, 
    EvaluationResult, 
    CareerAdvice,
    CandidateAnswer,
    InterviewQuestion
)
from app.core.exceptions import SessionNotFoundException
from app.core.logging import logger

class SQLiteSessionRepository(ISessionRepository):
    def __init__(self, database_url: str):
        # Extract file path from sqlite:///path
        self.db_path = database_url.replace("sqlite:///", "")
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        # Enable row factory for easier mapping if needed, but we'll do manual select mapping
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    status TEXT DEFAULT 'created',
                    current_question_index INTEGER DEFAULT 0,
                    raw_resume TEXT,
                    raw_jd TEXT,
                    candidate_profile TEXT,
                    job_requirement TEXT,
                    skill_gap TEXT,
                    questions TEXT,
                    answers TEXT,
                    evaluation TEXT,
                    career_advice TEXT
                )
            """)
            conn.commit()
            logger.info("SQLite Database initialized successfully", db_path=self.db_path)

    def create_session(self, session_id: str) -> None:
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO sessions (session_id, status) VALUES (?, 'created')",
                    (session_id,)
                )
                conn.commit()
                logger.info("Created prep session in SQLite", session_id=session_id)
        except Exception as e:
            logger.error("Failed to create prep session in SQLite", session_id=session_id, error=str(e))
            raise

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT session_id, current_question_index, questions, answers, status FROM sessions WHERE session_id = ?",
                    (session_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return None

                session_id_val, current_question_index, questions_json, answers_json, status = row
                
                # Parse questions
                questions: List[InterviewQuestion] = []
                if questions_json:
                    try:
                        questions_data = json.loads(questions_json)
                        questions = [InterviewQuestion.model_validate(q) for q in questions_data]
                    except Exception as pe:
                        logger.error("Error parsing questions from JSON", error=str(pe))

                # Parse answers
                answers: List[CandidateAnswer] = []
                if answers_json:
                    try:
                        answers_data = json.loads(answers_json)
                        answers = [CandidateAnswer.model_validate(a) for a in answers_data]
                    except Exception as pe:
                        logger.error("Error parsing answers from JSON", error=str(pe))

                return InterviewSession(
                    session_id=session_id_val,
                    current_question_index=current_question_index or 0,
                    questions=questions,
                    answers=answers,
                    status=status or "created"
                )
        except Exception as e:
            logger.error("Error retrieving session from SQLite", session_id=session_id, error=str(e))
            return None

    def update_session(self, session: InterviewSession) -> None:
        try:
            questions_json = json.dumps([q.model_dump() for q in session.questions])
            answers_json = json.dumps([a.model_dump() for a in session.answers])

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT 1 FROM sessions WHERE session_id = ?",
                    (session.session_id,)
                )
                if not cursor.fetchone():
                    # insert if missing, though typically we create first
                    conn.execute(
                        "INSERT INTO sessions (session_id, status, current_question_index, questions, answers) VALUES (?, ?, ?, ?, ?)",
                        (session.session_id, session.status, session.current_question_index, questions_json, answers_json)
                    )
                else:
                    conn.execute(
                        "UPDATE sessions SET status = ?, current_question_index = ?, questions = ?, answers = ? WHERE session_id = ?",
                        (session.status, session.current_question_index, questions_json, answers_json, session.session_id)
                    )
                conn.commit()
                logger.info("Updated interview session in SQLite", session_id=session.session_id, status=session.status)
        except Exception as e:
            logger.error("Failed to update session in SQLite", session_id=session.session_id, error=str(e))
            raise

    def save_profile(self, session_id: str, profile: CandidateProfile) -> None:
        try:
            profile_json = profile.model_dump_json()
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE sessions SET candidate_profile = ? WHERE session_id = ?",
                    (profile_json, session_id)
                )
                conn.commit()
                logger.info("Saved candidate profile to session", session_id=session_id)
        except Exception as e:
            logger.error("Failed to save candidate profile", session_id=session_id, error=str(e))
            raise

    def get_profile(self, session_id: str) -> Optional[CandidateProfile]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT candidate_profile FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row and row[0]:
                return CandidateProfile.model_validate_json(row[0])
            return None

    def save_job_requirement(self, session_id: str, requirement: JobRequirement) -> None:
        try:
            req_json = requirement.model_dump_json()
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE sessions SET job_requirement = ? WHERE session_id = ?",
                    (req_json, session_id)
                )
                conn.commit()
                logger.info("Saved job requirements to session", session_id=session_id)
        except Exception as e:
            logger.error("Failed to save job requirements", session_id=session_id, error=str(e))
            raise

    def get_job_requirement(self, session_id: str) -> Optional[JobRequirement]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT job_requirement FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row and row[0]:
                return JobRequirement.model_validate_json(row[0])
            return None

    def save_skill_gap(self, session_id: str, gap: SkillGap) -> None:
        try:
            gap_json = gap.model_dump_json()
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE sessions SET skill_gap = ? WHERE session_id = ?",
                    (gap_json, session_id)
                )
                conn.commit()
                logger.info("Saved skill gap to session", session_id=session_id)
        except Exception as e:
            logger.error("Failed to save skill gap", session_id=session_id, error=str(e))
            raise

    def get_skill_gap(self, session_id: str) -> Optional[SkillGap]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT skill_gap FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row and row[0]:
                return SkillGap.model_validate_json(row[0])
            return None

    def save_evaluation(self, session_id: str, evaluation: EvaluationResult) -> None:
        try:
            eval_json = evaluation.model_dump_json()
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE sessions SET evaluation = ? WHERE session_id = ?",
                    (eval_json, session_id)
                )
                conn.commit()
                logger.info("Saved evaluation to session", session_id=session_id)
        except Exception as e:
            logger.error("Failed to save evaluation", session_id=session_id, error=str(e))
            raise

    def get_evaluation(self, session_id: str) -> Optional[EvaluationResult]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT evaluation FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row and row[0]:
                return EvaluationResult.model_validate_json(row[0])
            return None

    def save_career_advice(self, session_id: str, advice: CareerAdvice) -> None:
        try:
            advice_json = advice.model_dump_json()
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE sessions SET career_advice = ? WHERE session_id = ?",
                    (advice_json, session_id)
                )
                conn.commit()
                logger.info("Saved career advice to session", session_id=session_id)
        except Exception as e:
            logger.error("Failed to save career advice", session_id=session_id, error=str(e))
            raise

    def get_career_advice(self, session_id: str) -> Optional[CareerAdvice]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT career_advice FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row and row[0]:
                return CareerAdvice.model_validate_json(row[0])
            return None

    def save_raw_texts(
        self, 
        session_id: str, 
        resume_text: Optional[str] = None, 
        jd_text: Optional[str] = None
    ) -> None:
        try:
            with self._get_connection() as conn:
                # Ensure session row exists (create if not present)
                conn.execute(
                    "INSERT OR IGNORE INTO sessions (session_id, status) VALUES (?, 'created')",
                    (session_id,)
                )
                # Update the text fields
                if resume_text is not None:
                    conn.execute("UPDATE sessions SET raw_resume = ? WHERE session_id = ?", (resume_text, session_id))
                if jd_text is not None:
                    conn.execute("UPDATE sessions SET raw_jd = ? WHERE session_id = ?", (jd_text, session_id))
                conn.commit()
                logger.info("Saved raw texts for session", session_id=session_id, resume_updated=resume_text is not None, jd_updated=jd_text is not None)
        except Exception as e:
            logger.error("Failed to save raw texts", session_id=session_id, error=str(e))
            raise

    def get_raw_texts(self, session_id: str) -> Tuple[Optional[str], Optional[str]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT raw_resume, raw_jd FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                return row[0], row[1]
            return None, None
