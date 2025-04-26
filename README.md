# Metta Motto

This package provides integration of MeTTa and LLMs for prompt tamplates, guidance, and chaining as well as composition with other agents.

## Installation

The main requirement is [MeTTa](https://github.com/trueagi-io/hyperon-experimental/).

The project itself can be installed via
```bash
git clone git@github.com:zarqa-ai/metta-motto.git
cd metta-motto
```

### Using-pip

Run the following command to install the project using pip:
```bash
pip install metta-motto
```

## Usage

The package can be used both as a Python package
```python
import motto
```

and MeTTa extention
```
!(import! &self motto)
```

Please, refer to the [tutorial](https://github.com/zarqa-ai/metta-motto/tree/main/tutorial) and [examples](https://github.com/zarqa-ai/metta-motto/tree/main/examples). [Tests](https://github.com/zarqa-ai/metta-motto/tree/main/tests) can also be considered in addition.

## Tests

The unit tests can be executed via

```bash
cd tests
pytest
```
