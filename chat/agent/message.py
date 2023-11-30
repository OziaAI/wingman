from dataclasses import dataclass
from typing import TypedDict

class UserMessageAction(TypedDict):
    buttonText: str
    messageToSend: str

class WingmanMessageOption(TypedDict):
    embeddedUrl: str | None
    acceptAction: UserMessageAction | None
    denyAction: UserMessageAction | None

@dataclass
class WingmanMessage:
    message: str
    option: WingmanMessageOption | None
