# Git Commit Message Best Practices

## Format

Use the Conventional Commits structure:

```
<type>(<scope>): <short summary>

[optional body]

[optional footer]
```

The scope is typically a ticket number (Jira, Linear, etc.):

```
fix(ZOO-123): Correct RabbitMQ binder names
feat(SCHOOL-23): Add Japanese language support
```

## Types

| Type | Use for |
|------|---------|
| `feat` | New feature or functionality |
| `fix` | Bug fix |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `docs` | Documentation only |
| `test` | Adding or fixing tests |
| `chore` | Build process, dependencies, tooling |
| `perf` | Performance improvement |
| `ci` | CI/CD configuration |

Add `!` before the colon for breaking changes: `feat(api)!: Drop support for v1 auth`

## The Seven Rules (Chris Beams)

1. Separate subject from body with a blank line
2. Limit the subject line to 50 characters
3. Capitalize the subject line
4. Do not end the subject line with a period
5. Use imperative mood - write as a command: "Fix bug" not "Fixed bug"
6. Wrap the body at 72 characters
7. Use the body to explain *what* and *why*, not *how*

**Litmus test**: the subject should complete the sentence "If applied, this commit will ___."

## Common Mistakes to Avoid

- **Too vague**: "Added more changes", "Fixed it", "Initial commit" after finishing a whole feature
- **Too detailed**: listing every file or method name - let the diff speak for itself
- **Emotional**: "Get working already!!!!!", "wgo8g7tfwo82w37fdto" - always unprofessional
- **Past tense**: "Fixed the bug" → use "Fix the bug"
- **Big-bang commits**: commit incrementally as work progresses, not once at the very end

## Examples

| Bad | Good |
|-----|------|
| `fix stuff` | `fix(AUTH-42): Redirect to login on session expiry` |
| `Added an email support to UserNotificationService by introducing emailSender() method that uses angus-mail` | `feat(NOTIF-7): Add email support for user notifications` |
| `Fix to UserNotificationIntegrationTest, BillingIntegrationTest, BaseIntegrationTest` | `fix(BILL-99): Fix failing integration tests` |
| `Initial commit` *(after completing entire project)* | Incremental commits throughout development |
