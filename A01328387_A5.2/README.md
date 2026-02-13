---

# A01328387_A5.2 – Compute Sales

## Description

This project implements the **Compute Sales** program in Python. The application reads a product catalog and a sales record (JSON files), calculates the total sales, handles invalid data without stopping execution, measures execution time, and generates the output in the console and in a `SalesResults.txt` file.

The code follows **PEP8** standards and was validated using **flake8** and **pylint**.

---

## Project Structure

```
A01328387_A5.2/
│
├── Source/
│   └── computeSales.py
│
├── Tests/
│   ├── TC1/
│   ├── TC2/
│   └── TC3/
│
├── Results/
│   ├── TC1/
│   ├── TC2/
│   ├── TC3/
│   ├── flake8_results.png
│   └── pylint_results.png
│
└── README.md
```

* **Source/**: Main program.
* **Tests/**: Input JSON files for three test cases.
* **Results/**: Execution evidence, including:

  * `SalesResults.txt` for each test case
  * Console screenshots
  * Static analysis results.

---

## Execution

Run the program from the command line:

```bash
python Source/computeSales.py Tests/TC1/TC1.ProductList.json Tests/TC1/TC1.Sales.json
```

---

## Static Analysis

Static code analysis was performed using:

* **flake8**
* **pylint**

The images:

* `flake8_results.png`
* `pylint_results.png`

show **before and after results in the same screenshot**, where the final execution shows **0 errors** in both tools.

---

## Author

**A01328387**
Activity **A5.2**

---

