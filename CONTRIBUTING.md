# Git Commit Message Guide

## Commit Message Structure

Each commit message should generally follow this format:

```
<type>: <short summary>

[optional body]

[optional footer(s)]
```

### 1. Adding a New File

```
feat: Add user authentication module
```

### 2. Adding New Functionality

```
feat: Implement password reset functionality
```

### 3. Updating Functionality

```
refactor: Improve search algorithm efficiency
```

### 4. Fixing Bugs

```
fix: Resolve login error for special characters
```

### 5. Removing Unused Code

```
chore: Remove deprecated user profile functions
```

### 6. Updating Documentation

```
docs: Update README with new API endpoints
```

### 7. Refactoring Code (without changing functionality)

```
refactor: Simplify error handling in payment module
```

### 8. Updating Dependencies

```
chore: Update dependencies to latest versions
```

### 9. Making Performance Improvements

```
perf: Optimize image loading on homepage
```

## Pull Requests

```
feat: Add user registration API endpoint

- Implement POST /api/users/register
- Add input validation and error handling
- Create unit tests for the new endpoint

Closes #123
```

```
fix: Prevent race condition in concurrent file access

- Implement file locking mechanism
- Add timeout to prevent deadlocks
- Update relevant documentation

Bug: #456
```
