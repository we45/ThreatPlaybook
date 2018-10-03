from threat_playbook.ThreatPlaybook import ThreatPlaybook

TEST_FILE_PATH = '/Users/abhaybhargav/Documents/Code/Python/ThreatPlaybook/threat_playbook/threat_playbook/test/artefacts/'

tp = ThreatPlaybook('test', db_name = 'test_tp')

def test_load_threat_model():
    tp.find_or_load_cases_from_directory(case_path=TEST_FILE_PATH)

def test_generate_threat_maps():
    tp.generate_threat_maps()

def test_generate_markdown_report():
    tp.write_markdown_report(gen_diagram = "False")