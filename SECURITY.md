# Security Policy

## Supported Versions

Teyvat Vision is currently pre-alpha software. No production release is currently supported.

## Reporting Security Issues

Security vulnerabilities should not be disclosed publicly before they have been evaluated.

Until a dedicated security reporting channel is established, use the repository maintainer's GitHub contact mechanisms for responsible disclosure.

Do not include credentials, authentication tokens, session data, or other sensitive information in public issue reports.

## Application Security Principles

Teyvat Vision is intended to operate through visible game UI state, screenshots, and normal keyboard/mouse interaction.

The core architecture should not require:

- DLL injection
- Game-memory modification
- Process-memory scanning
- Credential extraction
- Packet interception
- Private authenticated HoYoverse endpoints
- Collection of user session cookies

Any future proposal to introduce one of these mechanisms requires explicit architectural and security review before implementation.

## Secrets and Credentials

Secrets and credentials must never be committed to the repository.

Local environment files and other secret-bearing configuration are excluded from version control.

If a credential is accidentally committed, removing it from the latest revision is not sufficient. The credential must be considered compromised and rotated.

## External Services

External APIs and community services must be treated as untrusted boundaries.

Integrations should:

- Validate external responses before use.
- Define reasonable network timeouts.
- Handle unavailable services without corrupting scan results.
- Avoid exposing unnecessary user information.
- Avoid storing authentication material unless explicitly required by an approved design.
- Keep optional external services from becoming required for core offline scanning.

## Dependencies

Third-party dependencies should be deliberately selected and kept to the minimum necessary for the application.

Dependency changes should be reviewable through version control and should not introduce packages solely for functionality that can reasonably be implemented using the existing stack.

Automated dependency and security scanning may be introduced as part of the repository CI pipeline.

## Recognition Data and Diagnostics

Diagnostic captures may contain information visible in the user's Genshin Impact client.

Diagnostic data should therefore:

- Remain local by default.
- Never be uploaded automatically.
- Be clearly identified when a user chooses to share it.
- Avoid collecting unrelated screen content where practical.
- Be excluded from version control unless intentionally sanitized and approved as a test fixture.

## Security Scope

This policy applies to the Teyvat Vision source code and supporting project infrastructure.

Teyvat Vision is an independent community project and is not affiliated with, endorsed by, or sponsored by HoYoverse.