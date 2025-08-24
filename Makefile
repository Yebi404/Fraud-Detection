run:
	uvicorn api.app:app --reload --port 8001

test:
	pytest -q

docker:
	docker build -t fraud-graph-agent .
	docker run -p 8001:8001 fraud-graph-agent
