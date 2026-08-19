# ADR 0002: Use Python 3.13 as the Primary Application Runtime

- Status: Accepted
- Date: 2026-08-19

## Context

Teyvat Vision is a Windows desktop application centered on computer vision,
structured data processing, constrained recognition, validation, and
potential machine-learning inference.

The project requires a development ecosystem that supports:

- Computer vision and image processing
- Numerical operations
- Machine-learning research and training
- Production model inference
- Windows desktop application development
- Typed domain models
- Automated testing
- Static analysis
- Data-processing and dataset tooling
- Reproducible development environments

The application is expected to perform substantial experimentation during the
recognition research phase. The language and runtime should therefore support
rapid iteration without forcing the production application to depend on the
entire research and training environment.

The development machine currently has Python 3.13 and Python 3.14 available.

Python 3.13 provides a current runtime while allowing the project to avoid
unnecessarily adopting Python 3.14 before the compatibility of all required
computer-vision, inference, GUI, packaging, and development dependencies has
been established.

## Decision

Teyvat Vision will use Python 3.13 as its primary application runtime.

The project will initially declare:

`requires-python = ">=3.13,<3.14"`

The local project environment will use a repository-local virtual environment:

`.venv`

The source code will use a `src` layout with the primary Python package:

`src/teyvat_vision/`

Python source code will be type annotated. Static type checking will be part
of the normal development quality gates.

The initial development quality toolchain will include:

- pytest for automated testing
- Ruff for linting and formatting
- mypy with strict type checking

Application dependencies will not be installed or adopted merely because they
appear in the proposed technology stack.

Major runtime dependencies will be evaluated independently before becoming
architectural commitments.

This includes, but is not limited to:

- OpenCV
- NumPy
- PySide6 / Qt
- ONNX Runtime
- Pydantic
- PyTorch

Where appropriate, significant dependency or framework decisions will receive
their own ADR.

## Research and Production Separation

The production application must not require the complete machine-learning
research and training environment.

The intended model lifecycle is conceptually:

    Research / training environment
        ↓
    Trained model
        ↓
    Portable production representation
        ↓
    Production inference runtime

PyTorch is currently a candidate for research and training.

ONNX is currently a candidate for portable model representation.

ONNX Runtime is currently a candidate for production inference.

These technologies are not accepted by this ADR. They must be validated
before adoption.

This separation is intended to prevent development-only ML dependencies from
unnecessarily increasing production application size, complexity, startup
cost, or packaging difficulty.

## Dependency Management

Project dependencies will be declared through `pyproject.toml`.

Direct project dependencies must not rely solely on an undocumented local
environment or an ad hoc `pip install` history.

Dependencies should be classified according to their purpose, including:

- Production/runtime dependencies
- Development and quality tooling
- Research/training dependencies

The exact dependency-group and locking strategy will be established
separately before the dependency graph becomes substantial.

## Alternatives Considered

### Python 3.14

Python 3.14 is installed on the development system and is newer than Python
3.13.

It was not selected as the initial project runtime because Teyvat Vision
depends on several specialized ecosystems, including computer vision,
machine-learning inference, GUI frameworks, and Windows packaging.

Adopting the newest interpreter provides little project value if it narrows
dependency compatibility or complicates packaging.

Python 3.14 may be adopted later after the complete required dependency stack
has been verified against it.

### C# / .NET

C# and .NET are strong candidates for Windows desktop applications and provide
excellent Windows integration, static typing, tooling, and deployment
capabilities.

They were not selected as the primary runtime because Teyvat Vision's central
technical problem is computer vision and recognition research, where Python
provides a particularly mature and accessible ecosystem.

A future architecture could still use .NET for a component if a demonstrated
technical requirement justifies the additional cross-language complexity.

### C++

C++ provides high performance and direct access to mature computer-vision
libraries.

It was not selected as the primary application language because the expected
performance benefits do not currently justify the additional implementation
complexity and slower research iteration.

Performance-sensitive functionality may already execute in optimized native
libraries accessed from Python.

## Consequences

The project gains direct access to a mature computer-vision,
machine-learning, testing, and data-processing ecosystem.

Recognition experiments can be developed and evaluated rapidly.

The application can use optimized native libraries through Python bindings
where necessary.

Python's dynamic runtime increases the importance of disciplined type
annotations, static analysis, tests, validation, and clearly defined
interfaces.

Python packaging into a polished Windows desktop application remains a
technical risk that must be validated before release.

The project intentionally accepts that risk rather than selecting a Windows
application technology primarily for packaging convenience before the core
recognition architecture has been proven.

The Python version constraint will need deliberate review before adopting a
new minor Python version.

## Revisit Conditions

This decision should be revisited if:

- A required production dependency cannot reliably support Python 3.13.
- Windows packaging proves unsuitable for the required application experience.
- Performance measurements demonstrate that Python is a material bottleneck
  that cannot reasonably be addressed through optimized libraries or isolated
  native components.
- The architecture changes such that computer-vision and ML experimentation
  are no longer central to the application.
- Python 3.14 or a later runtime provides meaningful project benefits and the
  complete dependency stack has demonstrated support for it.