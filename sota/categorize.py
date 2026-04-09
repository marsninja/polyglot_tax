import os
from enum import Enum

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate


class Category(str, Enum):
    WORK = "work"
    PERSONAL = "personal"
    SHOPPING = "shopping"
    HEALTH = "health"
    OTHER = "other"


_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Categorize the following todo item into exactly one of these categories: "
     "WORK, PERSONAL, SHOPPING, HEALTH, OTHER. "
     "Respond with ONLY the category name, nothing else."),
    ("human", "{title}"),
])

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        )
    return _llm


async def categorize(title: str) -> str:
    try:
        llm = _get_llm()
        chain = _prompt | llm
        result = await chain.ainvoke({"title": title})
        cat = result.content.strip().lower()
        # Validate against enum
        if cat in [c.value for c in Category]:
            return cat
        return "other"
    except Exception:
        return "other (setup AI key)"
