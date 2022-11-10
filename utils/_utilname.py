import random

words = ['here', 'we', 'are', 'going', 'to', 'learn', 'about', 'how', 'moon', 'random', 'sent', 'in',
         'python', 'can', 'get', 'us', 'use', 'like', 'secret', 'mode', 'slim', 'fat', 'fart',
         'many', 'of', 'us', 'are', 'only', 'fame', 'fake', 'price', 'soon', 'war', 'pop', 'rock',
         'with', 'any', 'one', 'of', 'mood', 'but', 'try', 'happy', 'sad', 'old', 'new', 'cold', 'hot', 'heavy',
         'learn', 'all', 'post', 'ways', 'that', 'will', 'be', 'use', 'this', 'art', 'having',
         'cover', 'milk', 'news', 'of', 'when', 'ways', 'put', 'lost',
         'in', 'pit', 'man', 'love', 'must', 'sing', 'song', 'mine']


def generate_name(word_count: int = 4) -> str:
    lst = random.choices(words, k=word_count)
    return "_".join(lst)


if __name__ == "__main__":
    def test():
        print(generate_name())
        print(generate_name())
        print(generate_name())
        print(generate_name())


    test()
