# Brick Agent Usage

Use Brick whenever project context, preferences, decisions, routines, commands,
or merge-review memory may affect your work.

## Start Of Work

1. Run `./brick setup` if Brick directories, the root `brick` symlink, or Git
   merge-driver config appear incomplete.
2. Search memory before relying on assumptions:

   ```sh
   ./brick memory search "topic or task" --pretty
   ```

3. If `.agents/brick/index/brick.sqlite3` is missing or stale, run:

   ```sh
   ./brick rebuild
   ```

## Adding Memory

Do not hand-edit canonical memory files unless the user explicitly asks. Prepare
a JSON candidate and send it through Brick:

```sh
./brick memory add < .agents/brick/examples/memory-add/decision.json
```

Valid candidates need:

- `title`, `type`, `tags`, `body`, `source`, and `evidence`.
- Concrete source/evidence that lets maintainers judge trust.
- No secrets.
- No possible PII unless the user has explicitly confirmed it is public with
  `confirm_public: true`.

After a memory is accepted, rebuild search:

```sh
./brick rebuild
```

## Useful Commands

```sh
./brick memory validate --pretty
./brick memory search "release process" --limit 5 --pretty
./brick conflicts list --pretty
./brick conflicts export <conflict-id> --pretty
```

## Merge Conflicts

Brick's merge driver only resolves exact or fast-forward-safe memory cases.
When it writes a conflict report, export and inspect it before proposing a
resolution:

```sh
./brick conflicts list --pretty
./brick conflicts export <conflict-id> --pretty
```

Human review is required before writing a final merged memory when Brick reports
`required_action: human_review`.

## Examples

- `memory-add/decision.json`: valid decision candidate.
- `memory-add/command.json`: valid command candidate with structured command fields.
- `memory-add/routine.json`: valid routine candidate with steps.
- `memory-add/skill.json`: valid skill candidate with steps.
- `memory-add/blocked-unsafe.json`: unsafe example that Brick should reject.
- `memory-files/*.md`: rendered examples of canonical Markdown memory files.
