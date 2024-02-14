from hyperon import MeTTa
from pathlib import Path
pwd = Path(__file__).parent

def test_scripts():
    MeTTa().load_module_at_path(f"{pwd}/basic_direct_call.metta")
    MeTTa().load_module_at_path(f"{pwd}/basic_function_call.metta")
    MeTTa().load_module_at_path(f"{pwd}/basic_script_call.metta")
    MeTTa().load_module_at_path(f"{pwd}/basic_agent_call.metta")
    MeTTa().load_module_at_path(f"{pwd}/metta_chat.metta")
    MeTTa().load_module_at_path(f"{pwd}/nested_script_direct.metta")
    MeTTa().load_module_at_path(f"{pwd}/nested_dialog_call.metta")
    MeTTa().load_module_at_path(f"{pwd}/sparql_functions_test.metta")
