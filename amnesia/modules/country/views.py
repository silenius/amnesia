import logging

from pyramid.view import view_defaults
from pyramid.view import view_config

from amnesia.modules.country import Country
from amnesia.modules.country import CountryEntity
from amnesia.modules.country import CountryResource
from amnesia.modules.country import CountrySchema
from amnesia.views import BaseView

log = logging.getLogger(__name__)


def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__, categories=('pyramid', 'amnesia'))


@view_defaults(
    context=CountryResource
)
class CountryCRUD(BaseView):

    #######
    # GET #
    #######

    @view_config(
        request_method='GET',
        accept='application/json',
        renderer='json'
    )
    def get(self):
        schema = self.schema(CountrySchema)

        countries = self.dbsession.execute(
            self.context.query().order_by(
                Country.name
            )
        ).scalars().all()
                                   
        return schema.dump(countries, many=True)
