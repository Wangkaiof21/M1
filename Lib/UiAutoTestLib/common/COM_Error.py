import poco.utils.six as six


class MYError(Exception):
    """
    Base class for errors and exceptions of MY. It is Python3 compatible.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return f"资源异常"


class ResourceError(MYError):
    """
    书籍资源类异常
    """

    def __init__(self, error_message, book_id=None, chapter_progress=None, chat_progress=None, type=None):
        self.errorMessage = error_message
        self.book_id = book_id
        self.chapterProgress = chapter_progress
        self.chatProgress = chat_progress
        self.type = type

    def __str__(self):
        return "书籍资源异常,{0}".format(self.errorMessage)
