from openai import OpenAI
from os import getenv


client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=getenv("OPEN_AI_KEY") if getenv("OPEN_AI_KEY") else "",
)
