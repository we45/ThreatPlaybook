from threat_playbook.ThreatPlaybook import ThreatPlaybook

TEST_FILE_PATH = '/Users/abhaybhargav/Documents/Code/Python/ThreatPlaybook/threat_playbook/threat_playbook/test/artefacts/'

tp = ThreatPlaybook('Test ThreatPlaybook', db_name = 'test_tp')

def test_project_name_value():
    assert tp.project.name == 'test_threatplaybook'

def test_load_threat_model():
    tp.find_or_load_cases_from_directory(case_path=TEST_FILE_PATH)

def test_generate_threat_maps():
    tp.generate_threat_maps()

def test_generate_markdown_report():
    tp.write_markdown_report(gen_diagram = "False")

def test_create_and_link_recon():
    tp.find_or_create_target(name = 'test_target', uri='http://www.target.t')
    tp.create_and_link_recon(tool = 'zap', target_name='test_target')