import pandas as pd
from drain import util, dedupe

engine = util.create_engine()

edges = pd.read_sql("""
with kid_ids as (
    SELECT id, first_name, last_name, date_of_birth, coalesce(canon_id, id) kid_id
    FROM dedupe.infants LEFT JOIN dedupe.entity_map0 using (id)
)

SELECT k1.kid_id id1, k2.kid_id id2 from
kid_ids k1 JOIN
(SELECT min(kid_id) id2, first_name, last_name, date_of_birth from kid_ids group by 2,3,4 having count(*) > 1) t
using (first_name, last_name, date_of_birth)
JOIN kid_ids k2 on id2 = k2.kid_id
where k1.kid_id > k2.kid_id
group by 1,2
""", engine)

components = dedupe.components_to_df(dedupe.get_components(edges))

db = util.PgSQLDatabase(engine)

db.to_sql(frame=components,
          if_exists='replace',
          name='exact_matches',
          schema='dedupe',
          index=False)
