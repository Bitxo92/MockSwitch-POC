# GitHub Copilot Custom Instructions

## Purpose

This file provides custom instructions and guidelines for using GitHub Copilot in the demeter-frontend-template repository.

## Best Practices

- Use [Conventional Commits](https://www.conventionalcommits.org/) for all commit messages.
- Follow the project’s code style and linting rules.
- Write clear, concise, and maintainable code.
- Add comments for complex logic or important decisions.
- Update documentation and tests when making changes.

## Pull Requests

- Use the provided pull request template.
- Fill out the necessary sections, including the "Changes" area divided by commit type.
- Attach relevant screenshots or media for UI changes.

## Code Reviews

- Review code for security, performance, and readability.
- Ensure all checklist items are completed before merging.

## UI Component & Styling Guidelines

- Use [lucide-react](https://lucide.dev/) icons for all iconography.
- Use shadcn components from the `src/components/ui` folder. If a required component is missing, download or generate it before use.
- Always use Tailwind CSS for styling. If Tailwind does not provide a built-in style or animation, create custom utilities or animations in `src/index.css`.
- Always reference or create CSS variables in `src/index.css` for colors, fonts, and other design tokens. Avoid hardcoding color or font values directly in code or components.
- Always take responsive design into account. Ensure all UI components and layouts adapt well to different screen sizes and devices.
- Always stay within the design system and style guidelines defined in the project. Avoid introducing new styles or patterns that are not consistent with the existing design.
- All text content should be in Spanish, as the project is intended for a Spanish-speaking audience.

## Copilot Usage

- Use Copilot suggestions as a starting point, but always review and adapt them to fit the project’s requirements.
- Avoid committing generated code without review.

---

For questions or improvements to these instructions, open an issue or contact the repository maintainers.
