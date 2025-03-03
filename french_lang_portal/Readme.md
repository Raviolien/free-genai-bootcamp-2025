# Setup
## Create and acitvate virtual environment
```sh
python3 -m venv venv 
source venv/bin/activate
```

## Install dependencies
```sh
pip install -r requirements.txt
```

## Install Vito
```sh	
npm i -D @vitejs/plugin-react-swc
```

## Setup database
```sh
cd backend-flask
invoke init-db
```

## Run the app
### Run backend
```sh
python app.py
```

### Run frontend
```sh
cd frontend-react
npm run dev
```