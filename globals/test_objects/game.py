from game.models import Session, SessionQuestion


def create_session(user, correct_answer, user_answer=None,challenge_type="random",):
    return Session.objects.create(
        user=user,
        challenge_type=challenge_type,
        correct_answer=correct_answer,
        user_answer=user_answer,
    )

def create_session_question(session, ayah):
    return SessionQuestion.objects.create(
        session=session,
        ayah=ayah,
    )
