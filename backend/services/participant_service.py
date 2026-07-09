from models.participant import Participant
from models.meeting import Meeting
from models.confidence import ConfidenceSnapshot
from repositories.participant_repository import ParticipantRepository


class ParticipantService:

    def __init__(self):

        self.repository = ParticipantRepository()


    def create_participant(
        self,
        db,
        data
    ):

        participant = Participant(
            meeting_id=data.meeting_id,
            participant_id=data.participant_id,
            display_name=data.display_name,
            email=data.email
        )

        return self.repository.create(
            db,
            participant
        )


    def get_all(
        self,
        db
    ):
        participants = self.repository.get_all(db)
        latest_meeting = db.query(Meeting).order_by(Meeting.created_at.desc()).first()

        has_interviewer = False
        for p in participants:
            if p.role in ["interviewer", "Interviewer"] or "interviewer" in str(p.participant_id).lower():
                has_interviewer = True
                p.role = "Interviewer"
                if latest_meeting and latest_meeting.interviewer_names:
                    p.display_name = latest_meeting.interviewer_names
            else:
                p.role = "Interviewee (Candidate)"
                if latest_meeting:
                    if latest_meeting.candidate_name:
                        p.display_name = latest_meeting.candidate_name
                    if latest_meeting.candidate_email:
                        p.email = latest_meeting.candidate_email
                    p.meeting_id = latest_meeting.id

            latest_snap = (
                db.query(ConfidenceSnapshot)
                .filter(ConfidenceSnapshot.participant_id == p.participant_id)
                .order_by(ConfidenceSnapshot.created_at.desc())
                .first()
            )
            if not latest_snap and p.role == "Interviewee (Candidate)":
                latest_snap = db.query(ConfidenceSnapshot).order_by(ConfidenceSnapshot.created_at.desc()).first()
            if latest_snap:
                p.confidence = latest_snap.confidence

        if not has_interviewer and latest_meeting and latest_meeting.interviewer_names:
            interviewer_p = Participant(
                id=9999,
                participant_id="interviewer_001",
                display_name=latest_meeting.interviewer_names,
                email="interviewer@company.com",
                role="Interviewer",
                webcam_on=True,
                microphone_on=True,
                screen_share=False,
                speaking_duration=0.0,
                confidence=1.0,
                status="joined",
                meeting_id=latest_meeting.id,
            )
            participants.append(interviewer_p)

        return participants


    def get_by_id(
        self,
        db,
        participant_id
    ):

        return self.repository.get_by_id(
            db,
            participant_id
        )


    def delete(
        self,
        db,
        participant_id
    ):

        return self.repository.delete(
            db,
            participant_id
        )

    def get_by_participant_identifier(
        self,
        db,
        participant_identifier,
    ):
        return self.repository.get_by_participant_identifier(
            db,
            participant_identifier,
        )


    def update_confidence(
        self,
        db,
        participant_identifier,
        confidence,
    ):
        return self.repository.update_confidence(
            db,
            participant_identifier,
            confidence,
        )