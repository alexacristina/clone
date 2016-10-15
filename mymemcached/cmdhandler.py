import pickle

class CommandHandler(object):
    '''
    CommandHandler is Base class that represents
    the processing of the commands
    '''

    endreply = "END\r\n"
    stored_reply = "STORED\r\n"
    error_reply = "ERROR\r\n"
    notstored_reply = "NOT STORED\r\n"
    notfound_reply = "NOT FOUND\r\n"
    deleted_reply = "DELETED\r\n"

    def __init__(self, key, cache_mem):
        # with open(cache_file, 'rb') as handle:
        #     self.cache_mem = pickle.load(handle)
        self.key = key
        self.cache_mem = cache_mem

    # def _update_file(self):
    #     with open(self.cache_file, 'wb') as handle:
    #         pickle.dump(self.cache_mem, handle)

    def _store_value(self, params, data):
        if data.isdigit():
            self.cache_mem[self.key] = {'flag': params[0],
                                        'time': params[1],
                                        'object': int(data)}
        else:
            self.cache_mem[self.key] = {'flag': params[0],
                                        'time': params[1],
                                        'object': data}
        # _self._update_file()

    def retrieve_value(self, obj):
        if type(self.cache_mem[self.key]['object']) is str:
            return '%s %s %s' % (self.cache_mem[self.key]['flag'],
                                 len(obj), obj)
        else:
            return '%s %s %s' % (self.cache_mem[self.key]['flag'],
                                 len(str(obj)), str(obj))


class GetHandler(CommandHandler):

    '''
    GetHandler is the class that handles the functionality
    of the get command of the memcached tool
    '''

    def get_value(self, params=[], data=None):
        '''
        Checks if the value with the particular key exists
        in the cache memory
        '''
        if self.key in self.cache_mem:
            return self.cache_mem[self.key]
        else:
            return None

    def response_get(self):
        '''
        Returns the response of the 'get' command
        '''
        if self.get_value() is not None:

            obj = self.cache_mem[self.key]['object']
            return 'VALUE %s\r\n%s' % (self.retrieve_value(obj),
                                       self.endreply)
        else:
            return self.endreply


class SetHandler(CommandHandler):
    '''
    SetHandler is a class that handles the functionality
    of the 'set' command
    '''

    def set_value(self, params, data):
        '''Stores new value into the cache memory'''
        self._store_value(params, data)

    def response_set(self, params, data):
        '''Returns the status of the value to store'''
        if len(data) > (int(params[2]) + 2):
            return self.error_reply
        else:
            self.set_value(params, data[:-2])
            return self.stored_reply


class AddHandler(CommandHandler):
    '''
    Class that permits handling of a new value with
    having only a new key, doesn't permit overriding objects
    '''

    def add_value(self, params, data):
        '''
        Stores only a value with a new key in the cache
        memory
        '''
        if self.key in self.cache_mem:
            return False
        else:
            self._store_value(params, data)
            # self._update_file()
            return True

    def response_add(self, params, data):
        '''Returns the status of the 'add' command'''

        if len(data) > (int(params[2]) + 2):
            return self.error_reply
        else:
            return self.add_value(
                params,
                data[:-2]
            ) is True and self.stored_reply or self.notstored_reply


class ReplaceHandler(CommandHandler):

    def replace_value(self, params, data):
        if self.key in self.cache_mem:
            self._store_value(params, data)
            # self._update_file()
            return True
        else:
            return False

    def response_replace(self, params, data):
        if len(data) > (int(params[2]) + 2):
            return self.error_reply
        else:
            return self.replace_value(
                params,
                data[:-2]
            ) is True and self.stored_reply or self.notstored_reply


class DeleteHandler(CommandHandler):
    '''
    DeleteHandler permits the deletion of an object in the
    cache memory
    '''

    def response_delete(self):
        '''
        Delete the object from cache and return the status according
        to the presence of the object in the cache
        '''
        if self.key in self.cache_mem:
            self.cache_mem.pop(self.key)
            # self._update_file()
            return self.deleted_reply
        else:

            return self.notfound_reply
