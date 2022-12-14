drop table if exists output.tests;

create table output.tests as (
    select test_id, kid_id, 
        CASE WHEN a.address in 
            ('5001 S MICHIGAN AVE', '1634 W POLK ST', '810 W MONTROSE AVE') 
        THEN null ELSE a.address_id END AS address_id,
        apt, test_lab.lab_id, t.provider_id,
        sample_date as date, analysis_date, reported_date,
        t.sample_type, 
        sample_date - k.date_of_birth AS age,
        first, first_bll6, first_bll10, increase, test_number,
        b.bll0, b.bll, b.lod, b.detected
    
    from aux.tests t
    join aux.test_lab using (test_id)
    join aux.blls b using (test_id)
    join aux.kid_tests_info kt using (test_id)
    left join aux.test_addresses ta using (test_id)
    left join aux.addresses a using (address_id)
    left join aux.kids k using (kid_id)
);

alter table output.tests add primary key (test_id);
create index on output.tests (kid_id, address_id);
