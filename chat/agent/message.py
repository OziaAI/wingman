from dataclasses import dataclass
from typing import TypedDict


class UserMessageAction(TypedDict):
    buttonText: str
    messageToSend: str


class WingmanMessageOption(TypedDict):
    embeddedUrl: str | None
    acceptAction: UserMessageAction | None
    denyAction: UserMessageAction | None


class WingmanMessageContext(TypedDict):
    disconnect: bool


class WingmanMessage(TypedDict):
    message: str
    context: WingmanMessageContext
    option: WingmanMessageOption | None
