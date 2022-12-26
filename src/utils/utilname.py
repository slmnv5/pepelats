import random

words1 = ['we', 'go', 'to', 'how', 'in', 'pit', 'can', 'get', 'us', 'use', 'fat', 'of', 'us', 'are', 'any', 'one', 'of',
          'but', 'try', 'sad', 'old', 'new', 'hot', 'all', 'be', 'use', 'art', 'do', 'off', 'put', 'cat', 'in', 'pit',
          'man', 'he', 'she', 'see', 'out', 'up']

words2 = ['here', 'learn', 'about', 'moon', 'random', 'sent', 'like', 'secret', 'mode', 'slim', 'fart', 'many', 'only',
          'fame', 'fake', 'price', 'soon', 'rock', 'with', 'mood', 'happy', 'warm', 'cold', 'happy', 'happy', 'happy',
          'heavy', 'learn', 'post', 'ways', 'that', 'will', 'this', 'cover', 'milk', 'news', 'when', 'ways', 'lost',
          'love', 'must', 'sing', 'song', 'mine', 'this', 'them', ]


def generate_name() -> str:
    lst = random.choices(words1, k=1) + random.choices(words2, k=1) + \
          random.choices(words1, k=2)
    return "_".join(lst)


if __name__ == "__main__":
    def test():
        import logging

        logging.debug(generate_name())
        logging.debug(generate_name())
        logging.debug(generate_name())
        logging.debug(generate_name())


    test()
