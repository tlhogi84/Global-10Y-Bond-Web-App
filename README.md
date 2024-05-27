# Global 10-Year Bond Yields and Returns Web Application

Welcome to the Global 10-Year Bond Yields and Returns web application. 
This project is built using Python and Dash by Plotly to provide insights into global sovereign bond yields and returns.

## Live Demo

You can access the live application here: [Global 10Y Bond Web App](https://global-10y-bond-web-app.onrender.com/)

## Article Series on Medium

This project is part of a series of articles that guide you through the process of building this web application:

* **Part 1: Data collection and pre-processing**
  [Read Part 1](https://medium.com/@gdebeila/building-a-python-web-application-global-sovereign-10-year-bond-yields-and-returns-part-1-of-5-1c7be6da0daa)

* **Part 2: Calculating historical inflation rates**
  [Read Part 2](https://medium.com/@gdebeila/building-a-python-web-application-global-sovereign-10-year-bond-yields-and-returns-part-2-of-5-3abc3b3fec36)

* **Part 3: Estimating 10Y sovereign bond total returns from yield data**
  [Read Part 3](https://medium.com/@gdebeila/building-a-python-web-application-global-sovereign-10-year-bond-yields-and-returns-part-3-of-5-fbe5ddbf6a8f)

* **Part 4: Using Dash by Plotly to visualize the results**
  [Read Part 4](https://medium.com/@gdebeila/building-a-python-web-application-global-sovereign-10-year-bond-yields-and-returns-part-4-of-5-ff0f745778e2)

* **Part 5: Deploying the Python web application on Render**
  [Read Part 5](https://medium.com/@gdebeila/building-a-python-web-application-global-sovereign-10-year-bond-yields-and-returns-part-5-of-5-b2bc325dc8d3)

## Installation

### Prerequisites

- Python 3.x installed on your system

### Setup

1. Clone the repository to your local machine:

    ```sh
    git clone https://github.com/your-username/your-repository.git
    ```

2. Navigate to the project directory:

    ```sh
    cd your-repository
    ```

3. Create a virtual environment:

    ```sh
    python -m venv render_app_venv
    ```

4. Activate the virtual environment:

    - On Windows:

    ```sh
    render_app_venv\Scripts\activate
    ```

    - On macOS/Linux:

    ```sh
    source render_app_venv/bin/activate
    ```

5. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

To run the application locally, ensure that the virtual environment is activated and use the following command:

```sh
python app.py

## Project Structure

- **Collect_API_Data.ipynb:** Queries the OECD database and creates CSV files with raw data.
- **CPI_CALCS.ipynb:** Calculates inflation indices and creates a CSV file with the data.
- **LTRATES_Calcs.ipynb:** Processes data to create the resource file for the Dash app.
- **assets/Quandoyen_Banner.png:** Image asset used in the Dash app.
- **static/reset.css:** CSS file for consistent styling across browsers.
- **app.py:** Contains the code to run the Dash app.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries, please contact us at: info@quandoyen.com
