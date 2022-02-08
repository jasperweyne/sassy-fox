from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from flatdict import FlatDict
import pandas as pd

# flatten array of nested dicts to array of single level dictionary
def flatten(data, delimiter=':'):
    # flatten data
    frame = pd.DataFrame(map(lambda x: FlatDict(x, delimiter=delimiter), data))

    # drop all columns that only contain empty values and return
    return frame.dropna(axis=1, how='all')

# unwrap nested arrays in an array of dicts to a single array of dicts
# this replicates the contents of the parent dict to all nested instances
# eg. [{'a': 'x', 'b':[1, 2]}] -> [{'a': 'x', 'b':1}, [{'a': 'x', 'b':2}]
def repl(data, ref):
    return [{**row, ref: k} for row in data for k in row[ref]]

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
            return False
        
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
        registrations = flatten(repl(result['current'], 'registrations'))
        return registrations.loc[registrations["registrations:deleted"].isnull(), ['name', 'registrations:created']]

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