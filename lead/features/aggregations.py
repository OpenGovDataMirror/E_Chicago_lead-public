from lead.features.buildings import BuildingsAggregation
from lead.features.assessor import AssessorAggregation
from lead.features.tests import TestsAggregation
from lead.features.kids import KidsAggregation
from lead.features.permits import PermitsAggregation
from lead.features.violations import ViolationsAggregation
from lead.features.investigations import InvestigationsAggregation
from lead.features.events import EventsAggregation
from lead.features.wic import EnrollAggregation, BirthAggregation, PrenatalAggregation

from drain import util, data
from datetime import date
import sys
from drain.util import lru_cache

# default date is january 1
DATES = (date(y,1,1) for y in range (2014, 2016))

indexes = {
    'kid':'kid_id', 
    'address':'address_id',
    'building': 'building_id', 
    'complex':'complex_id', 
    'block':'census_block_id',
    'tract':'census_tract_id',
}

def get_deltas():
    return {
        'address': ['1y', '2y', '5y', '10y', 'all'],
        #'complex': ['1y', '2y', '5y', '10y', 'all'],
        'block': ['1y','2y','5y'],
        'tract': ['1y','2y','3y']
    }

wic = {'kid': ['all']}

def get_args(deltas):
    return dict(
        buildings = ['building', 'complex', 'block', 'tract'],
        assessor = ['address', 'building', 'complex', 'block', 'tract'],
        tests = deltas,
        investigations = deltas,
        #events = deltas,
        permits = deltas,
        kids = dict(kid=['all'], **deltas),
        violations = util.dict_subset(deltas, ('address', 'block')),
        wic_enroll = wic,
        wic_birth = wic,
        wic_prenatal = wic,
    )

args = get_args(get_deltas())

@lru_cache(maxsize=10)
def all_dict(dates=None, lag=None, parallel=True):
    dates = list(dates if dates is not None else DATES)
    delta = data.parse_delta(lag) if lag is not None else None

    aggs = {}

    for name, a in args.iteritems():
        cls = getattr(sys.modules[__name__], '%sAggregation' % name.split('_')[-1].title())
        if name in ('buildings', 'assessor'):
            aggs[name] = cls(indexes={n:indexes[n] for n in a}, parallel=parallel)
            for i in aggs[name].inputs: i.target=True
        else:
            spacedeltas = {n: (indexes[n], d) 
                    for n, d in a.iteritems()}
            dates_lagged = [d - delta for d in dates] if delta is not None and name.startswith('wic') else dates
            aggs[name] = cls(spacedeltas=spacedeltas, dates=dates_lagged, parallel=parallel)
            for i in aggs[name].inputs: i.target=True

    return aggs

def all():
    return all_dict().values()
