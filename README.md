# human-tone

**A cheap, low-effort skill that makes AI text sound less obviously AI, in the style you pick.**

Agents call it in one step: hand it a draft, get back plain, natural text with the usual AI tells removed. Pick **default** (neutral) or **casual** (text-message voice). No model-specific tricks, no extra tooling, very little compute: it is a short prompt plus a tiny rule checker.

> **Honest scope:** this is a style editor. It does **not** target, test against, or claim to beat GPTZero, Turnitin or any other AI detector, and it makes no promise about detector scores. If your school or workplace requires disclosing AI use, follow that.

## What it does
- Removes stock AI phrasing ("delve", "crucial", "moreover", "in conclusion", "double-edged sword"...)
- Avoids **tricolons** (exactly-three lists) and three sentences in a row opening the same way
- No em dashes, no filler openers/closers, varied sentence length
- Keeps every fact, name, number, quote and citation unchanged. Adds no typos and no fake anecdotes
- **casual** voice weaves in "though", "too", "kind of", "a lot of", "not really", "to be honest" (about 1 per 20-80 words), good for agents that send texts or chat messages

## Two skills
| Skill | Voice | Use for |
|---|---|---|
| `/human-default` | neutral, clear | emails, summaries, essays, reports |
| `/human-casual` | relaxed, conversational | text messages, DMs, chat replies |

## Examples
**Input**
> In today's fast-paced world, social media plays a crucial role in shaping how teenagers communicate. Moreover, it fosters a multifaceted landscape of connection, showcasing both opportunities and risks. Furthermore, a recent survey found that 59% of teens use it daily. It is important to note that this underscores the pivotal need for balance. In conclusion, social media is a double-edged sword.

**`/human-default`**
> Social media has changed how teenagers talk to each other. It gives them easy ways to stay in touch, and it also exposes them to real risks. One recent survey found that 59% of teens use it every day. That's a lot of time on a screen, so finding some balance matters. Used carefully, it helps. Used without thought, it can hurt.

**`/human-casual`**
> Social media has changed how teenagers talk to each other, though it's not all good. It makes it easy to stay in touch, but it's kind of risky too. One recent survey found that 59% of teens use it every day. That's a lot of time on a screen, so finding some balance matters. Used carefully it helps, and used without thought it can hurt.

*(Reference outputs from the spec; both pass the bundled checker.)*

## Install

**Claude Code / Claude agents (skill):** copy the two folders into your skills directory.
```
git clone https://github.com/sirwinstontea/human-tone
cp -r human-tone/skills/human-default human-tone/skills/human-casual ~/.claude/skills/
```
Then: `/human-casual <text>` or let an agent call it ("make this sound casual").

**Any other model or app (Grok, ChatGPT, Gemini, local):** paste `dist/humanizer-default.prompt.md` or `dist/humanizer-casual.prompt.md` as the system prompt or custom instructions, then send the text. Or call any API with that file as the system prompt at temperature 0.

## Verify output (cheap, offline, any model)
Each skill bundles a stdlib-only checker that tells you whether a text follows the rules:
```
python skills/human-casual/scripts/check.py out.txt     # exit 0 = passes, else lists violations
```
Feed the violations back to the model for one repair pass. Different models won't produce word-for-word identical text, but the rules, example and checker are identical everywhere.

## Customise
All rules live in one file: [`dist/humanizer_spec.json`](dist/humanizer_spec.json) (banned words/phrases, tricolon rule, casual markers and frequency, examples). Edit it, then regenerate the prompts and skill files from it.

## Layout
```
skills/human-default/   SKILL.md + scripts/check.py
skills/human-casual/    SKILL.md + scripts/check.py
dist/                   portable prompts for any model + the spec JSON
```

## License
MIT
