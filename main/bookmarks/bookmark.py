class Bookmarks:
    """Session based class for bookmarks management"""

    def __init__(self, request):
        self._session = request.session
        self.bookmarks: dict = self._session.get('bookmarks')
        if not self.bookmarks:
            self.bookmarks = self._session['bookmarks'] = {}

    def add_bookmark(self, topic_slug: str, topic_name: str):
        if topic_slug not in self.bookmarks:
            self.bookmarks[topic_slug] = topic_name
            self._save()

    def remove_bookmark(self, topic_slug: str):
        if topic_slug in self.bookmarks:
            del self.bookmarks[topic_slug]
            self._save()

    def _clear(self):
        del self._session['bookmarks']
        self._session.modified = True

    def _save(self):
        self._session['bookmarks'] = self.bookmarks
        self._session.modified = True

    def __len__(self):
        return len(self.bookmarks)
