.PHONY: help install run test docker clean lint format

# Default target
help:
	@echo "Fraud Detection Graph Agent - Available Commands:"
	@echo ""
	@echo "  install    Install dependencies"
	@echo "  run        Start development server"
	@echo "  test       Run test suite"
	@echo "  docker     Build and run Docker container"
	@echo "  clean      Clean up temporary files"
	@echo "  lint       Run code linting"
	@echo "  format     Format code with black"
	@echo ""

# Install dependencies
install:
	pip install -r requirements.txt

# Start development server
run:
	uvicorn api.unified_app:app --reload --port 8001

# Run tests
test:
	pytest -v

# Run tests with coverage
test-cov:
	pytest --cov=src --cov=api --cov-report=html

# Build and run Docker container
docker:
	docker build -t fraud-graph-agent .
	docker run -p 8001:8001 fraud-graph-agent

# Clean up temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

# Run code linting
lint:
	flake8 src/ api/ tests/
	pylint src/ api/ tests/

# Format code
format:
	black src/ api/ tests/
	isort src/ api/ tests/
