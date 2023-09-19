import random

words1 = ["brave", "slim", "wise", "smart", "good", "new", "first", "last", "long", "great", "little", "own", "other",
          "old", "right", "big", "high", "his", "small", "large", "next", "early", "young", "fast", "her",
          "fit", "same", "able", "happy", "nice", "deep", "black", "blue", "green"]

words2 = ["year", "people", "way", "day", "man", "thing", "woman", "life", "child", "world", "school",
          "state", "family", "student", "group", "country", "chair", "hand", "part", "place", "case",
          "week", "company", "system", "program", "question", "work", "wife", "number", "night",
          "point", "home", "water", "room", "mother", "area", "money", "story", "fact", "month", "lot",
          "right", "study", "book", "eye", "job", "word", "line", "issue", "side", "kind", "head",
          "house", "service", "friend", "father", "power", "hour", "game", "line", "end", "member", "law",
          "car", "city", "link", "name", "president", "team", "minute", "idea", "kid", "body",
          "case", "back", "parent", "face", "others", "level", "office", "door", "health", "person",
          "art", "war", "history", "party", "result", "change", "morning", "reason", "smile", "girl",
          "guy", "moment", "air", "teacher", "force", "run", "smile", "moon", "pen", "ring", "square"]


def generate_name() -> str:
    while True:
        wrd1 = random.choice(words1)
        wrd2 = random.choice(words2)
        if len(wrd1) + len(wrd2) < 18:
            break
    return f"{wrd1}_{wrd2}"
