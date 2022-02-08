from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from flatdict import FlatterDict
from dateutil.parser import parse
import pandas as pd

# flatten array of nested data to array of single level dictionary
def flatten(data, delimiter=':'):
    # flatten data
    frame = pd.DataFrame(map(lambda x: FlatterDict(x, delimiter=delimiter), data))

    # drop all columns that only contain empty values and return
    return frame.dropna(axis=1, how='all')

# create a client
class Data:
    _authenticated = False

    def __init__(self, url, token=None):
        cookies = {}
        if token:
            cookies['KIWI_PHPSESSID'] = token
            self._authenticated = True

        transport = RequestsHTTPTransport(url, cookies=cookies)
        self.client = Client(
            transport=transport,
            fetch_schema_from_transport=True,
        )
    
    @property
    def authenticated(self):
        return self._authenticated

    @property
    def admin(self):
        if not self._authenticated:
            return false
        
        query = gql('''
            {
                user {
                    isAdmin
                }
            }
        ''')

        result = self.client.execute(query)
        return result['user']['isAdmin']

    def activities(self):
        query = gql('''
            {
                current {
                    name
                    description
                    author {
                        name
                    }
                    location {
                        address
                    }
                }
            }
        ''')

        result = self.client.execute(query)
        return flatten(result['current'])

    def registrations(self):
        query = gql('''
            {
                current {
                    name
                    registrations {
                        created
                        deleted
                    }
                }
            }
        ''')

        result = self.client.execute(query)
        return pd.DataFrame([[activity['name'], parse(reg['created'])] for activity in result['current'] for reg in activity['registrations'] if not reg['deleted']], columns=['name', 'registration'])

    def user_relations(self):
        query = gql('''
            {
                user {
                    relations {
                        group {
                            name
                        }
                    }
                }
            }
        ''')

        result = self.client.execute(query)
        return flatten(result['user']['relations'])
    
    def user_registrations(self):
        query = gql('''
            {
                user {
                    registrations {
                        activity {
                            name
                            start
                        }
                        option {
                            price
                        }
                    }
                }
            }
        ''')

        result = self.client.execute(query)
        return flatten(result['user']['registrations'])

    def groups(self):
        if not self._authenticated:
            raise Exception("Source unauthenticated")
        
        query = gql('''
            {
                groups {
                    name
                }
            }
        ''')

        result = self.client.execute(query)
        return flatten(result['groups'])