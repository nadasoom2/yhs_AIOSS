# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability, please **do not** open a public GitHub issue. Instead, please report it to the maintainers privately.

### How to Report
1. Email: [your-email@example.com] (setup in your repository)
2. GitHub Security Advisory: Use "Report a vulnerability" button if available

### What to Include
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

## Security Update Process

1. **Assessment**: We will assess the vulnerability within 2 business days
2. **Development**: A fix will be developed in a private repository
3. **Testing**: The fix will be tested thoroughly
4. **Release**: A security patch will be released with a CVE if applicable
5. **Disclosure**: Details will be disclosed after the patch is released

## Supported Versions

| Version | Status | Security Support Until |
|---------|--------|------------------------|
| 1.0.x   | Current| 2027-05-18            |
| < 1.0   | EOL    | N/A                   |

## Security Best Practices

### For Users
- Keep dependencies updated using Dependabot
- Monitor GitHub Security alerts
- Use environment variables for sensitive data (API keys, tokens)
- Never commit secrets to the repository

### For Developers
- Review Dependabot PRs promptly
- Run security scans locally: `npm audit`
- Use Snyk CLI for pre-commit checks
- Follow secure coding practices

## Dependencies Security

We use the following tools to monitor security:
- **npm audit**: Built-in Node.js security audit
- **Snyk**: Continuous vulnerability scanning
- **Dependabot**: Automated dependency updates
- **GitHub Security**: Code scanning and alerts

## Compliance

This project aims to maintain security standards and follows best practices for:
- Supply chain security
- Dependency management
- Vulnerability disclosure
- Patch management
