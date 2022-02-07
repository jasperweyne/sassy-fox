from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from flatdict import FlatterDict
import pandas as pd
import streamlit as st

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
                    deadline
                    registrations {
                        created
                        deleted
                    }
                }
            }
        ''')

        result = self.client.execute(query)
        return flatten(result['current'])

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