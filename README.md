# WatchTower: DDoS Detection with Autoencoders

## Introduction

This project aims to detect Distributed Denial of Service (DDoS) attacks using a hybrid model combining autoencoders and XGBoost. The backend is built using Django and Django REST Framework, while the frontend is developed with React.

## Prerequisites

**NOTE:** You need Anaconda for this environment; otherwise, it will not work.

- Anaconda: [Download and install Anaconda](https://www.anaconda.com/products/individual)
- Node.js and npm: [Download and install Node.js and npm](https://nodejs.org/)

## Setting up

### Setup the Environment

1. Clone the repository:
   ```sh
   git clone https://github.com/username/project-name.git
   cd project-name
   ```

2. Run the setup script:
   ```sh
   ./setup.sh
   ```

3. Activate your conda environment:
   ```sh
   conda activate myenv
   ```

## Backend (Django)

### Installation

1. Navigate to the backend directory:
   ```sh
   cd backend
   ```

2. Apply database migrations:
   ```sh
   cd watchtower
   python manage.py makemigrations
   python manage.py migrate
   ```

### Running the Application

1. Start the development server:
   ```sh
   python manage.py runserver
   ```

2. Access the backend API at: `http://127.0.0.1:8000/`

### Configuration

- Ensure `INSTALLED_APPS` in `backend/watchtower/watchtower/settings.py` includes `'alertsystem'` and `'rest_framework'`.

### Testing

Run tests for the backend:
   ```sh
   python manage.py test
   ```

### Deployment

Instructions for deploying the backend to a production environment (e.g., using Gunicorn, Nginx, and Docker) can be added here.

## Frontend (React)

### Installation

1. Navigate to the frontend directory:
   ```sh
   cd ../../frontend
   ```

2. Install dependencies:
   ```sh
   npm install
   ```

### Running the Application

1. Start the development server:
   ```sh
   npm start
   ```

2. Access the frontend at: `http://localhost:3000/`

### Building for Production

Build the frontend for production:
   ```sh
   npm run build
   ```

### Testing

Run tests for the frontend:
   ```sh
   npm test
   ```

## Additional Information

### Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

### License

This project is licensed under the GNU License. See the LICENSE file for details.

### Troubleshooting

Common issues and solutions:

- **SQLite3 Error:** If you encounter an SQLite3 error on macOS, try reinstalling SQLite via conda:
  ```sh
  conda install -c conda-forge sqlite -y
  ```

- **React Project Naming Error:** Ensure your React project name does not contain capital letters or special characters.

### Contact

For questions or support, please open an issue in the repository or contact the project maintainer.
