setup:
	python -m pip install -e ".[dev,dashboard]"
synth:
	renaltwin data synth --n-patients 3000 --seed 42
train:
	renaltwin train --seed 42
db-init:
	renaltwin db init
seed:
	renaltwin demo seed
api:
	uvicorn renaltwin.api.main:app --host 127.0.0.1 --port 8000
dashboard:
	streamlit run dashboard/app.py --server.port 8501
test:
	pytest -q
demo: synth train db-init seed
clean-db:
	rm -f artifacts/renaltwin.db
