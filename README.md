# Teyvat Vision

Teyvat Vision is a ground-up, computer-vision-driven inventory scanner for Genshin Impact.

The project is designed to extract structured account data from the visible game UI using Genshin-specific visual recognition, constrained recognition, and domain validation rather than relying on general-purpose OCR as the primary recognition mechanism.

> **Project status:** Pre-alpha / architecture and feasibility phase.

## Goals

Teyvat Vision is intended to support scanning and structured representation of:

- Characters
- Weapons
- Artifacts
- Character development information
- Materials
- Equipment ownership and locations
- Relevant levels, ascensions, refinements, constellations, talents, lock states, stats, and quantities

The first mandatory export target is GOOD v3 compatibility for the Genshin Optimizer ecosystem.

## Design Principles

Teyvat Vision is being developed around several core principles:

- Correctness before scan speed
- Verified results before guessed results
- Explicit unknown states instead of fabricated defaults
- Stable machine identities instead of display strings
- Genshin-specific recognition instead of unrestricted OCR
- Resolution-independent UI geometry
- Domain validation for recognized values
- Diagnostic evidence for failed or ambiguous recognition
- Offline operation for core scanning functionality
- Pluggable external data providers and exporters

## Recognition Architecture

The intended recognition pipeline is:

    Genshin Window
        ↓
    Screen-State Detection
        ↓
    UI Anchor Detection
        ↓
    Canonical Coordinate Transform
        ↓
    ROI Extraction
        ↓
    Task-Specific Recognition
        ↓
    Raw Result + Confidence
        ↓
    Domain Validation
        ↓
    Retry / Alternate Recognition
        ↓
    Canonical Domain Model
        ↓
    Exporter

General-purpose OCR is treated as one specialized tool within the recognition system, not as the foundation of the application.

## Current Development Phase

Development is currently focused on:

1. Architecture and external data contracts
2. Canonical domain models
3. Static game-data providers
4. GOOD compatibility
5. Computer-vision feasibility testing
6. Recognition regression infrastructure

Full game automation and the desktop UI will be implemented only after the recognition and data contracts have been proven independently.

## Planned Technology Stack

The current architecture candidates include:

- Python 3.13
- OpenCV
- NumPy
- PyTorch for research and model training
- ONNX for production model interchange
- ONNX Runtime for production inference
- PySide6 / Qt 6 for the Windows desktop application
- pytest
- Ruff
- mypy

Technology choices remain subject to Architecture Decision Records and feasibility testing.

## Repository Structure

    src/                  Application source
    tests/                Automated test suites and regression fixtures
    docs/adr/             Architecture Decision Records
    docs/architecture/    Architecture documentation
    datasets/             Dataset manifests and controlled dataset metadata
    models/               Model manifests and controlled model metadata

Large datasets, trained models, and third-party assets will not be committed without an explicit storage and licensing policy.

## Compatibility

The first required external compatibility target is GOOD v3.

Export serialization will remain separate from recognition logic so additional export formats can be implemented independently.

## Safety

Teyvat Vision is intended to interact with Genshin Impact through visible UI state, screenshots, and normal keyboard/mouse input.

The default architecture does not require:

- Process memory modification
- DLL injection
- Game-memory scanning
- Packet capture
- Private authenticated HoYoverse APIs

## Testing Philosophy

Recognition behavior must be reproducible.

A recognition defect is not considered fixed until it has a regression fixture that proves the corrected behavior.

Training data and validation data must have documented provenance. Legacy scanner output is not considered ground truth unless independently verified.

## License

Teyvat Vision source code is licensed under the MIT License.

Genshin Impact, its names, characters, imagery, game assets, and related intellectual property are owned by their respective rights holders and are not covered by the Teyvat Vision MIT license.

Teyvat Vision is an independent community project and is not affiliated with, endorsed by, or sponsored by HoYoverse.