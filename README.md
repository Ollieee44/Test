# Test

Claude Code skills live in `.claude/skills/`. Claude uses them automatically when a task matches, or you can ask for one by name.

| Skill | What it does | Source |
|---|---|---|
| design-taste-frontend | Main taste skill: premium, non-generic frontend design (v2) | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) |
| design-taste-frontend-v1 | Original v1 of the taste skill | taste-skill |
| gpt-taste | Taste skill variant tuned for GPT-style models | taste-skill |
| high-end-visual-design | Soft, high-end visual style | taste-skill |
| minimalist-ui | Minimalist style | taste-skill |
| industrial-brutalist-ui | Brutalist style | taste-skill |
| stitch-design-taste | Google Stitch-compatible design rules | taste-skill |
| redesign-existing-projects | Upgrade the look of an existing site | taste-skill |
| full-output-enforcement | Stops the agent from leaving placeholder/truncated code | taste-skill |
| image-to-code | Turn design images into a website (give it mockups; it was written for Codex, which can generate images) | taste-skill |
| imagegen-frontend-web / imagegen-frontend-mobile / brandkit | Prompts for generating design reference images in an image generator | taste-skill |
| web-design-guidelines | Review UI code for design and accessibility issues ("review my UI") | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) |
| playwright-cli | Open a real browser to test and screenshot pages | [@playwright/cli](https://playwright.dev/agent-cli/skills) |

The Playwright CLI is installed automatically at the start of each Claude Code on the web session by `.claude/hooks/session-start.sh`, and `.playwright/cli.config.json` points it at the environment's pre-installed Chromium.
