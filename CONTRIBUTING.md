# Contributing to Fraud Detection Graph Agent

Thank you for your interest in contributing to the Fraud Detection Graph Agent! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/your-username/fraud-detection.git`
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Make** your changes
5. **Test** your changes: `make test`
6. **Commit** your changes: `git commit -m 'Add amazing feature'`
7. **Push** to your branch: `git push origin feature/amazing-feature`
8. **Open** a Pull Request

## 🏗️ Development Setup

### Prerequisites
- Python 3.11+
- pip
- git

### Local Development
```bash
# Clone and setup
git clone <your-fork-url>
cd fraud-detection

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
make install

# Start development server
make run
```

### Running Tests
```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_api.py -v
```

### Code Quality
```bash
# Format code
make format

# Lint code
make lint

# Clean up
make clean
```

## 📝 Code Style

### Python
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions small and focused

### Example
```python
from typing import Dict, List, Optional

def process_transactions(
    transactions: List[Dict[str, any]], 
    threshold: float = 0.5
) -> Dict[str, float]:
    """
    Process a list of transactions and return fraud scores.
    
    Args:
        transactions: List of transaction dictionaries
        threshold: Minimum fraud score threshold
        
    Returns:
        Dictionary mapping transaction IDs to fraud scores
    """
    # Implementation here
    pass
```

## 🧪 Testing Guidelines

### Test Structure
- Place tests in the `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test function names
- Test both success and failure cases

### Example Test
```python
def test_score_batch_with_valid_data():
    """Test batch scoring with valid transaction data."""
    # Arrange
    test_data = [{"idx": 1, "amount": 1000, ...}]
    
    # Act
    result = score_batch(test_data)
    
    # Assert
    assert len(result) == 1
    assert result[0]["ring_score_7d"] > 0
```

### Test Data
- Use the provided test data files in `tests/`
- Create new test scenarios as needed
- Keep test data realistic and diverse

## 📚 Documentation

### Code Documentation
- Write clear docstrings for all functions
- Include examples in docstrings
- Document complex algorithms and business logic

### API Documentation
- Update `docs/api.md` for new endpoints
- Include request/response examples
- Document error codes and messages

### README Updates
- Update README.md for new features
- Include setup instructions for new dependencies
- Update project structure if changed

## 🔄 Pull Request Process

### Before Submitting
1. **Test** your changes thoroughly
2. **Update** documentation if needed
3. **Check** code style with `make lint`
4. **Ensure** all tests pass

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## 🐛 Bug Reports

### Bug Report Template
```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 10, Ubuntu 20.04]
- Python Version: [e.g., 3.11.0]
- Package Version: [e.g., 1.0.0]

## Additional Context
Any other relevant information
```

## 💡 Feature Requests

### Feature Request Template
```markdown
## Feature Description
Clear description of the requested feature

## Use Case
Why this feature is needed

## Proposed Solution
How you think it should work

## Alternatives Considered
Other approaches you've considered

## Additional Context
Any other relevant information
```

## 🤝 Team Collaboration

### Communication
- Use GitHub Issues for discussions
- Tag team members when relevant
- Keep conversations focused and constructive

### Code Review
- Review others' code promptly
- Provide constructive feedback
- Ask questions if something is unclear
- Suggest improvements respectfully

### Integration Points
- Coordinate with other team members (B, C, D)
- Ensure API compatibility
- Test integration scenarios

## 📋 Release Process

### Version Bumping
- Update version in `setup.py`
- Update `CHANGELOG.md`
- Tag releases in git

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped
- [ ] Release tagged

## 🆘 Getting Help

### Resources
- Check existing documentation
- Review GitHub Issues
- Ask questions in team discussions

### Contact
- Create GitHub Issues for bugs/features
- Use team communication channels
- Reach out to team leads for guidance

---

**Thank you for contributing to the Fraud Detection Graph Agent! 🚀**
