from threat_playbook.ThreatPlaybook import ThreatPlaybook
import inspect, os

cur_file = inspect.getfile(inspect.currentframe())
cur_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


TEST_FILE_PATH = os.path.join(cur_path, "artefacts")
ZAP_FILE = os.path.join(cur_path, 'scan_files/ctf.json')

tp = ThreatPlaybook('test_threatplaybook', db_name = 'test_tp')

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

def test_load_zap_results_to_db():
    tp.parse_zap_json(ZAP_FILE, 'test_target', 'http://www.target.t')