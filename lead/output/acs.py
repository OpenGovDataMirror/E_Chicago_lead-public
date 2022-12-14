from drain import util
import pandas as pd

engine = util.create_engine()
acs = pd.read_sql("select * from input.acs "
        "where length(census_tract_id::text) = 11", engine, 
        index_col=['census_tract_id', 'year'])

props = pd.DataFrame()
categories = set(c.split('_')[0] for c in acs.columns)

# get all columns
columns = {cat: [c for c in acs.columns 
        if c.startswith(cat) and not c.endswith('total')] 
            for cat in categories}

for category in categories:
    for c in columns[category]:
        props[c.replace('_count_', '_prop_')] = \
            acs[c] / acs[category + '_count_total']

    props[category + '_count'] = acs[category + '_count_total']

db = util.PgSQLDatabase(engine)
db.to_sql(props, name='acs', schema='output', 
        if_exists='replace', index=True, pk=['census_tract_id', 'year'])
