from drain.aggregation import SimpleAggregation
from drain.aggregate import Count, Aggregate, Proportion, Fraction
from drain.data import FromSQL

import numpy as np

CLASSES = ['residential', 'incentive', 'multifamily', 'industrial', 'commercial', 'brownfield', 'nonprofit']

assessor = FromSQL(query="select *, coalesce(nullif(apartments, 0), 1) as units "
                "from aux.assessor "
                "join output.addresses using (address)",
                tables=['aux.assessor', 'output.addresses'])
assessor.target = True

class AssessorAggregation(SimpleAggregation):
    def __init__(self, indexes, parallel=False):
        SimpleAggregation.__init__(self, inputs=[assessor], indexes=indexes, prefix='assessor', parallel=parallel)

    @property
    def aggregates(self):
        return [
            Count(),
            Aggregate('count', 'mean', 'assessents'),
            Aggregate(lambda a: a.land_value / 100000, 'mean', name='land_value'),
            Aggregate(['min_age', 'max_age'], ['min', 'mean', 'max']),

            # residential total value and average value
            Fraction(
                Aggregate(lambda a: a.total_value.where(a.residential > 0) / 100000,
                          'sum', 'residential_total_value', fname=False),
                Aggregate(lambda a: a.units.where(a.residential > 0),
                          'sum', name='residential_units', fname=False),
                include_numerator=True, include_denominator=True
            ),
            # non-residential total and average value
            Fraction(
                Aggregate(lambda a: a.total_value.where(a.residential == 0) / 100000,
                          'sum', 'non_residential_total_value', fname=False),
                Aggregate(lambda a: a.units.where(a.residential == 0),
                          'sum', name='non_residential_units', fname=False),
                include_numerator=True, include_denominator=True
            ),

            Aggregate('apartments', 'mean'),
            Aggregate('units', 'mean'),
            Aggregate(lambda a: a.rooms / a.units, 'mean', name='rooms_per_unit'),
            Aggregate(lambda a: a.beds / a.units, 'mean', name='beds_per_unit'),
            Aggregate(lambda a: a.baths / a.units, 'mean', name='baths_per_unit'),

            Proportion(lambda a: a.owner_occupied > 0, name='owner_occupied'),
            Proportion([lambda a, c=c: a[c] > 0 for c in CLASSES],
                    name=CLASSES)
        ]

