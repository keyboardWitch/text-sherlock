""" 
base.py
Created by: Christopher Bess
Copyright: 2011
"""

from core import settings

## Indexer Base Classes

class FileIndexer(object):
    """Represents the base file indexer object. All methods are required to be implemented.
    """
    def __init__(self, *args, **kwargs):
        pass

    def doc_count(self):
        """Returns the total document count
        """
        raise NotImplementedError

    def open_index(self, path, *args, **kwargs):
        """Opens the index at the specified path
        """
        raise NotImplementedError

    def create_index(self, path, *args, **kwargs):
        """Creates the index at the specified path
        """
        raise NotImplementedError

    def begin_index_file(self, filepath):
        """Called before file indexing operations. Usually used to
        open document writers for the indexer.
        """
        pass

    def index_file(self, filepath, *args, **kwargs):
        """Indexes and stores the file at the specified path
        """
        raise NotImplementedError

    def end_index_file(self, filepath):
        """Called after file indexing operations. Usually used to
        commit the changes to the indexer.
        """
        pass

    def index_exists(self, path):
        """Returns True if an index exist at the specified path, False otherwise
        """
        raise NotImplementedError

    
## Searcher Base Classes

class FileSearcher(object):
    def __init__(self, indexer):
        """Initializes this instance
        :param indexer: The sherlock.Indexer instance that is assigned to this search.
        """
        self._indexer = indexer
        pass

    def find_text(self, text, pagenum=1, limit=10):
        """Returns the search results for the given user text input.
        :param pagenum: The page number of the search results.
        :param limit: The max number of results to return as the results.
        """
        raise NotImplementedError

    def find_path(self, path):
        """Returns the search result for the target path.
        """
        raise NotImplementedError

    @property
    def indexer(self):
        return self._indexer


class SearchResults(list):
    """Represents the search results
    """
    searcher = None
    # the next page number, use -1 to indicate no next page available
    next_pagenum = -1
    # the previous page number, use -1 to indicate no prev page available
    prev_pagenum = -1
    # the max number of page results to process/return
    limit = 10
    # the total number of results from the search
    total_count = 0
    # the current page number that will be displayed, -1 to indicate that it has not been set
    pagenum = -1
    
    def __init__(self, searcher, hits, **kwargs):
        """Initializes this Results instance
        :param searcher: sherlock.Searcher instance that created the hits
        :param hits: sequence of raw search result objects from the search
        :param kwargs: {
            total_count = Total number of results for the entire search
            pagenum = The page of the expected results
            limit = The maximum number of results to store
        }
        """
        super(SearchResults, self).__init__()
        self._items = []
        self.total_count = kwargs.get('total_count', -1)
        self.pagenum = kwargs.get('pagenum', 0)
        self.limit = kwargs.get('limit', settings.RESULTS_PER_PAGE)
        self._searcher = searcher
        self.next_pagenum = self.pagenum + 1
        self.prev_pagenum = -1
        if self.pagenum > 1 and self.limit > 0:
            self.prev_pagenum = self.pagenum - 1
        self.process_hits(hits)
        # calculate last page
        if self.pagenum * self.limit >= self.total_count:
            self.next_pagenum = -1
        pass

    @property
    def items(self):
        """Returns the transformed results that represent the internal list elements
        """
        return self._items

    @property
    def searcher(self):
        return self._searcher

    def process_hits(self, hits):
        """Processes the raw search result hits. It must add the processed
        hit as a base.SearchResult instance, then pass it to `this.append` to store
        them as a result.
        """
        raise NotImplementedError


class SearchResult(object):
    """Represents a sherlock result
    """
    context = ''
    path = None
    filename = None
    # the path within the index path. The full file path without the index path prepended.
    index_path = None
    
    def __init__(self, hit, indexer, **kwargs):
        """Initializes this Result instance
        :param hit: The raw indexer search hit this instance represents
        :param indexer: The sherlock.Indexer that holds this search result
        @param kwargs {
            path = Path of the file this result represents
            filename = Filename of the file
        }
        """
        # the textual context of the hit
        self.context = ''
        self.path = kwargs.get('path')
        self.filename = kwargs.get('filename')
        # build index path
        path = settings.INDEX_PATH % { 'sherlock_dir' : settings.ROOT_DIR }
        self.index_path = self.path.replace(path, '')
        self.process_hit(hit)
        pass

    def process_hit(self, hit):
        """Process the result data, it should read the original file to produce
        the processed search result.
        @remark For now it only processes to get the context for the result. The
        processing operation should populate the default class properties.
        """
        raise NotImplementedError
        
    def append_line(self, lines, text):
        """ Appends the text to the target lines """        
        lines.append("<div class='line'>%s</div>\n" % text.strip())
        pass