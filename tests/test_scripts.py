from hyperon import MeTTa, E
from pathlib import Path
pwd = Path(__file__).parent

def process_exceptions(results):
    for result in results:
        assert result in [[E()], []]

def test_scripts():
    process_exceptions(MeTTa().import_file(f"{pwd}/basic_direct_call.metta"))
    process_exceptions(MeTTa().import_file(f"{pwd}/basic_function_call.metta"))
    process_exceptions(MeTTa().import_file(f"{pwd}/basic_script_call.metta"))
