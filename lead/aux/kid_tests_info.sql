drop table if exists aux.kid_tests_info;

create table aux.kid_tests_info as (

WITH tests AS (
    select kid_id, test_id, address_id, sample_date, b.bll, 
        row_number() OVER w as test_number,
        -- last_bll used to compute lagged max(bll) series for increase column below
        lag(b.bll) over w as last_bll
    from aux.tests 
    join aux.blls b using (test_id)
    join aux.kid_tests using (test_id) 
    join aux.kids using (kid_id)
    left join aux.test_addresses using (test_id)
    WHERE kids.date_of_birth is not null AND sample_date >= kids.date_of_birth
    -- order by address_id to ensure first_sample_address_id if availale
    WINDOW w AS (partition by kid_id order by sample_date asc, address_id is not null desc)
),

first_bll6 AS (
    select distinct on(kid_id) kid_id,test_id
    from tests
    where bll >= 6
    order by kid_id, sample_date asc, address_id is not null desc, test_id asc
),

first_bll10 AS (
    select distinct on(kid_id) kid_id,test_id
    from tests
    where bll >= 10
    order by kid_id, sample_date asc, address_id is not null desc, test_id asc
),

-- calculate the previous maximum bll from this child until this test
lag AS (
    select test_id, 
        max(last_bll) over (partition by kid_id order by sample_date asc) as max
    from tests
)

select tests.kid_id, test_id,
    first_bll6.test_id is not null as first_bll6,
    first_bll10.test_id is not null as first_bll10,
    test_number = 1 as first,
    test_number,
    coalesce(bll > lag.max, true) as increase -- coalesce to true so first test is an "increase"
from tests 
join lag using (test_id)
left join first_bll6 using (test_id)
left join first_bll10 using (test_id)
);


ALTER TABLE aux.kid_tests_info ADD PRIMARY KEY (test_id);
