import unittest

from pyramid import testing


class TutorialViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_hello_world(self):
        request = testing.DummyRequest()
        response = hello_world(request)
        self.assertEqual(response.status_code, 200)



#import unittest
#import transaction
#
#from pyramid import testing
#
#from .models import DBSession
#
#
#class TestMyViewSuccessCondition(unittest.TestCase):
#    def setUp(self):
#        self.config = testing.setUp()
#        from sqlalchemy import create_engine
#        engine = create_engine('sqlite://')
#        from .models import (
#            Base,
#            MyModel,
#            )
#        DBSession.configure(bind=engine)
#        Base.metadata.create_all(engine)
#        with transaction.manager:
#            model = MyModel(name='one', value=55)
#            DBSession.add(model)
#
#    def tearDown(self):
#        DBSession.remove()
#        testing.tearDown()
#
#    def test_passing_view(self):
#        from .views import my_view
#        request = testing.DummyRequest()
#        info = my_view(request)
#        self.assertEqual(info['one'].name, 'one')
#        self.assertEqual(info['project'], 'amnesia')
#
#
#class TestMyViewFailureCondition(unittest.TestCase):
#    def setUp(self):
#        self.config = testing.setUp()
#        from sqlalchemy import create_engine
#        engine = create_engine('sqlite://')
#        from .models import (
#            Base,
#            MyModel,
#            )
#        DBSession.configure(bind=engine)
#
#    def tearDown(self):
#        DBSession.remove()
#        testing.tearDown()
#
#    def test_failing_view(self):
#        from .views import my_view
#        request = testing.DummyRequest()
#        info = my_view(request)
#        self.assertEqual(info.status_int, 500)
