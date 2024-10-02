# NVIDIA AI Workbench: Introduction [![Open In AI Workbench](https://img.shields.io/badge/Open_In-AI_Workbench-76B900)](https://ngc.nvidia.com/open-ai-workbench/aHR0cHM6Ly9naXRodWIuY29tL05WSURJQS93b3JrYmVuY2gtZXhhbXBsZS1oeWJyaWQtcmFn)

<!-- Banner Image -->
<img src="https://developer-blogs.nvidia.com/wp-content/uploads/2024/07/rag-representation.jpg" width="100%">

<!-- Links -->
<p align="center"> 
  <a href="https://www.nvidia.com/en-us/deep-learning-ai/solutions/data-science/workbench/" style="color: #76B900;">:arrow_down: Download AI Workbench</a> •
  <a href="https://docs.nvidia.com/ai-workbench/" style="color: #76B900;">:book: Read the Docs</a> •
  <a href="https://docs.nvidia.com/ai-workbench/user-guide/latest/quickstart/example-projects.html" style="color: #76B900;">:open_file_folder: Explore Example Projects</a> •
  <a href="https://forums.developer.nvidia.com/t/support-workbench-example-project-agentic-rag/303414" style="color: #76B900;">:rotating_light: Facing Issues? Let Us Know!</a>
</p>

**Note:** [NVIDIA AI Workbench](https://www.youtube.com/watch?v=ntMRzPzSvM4) is the easiest way to get this RAG app running.
- NVIDIA AI Workbench is a <ins>free client application</ins> that you can install on your own machines.
- It provides portable and reproducible dev environments by handling Git repos and containers for you.
- Installing on a local system? Check out our guides here for [Windows](https://docs.nvidia.com/ai-workbench/user-guide/latest/installation/windows.html), [Local Ubuntu 22.04](https://docs.nvidia.com/ai-workbench/user-guide/latest/installation/ubuntu-local.html) and for [macOS 12 or higher](https://docs.nvidia.com/ai-workbench/user-guide/latest/installation/macos.html)
- Installing on a remote system? Check out our guide for [Remote Ubuntu 22.04](https://docs.nvidia.com/ai-workbench/user-guide/latest/installation/ubuntu-remote.html)

# Revolutionizing Project Risk Assessment with R.E.A.L.M.

In the complex world of reinsurance, underwriters face significant challenges when assessing risks for mega-projects. The traditional 5C approach (Character, Capacity, Capital, Collateral, and Conditions) has long been the industry standard, but its application often involves time-consuming manual processes and subjective interpretations. R.E.A.L.M. (Risk Evaluation and Assessment Leveraging Machine learning) addresses these pain points by digitizing and enhancing the 5C approach, providing underwriters with a powerful tool to streamline their work and improve decision-making.

## The Problem: Complexity in Mega-Project Risk Assessment

Underwriters in reinsurance companies, particularly those dealing with facultative reinsurance for large-scale projects, face several key challenges:

1. **Information Overload**: Mega-projects generate vast amounts of data, making it difficult for underwriters to process and analyze all relevant information efficiently.

2. **Subjectivity in Assessment**: Traditional methods often rely heavily on individual judgment, leading to potential inconsistencies in risk evaluation across different underwriters or projects.

3. **Time Constraints**: The pressure to make quick decisions can compromise the thoroughness of risk assessments, potentially leading to overlooked factors or inaccurate evaluations.

4. **Balancing Qualitative and Quantitative Factors**: Integrating both qualitative aspects (like management team reputation) and quantitative data (such as financial projections) into a cohesive risk profile is challenging.

5. **Keeping Up with Market Dynamics**: Rapidly changing market conditions and external factors can quickly render static risk assessments obsolete.

## How R.E.A.L.M. Solves These Problems

R.E.A.L.M. addresses these challenges by offering a comprehensive, AI-driven solution that enhances each aspect of the 5C approach:

### 1. Character Assessment

**Problem Solved**: Subjective evaluation of project management teams.
**R.E.A.L.M. Solution**: AI-driven analysis of historical performance data and track records, providing objective insights into the reliability and competence of project leadership.

### 2. Capacity Evaluation

**Problem Solved**: Time-consuming manual assessment of project feasibility.
**R.E.A.L.M. Solution**: Automated assessment tools that quickly analyze project timelines, resource allocation, and technical feasibility, offering a comprehensive view of the project's potential for success.

### 3. Capital Modeling

**Problem Solved**: Static financial projections that don't account for market volatility.
**R.E.A.L.M. Solution**: Real-time financial modeling and stress testing capabilities that provide dynamic insights into the project's financial health under various scenarios.

### 4. Collateral Appraisal

**Problem Solved**: Inconsistent valuation of project assets and guarantees.
**R.E.A.L.M. Solution**: Smart evaluation algorithms that assess project assets and guarantees, ensuring accurate and up-to-date valuation of collateral.

### 5. Conditions Analysis

**Problem Solved**: Difficulty in keeping up with rapidly changing market conditions.
**R.E.A.L.M. Solution**: AI-powered analysis of market conditions and external factors, providing real-time updates on the project's operating environment.

## Benefits for Underwriters

R.E.A.L.M. empowers underwriters in several key ways:

1. **Efficiency**: By automating data processing and analysis, R.E.A.L.M. significantly reduces the time required for risk assessment, allowing underwriters to handle more projects.

2. **Consistency**: The AI-driven approach ensures that all projects are evaluated using the same rigorous criteria, reducing subjectivity and potential biases.

3. **Depth of Analysis**: R.E.A.L.M.'s ability to process vast amounts of data quickly enables underwriters to consider a broader range of factors in their assessments.

4. **Dynamic Risk Profiles**: Real-time updates and stress testing capabilities allow underwriters to maintain up-to-date risk profiles and quickly adapt to changing conditions.

5. **Informed Decision-Making**: By providing comprehensive, data-driven insights, R.E.A.L.M. enables underwriters to make more confident and well-informed decisions.

## Project Structure

The R.E.A.L.M. project is organized as follows:

- `/code`: Contains the main Python files for the application
  - `app.py`: The main application file
  - `database.py`: Database configuration and session management
  - `models.py`: SQLAlchemy models for the database

- `requirements.txt`: Lists all the Python dependencies for the project
- `.gitignore`: Specifies intentionally untracked files to ignore
- `README.md`: This file, containing project documentation

## Quick Start

To get started with the R.E.A.L.M. project using NVIDIA Workbench, follow these steps:

1. **Set Up the Environment**:
    - Ensure you have NVIDIA Workbench installed.
    - Open the project in NVIDIA Workbench.

2. **Clone the Repository**:
    ```sh
    https://github.com/ekkirinaldi/REALM-Reinsurance-Eval-Analysis-for-Megaprojects.git
    ```

3. **Get your Perlplexity API**:
    - Get your API Key from Perplexity.

4. **Start the Application**:
    - Click "Open Chat" button.

5. **Access the Application**:
    - Open your web browser and navigate to your localhost. Paste your Perplexity API key, download the sample document, and you're ready to go.
