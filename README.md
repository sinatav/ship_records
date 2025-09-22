# README for ship_records

## Project Overview
`ship_records` is a Python repository that provides utilities and a pipeline for processing historical ships and voyages datasets. This project aims to facilitate the analysis of maritime data by providing various tools and methodologies to handle, manipulate, and visualize historical voyage information.

## Installation Instructions
To set up this project, you need to have Python installed on your machine. Additionally, you'll need to install the required dependencies specified in the `requirements.txt` or in the `pyproject.toml` file.

1. Clone the repository:
   ```bash
   git clone https://github.com/sinatav/ship_records.git
   cd ship_records
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage Guide
Once you have installed the required dependencies, you can start using the utilities provided in the notebooks located in the `notebooks/` directory. Here are a few example commands to get you started:

- To analyze voyage probabilities, you can explore `notebooks/probs.ipynb`:
  ```bash
  jupyter notebook notebooks/probs.ipynb
  ```

- To work with all voyages data, try `notebooks/all_voyages.ipynb`:
  ```bash
  jupyter notebook notebooks/all_voyages.ipynb
  ```

- If you want to conduct experiments, check `notebooks/experiments_1_2.ipynb`:
  ```bash
  jupyter notebook notebooks/experiments_1_2.ipynb
  ```

You can navigate through other notebooks for various analyses such as replacing data, checking edges, and more.

## Project Structure
The repository contains the following key files and directories:

```
.
├── notebooks/
│   ├── Untitled6.ipynb
│   ├── all_voyages.ipynb
│   ├── edges.ipynb
│   ├── experiments_1_2.ipynb
│   ├── probs.ipynb
│   ├── prob_given.ipynb
│   ├── replace x (1).ipynb
│   ├── replace x (1)-2.ipynb
│   └── replace x.ipynb
└── requirements.txt
```

* The `notebooks/` directory contains Jupyter notebooks that provide interactive environments for data analysis and experimentation.
* `requirements.txt` contains all dependencies required for the project.

## Testing Instructions
Tests are included in the repository to ensure that the utilities work as expected. To run the tests, make sure to have `pytest` installed, then execute:

```bash
pytest tests/
```

(Note: Ensure that the test files directory is created and contains relevant test scripts to validate the functionalities of the utilities.)

## License Information
This repository does not specify a license. Please check for any license updates or contributions before use. If you plan to use the code in a project or for distribution, ensure compliance with any applicable legal requirements.

---

We hope you find `ship_records` useful for your historical maritime data analyses! For any issues or contributions, feel free to raise an issue or a pull request on GitHub.