# KIBERA-8-SLUM-SAFARIS
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE))]
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.1.1-blue.svg)](https://pypi.org/project/Flask/)
[![Flask-RESTx](https://img.shields.io/badge/Flask--RESTx-0.5.1-blue.svg)](https://pypi.org/project/flask-restx/)
[![JWT](https://img.shields.io/badge/JWT-2.0.1-blue.svg)](https://pypi.org/project/PyJWT/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13.5-blue.svg)](https://www.postgresql.org/)


## Table of Content

- [Project Description](#project-description)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Contributing](#contributing)
- [Authors](#authors)
- [Licence](#license)

## Project Description 

 This project is aimed at managing and showcasing inventories and stories of beneficiary organizations associated with tour donations. It provides a platform to maintain detailed records of these organizations and their impactful stories, making it easier for stakeholders and donors to understand the value of their contributions.

 ## Features 

1. **User Registration and Login** - Users can create accounts or log in using their credentials.

2. **Organization management** - Admin accounts can manage organizations by approving and deleting ther requests

3. **Beneficiary Organization** - Maintanance of the beneficiaries list.

4. **Stories** - Share stories and updates about organizations to inspire donors and stakeholders.

5. **Inventory Tracking**- Maintain records of items, resources, or funds donated to each organization.

6. **Search and Filter** - Easily find and filter organizations, stories, and inventories based on various criteria.


## Technologies Used

- Backend: POSTGRESQL, Python Flask
- Authentication: JWT (JSON Web Tokens)

## Installation

1. Clone the Repository: 
```bash
    git clone git@github.com:Noelle-Wavinya-Maingi/Kibera-8-Slum-Safaris.git
```
2. Activate the environment 
```bash
    pipenv shell
```
3. Install the requirements
```bash
pip install -r requirements.txt
```
4. Navigate to the server folder
```bash
cd server
```
5. Start the server
```bash
gunicorn app:app
```

### Contributing 

If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and test thoroughly.
4. Create a pull request explaining the changes you've made.

### Authors : 
[Noelle Maingi](https://github.com/Noelle-Wavinya-Maingi)
[Ian Odhiambo](https://github.com/Noelle-Wavinya-Maingi)
[Kipngenoh A. Rotich](https://github.com/Noelle-Wavinya-Maingi)

### License
This project is licensed under the MIT [License](LICENCE).