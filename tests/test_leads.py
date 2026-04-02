def test_run_agent_and_list_leads(client):
    run = client.post('/run-agent')
    assert run.status_code == 200
    payload = run.json()
    assert payload['candidates_seen'] >= 1

    leads = client.get('/leads')
    assert leads.status_code == 200
    data = leads.json()
    assert len(data) >= 1
    assert data[0]['company_name']


def test_get_and_delete_lead(client):
    client.post('/run-agent')
    leads = client.get('/leads').json()
    lead_id = leads[0]['id']

    get_resp = client.get(f'/leads/{lead_id}')
    assert get_resp.status_code == 200

    del_resp = client.delete(f'/leads/{lead_id}')
    assert del_resp.status_code == 200
    assert del_resp.json()['deleted'] is True
