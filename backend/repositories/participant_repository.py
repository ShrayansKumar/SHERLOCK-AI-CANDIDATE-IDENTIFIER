from sqlalchemy.orm import Session

from models.participant import Participant


class ParticipantRepository:

    def create(
        self,
        db: Session,
        participant: Participant
    ):

        db.add(participant)
        db.commit()
        db.refresh(participant)

        return participant


    def get_all(
        self,
        db: Session
    ):

        return db.query(Participant).order_by(Participant.created_at.desc()).all()


    def get_by_id(
        self,
        db: Session,
        participant_id: int
    ):

        return (
            db.query(Participant)
            .filter(Participant.id == participant_id)
            .first()
        )


    def delete(
        self,
        db: Session,
        participant_id: int
    ):

        participant = (
            db.query(Participant)
            .filter(Participant.id == participant_id)
            .first()
        )

        if participant:
            db.delete(participant)
            db.commit()

        return participant

    def get_by_participant_identifier(
        self,
        db: Session,
        participant_identifier: str,
    ):
        return (
            db.query(Participant)
            .filter(
                Participant.participant_id == participant_identifier
            )
            .first()
        )


    def update_confidence(
        self,
        db: Session,
        participant_identifier: str,
        confidence: float,
    ):
        participant = self.get_by_participant_identifier(
            db,
            participant_identifier,
        )

        if participant is None:
            return None

        participant.confidence = confidence

        db.commit()
        db.refresh(participant)

        return participant