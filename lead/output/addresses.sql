DROP TABLE IF EXISTS output.addresses;

CREATE TABLE output.addresses AS (

with residential_addresses as (
    select address_id from aux.test_addresses
    UNION
    select address_id from aux.kid_wic_addresses
    UNION
    select address_id from output.investigations
),

residential_complexes as (
    select complex_id
    from aux.addresses a 
    left join aux.complex_addresses ca using (address_id)
    left join aux.assessor using (address)
    group by complex_id having bool_or(residential > 0)
)

select a.address_id address_id, a.address, ca.building_id, ca.complex_id,
    cast(a.census_tract_id as double precision), cast(a.census_block_id as double precision), a.ward_id, a.community_area_id,
    st_y(a.geom) address_lat,
    st_x(a.geom) address_lng,
    (rc.complex_id is not null) or (ta.address_id is not null) as address_residential
from aux.addresses a join aux.complex_addresses ca using (address_id)
left join residential_complexes rc using (complex_id)
left join residential_addresses ta using(address_id)
);

alter table output.addresses add primary key (address_id);
