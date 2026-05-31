import structlog

logger = structlog.get_logger(__name__)


class DialogState:
    def __init__(self, session_id: str, user_id: int = 0):
        self.session_id = session_id
        self.user_id = user_id
        self.current_agent: str = ""
        self.dialog_phase: str = "greeting"
        self.slots: dict = {}
        self.pending_confirmation: dict | None = None
        self.handoff_history: list = []
        self.emotion: str = "neutral"
        self.turn_count: int = 0

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "current_agent": self.current_agent,
            "dialog_phase": self.dialog_phase,
            "slots": self.slots,
            "pending_confirmation": self.pending_confirmation,
            "handoff_history": self.handoff_history,
            "emotion": self.emotion,
            "turn_count": self.turn_count,
        }


class DialogStateManager:
    def __init__(self):
        self.states: dict[str, DialogState] = {}

    def get_or_create(self, session_id: str, user_id: int = 0) -> DialogState:
        if session_id not in self.states:
            self.states[session_id] = DialogState(session_id, user_id)
            logger.info("dialog_state_created", session_id=session_id, user_id=user_id)
        state = self.states[session_id]
        if user_id and not state.user_id:
            state.user_id = user_id
        return state

    def update_phase(self, session_id: str, phase: str):
        if session_id in self.states:
            old = self.states[session_id].dialog_phase
            self.states[session_id].dialog_phase = phase
            logger.info("dialog_phase_changed", session_id=session_id, old=old, new=phase)

    def set_slot(self, session_id: str, key: str, value):
        if session_id in self.states:
            self.states[session_id].slots[key] = value
            logger.info("slot_filled", session_id=session_id, key=key, value=value)

    def get_slot(self, session_id: str, key: str):
        if session_id in self.states:
            return self.states[session_id].slots.get(key)
        return None

    def get_missing_slots(self, session_id: str, required_slots: list[str]) -> list[str]:
        if session_id not in self.states:
            return list(required_slots)
        return [s for s in required_slots if s not in self.states[session_id].slots]

    def set_pending_confirmation(self, session_id: str, confirmation: dict):
        if session_id in self.states:
            self.states[session_id].pending_confirmation = confirmation
            self.states[session_id].dialog_phase = "confirming"
            logger.info("pending_confirmation_set", session_id=session_id, action=confirmation.get("action"))

    def clear_pending_confirmation(self, session_id: str):
        if session_id in self.states:
            self.states[session_id].pending_confirmation = None
            self.states[session_id].dialog_phase = "executing"

    def add_handoff(self, session_id: str, from_agent: str, to_agent: str, reason: str):
        if session_id in self.states:
            self.states[session_id].handoff_history.append({
                "from": from_agent,
                "to": to_agent,
                "reason": reason,
            })
            self.states[session_id].current_agent = to_agent
            logger.info("handoff_recorded", session_id=session_id, from_agent=from_agent, to_agent=to_agent)

    def set_emotion(self, session_id: str, emotion: str):
        if session_id in self.states:
            self.states[session_id].emotion = emotion
            logger.info("emotion_updated", session_id=session_id, emotion=emotion)

    def increment_turn(self, session_id: str):
        if session_id in self.states:
            self.states[session_id].turn_count += 1
