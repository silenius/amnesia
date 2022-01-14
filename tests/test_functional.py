#def test_my_view_success(testapp, dbsession):
#    from amnesia.modules.document import Document
#
#    model = Document(title='adoc', description='adescr', body='<html></html>')
#    dbsession.add(model)
#    dbsession.flush()
#
#    res = testapp.get('/', status=200)
#    assert res.body
#
#def test_notfound(testapp):
#    res = testapp.get('/badurl', status=404)
#    assert res.status_code == 404
