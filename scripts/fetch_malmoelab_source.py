#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import psycopg2
from psycopg2.extras import RealDictCursor


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "data" / "used_sentences.jsonl"
DEFAULT_BASE_URL = "https://malmoelab.com"
HANGUL_BASE = 0xAC00
HANGUL_LAST = 0xD7A3
INITIALS = ["g", "kk", "n", "d", "tt", "r", "m", "b", "pp", "s", "ss", "", "j", "jj", "ch", "k", "t", "p", "h"]
VOWELS = ["a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o", "wa", "wae", "oe", "yo", "u", "wo", "we", "wi", "yu", "eu", "ui", "i"]
FINALS = ["", "k", "k", "ks", "n", "nj", "nh", "t", "l", "lk", "lm", "lb", "ls", "lt", "lp", "lh", "m", "p", "ps", "t", "t", "ng", "t", "t", "k", "t", "p", "h"]


QUERY = """
WITH english_gloss AS (
  SELECT
    wt.sense_id,
    wt.translation_text,
    ROW_NUMBER() OVER (
      PARTITION BY wt.sense_id
      ORDER BY wt.is_primary DESC, wt.display_order ASC, wt.created_at ASC
    ) AS ranking
  FROM word_translations wt
  WHERE wt.target_language_code = 'en'
)
SELECT
  w.id AS word_id,
  ws.id AS sense_id,
  we.id AS example_id,
  w.word_text,
  COALESCE(NULLIF(w.romanization, ''), NULLIF(w.reading_text, '')) AS word_romanization,
  w.reading_text,
  w.romanization,
  w.part_of_speech,
  w.topik_level,
  w.difficulty_score,
  ws.definition,
  ws.definition_translated,
  ws.register_label AS sense_register_label,
  we.example_text,
  we.translation_text AS example_translation_text,
  we.translation_language_code,
  we.register_label AS example_register_label,
  eg.translation_text AS english_gloss
FROM word_examples we
JOIN word_senses ws ON ws.id = we.sense_id
JOIN words w ON w.id = ws.word_id
JOIN languages lang ON lang.id = w.language_id
LEFT JOIN english_gloss eg ON eg.sense_id = ws.id AND eg.ranking = 1
WHERE lang.code = 'ko'
  AND w.is_published = TRUE
  AND ws.is_published = TRUE
  AND we.is_published = TRUE
  AND COALESCE(we.translation_language_code, '') = 'en'
  AND COALESCE(TRIM(we.translation_text), '') <> ''
  AND we.example_text ILIKE '%%' || w.word_text || '%%'
  AND (%(word_text)s IS NULL OR w.word_text = %(word_text)s)
  AND (%(example_id)s IS NULL OR we.id = %(example_id)s)
  AND (%(topik_max)s IS NULL OR w.topik_level IS NULL OR w.topik_level <= %(topik_max)s)
ORDER BY
  CASE WHEN %(word_text)s IS NULL THEN COALESCE(w.topik_level, 99) ELSE 0 END,
  CASE WHEN %(word_text)s IS NULL THEN COALESCE(w.difficulty_score, 999) ELSE 0 END,
  we.created_at ASC
LIMIT 250
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch a MalmoeLab sentence source packet for quiz shorts.")
    parser.add_argument("--output", required=True, help="Output JSON file path for the source packet.")
    parser.add_argument("--episode-slug", required=True, help="Episode slug to write into the packet.")
    parser.add_argument("--database-url", default=os.getenv("MALMOELAB_DATABASE_URL", ""), help="Override MALMOELAB_DATABASE_URL.")
    parser.add_argument("--base-url", default=os.getenv("MALMOELAB_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    parser.add_argument("--word", default="", help="Optional exact Korean focus word.")
    parser.add_argument("--example-id", default="", help="Optional exact example id.")
    parser.add_argument("--topik-max", type=int, default=2, help="Prefer easier Korean examples.")
    parser.add_argument("--question-caption", default="Which word fits the blank?")
    parser.add_argument("--engagement-caption", default="Double tap if you know it.")
    parser.add_argument("--reveal-prefix", default="Answer")
    parser.add_argument("--cta-caption", default="Learn more at malmoelab.com")
    parser.add_argument("--title-card-title", default="말모이랩 한글공부")
    parser.add_argument("--title-card-subtitle", default="15-second fill-in-the-blank quiz")
    parser.add_argument("--reserve", action="store_true", help="Append a reserved entry to the used sentence ledger.")
    parser.add_argument("--allow-reuse", action="store_true", help="Allow selecting an already-used example if no fresh one exists.")
    return parser.parse_args()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_used_example_ids(ledger_path: Path) -> set[str]:
    if not ledger_path.exists():
        return set()
    used: set[str] = set()
    with ledger_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            example_id = str(payload.get("exampleId") or "").strip()
            if example_id:
                used.add(example_id)
    return used


def blank_sentence(sentence: str, focus_word: str) -> str:
    if focus_word not in sentence:
        return sentence
    blank = "_" * max(len(focus_word), 3)
    return sentence.replace(focus_word, blank, 1)


def append_ledger_entry(ledger_path: Path, entry: dict) -> None:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def contains_hangul(text: str) -> bool:
    return any(HANGUL_BASE <= ord(char) <= HANGUL_LAST for char in text)


def romanize_hangul_text(text: str) -> str:
    pieces: list[str] = []
    for char in text:
        code = ord(char)
        if HANGUL_BASE <= code <= HANGUL_LAST:
            syllable_index = code - HANGUL_BASE
            initial = syllable_index // 588
            vowel = (syllable_index % 588) // 28
            final = syllable_index % 28
            pieces.append(INITIALS[initial] + VOWELS[vowel] + FINALS[final])
        elif char == "_":
            pieces.append("_")
        else:
            pieces.append(char)
    return "".join(pieces)


def resolve_romanization(word_text: str, romanization: str) -> tuple[str, str, str]:
    normalized = romanization.strip()
    if not normalized:
        fallback = romanize_hangul_text(word_text)
        return (
            fallback,
            "render_fallback",
            "Stored romanization/reading was unavailable; generated fallback for render use only.",
        )
    if contains_hangul(normalized):
        fallback = romanize_hangul_text(word_text)
        return (
            fallback,
            "render_fallback",
            "Stored romanization contained Hangul; generated fallback for render use only.",
        )
    return normalized, "authoritative", ""


def select_candidate(rows: list[dict], used_example_ids: set[str], allow_reuse: bool) -> dict:
    for row in rows:
        if row["example_id"] not in used_example_ids:
            return row
    if allow_reuse and rows:
        return rows[0]
    if rows:
        raise RuntimeError("Only previously used examples matched. Retry with --allow-reuse or widen the query.")
    raise RuntimeError("No matching MalmoeLab example found for the requested criteria.")


def fetch_rows(database_url: str, word_text: str | None, example_id: str | None, topik_max: int | None) -> list[dict]:
    normalized_url = database_url.strip()
    if normalized_url.startswith("postgresql+psycopg2://"):
        parsed = urlparse(normalized_url)
        normalized_url = urlunparse(("postgresql", parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))

    with psycopg2.connect(normalized_url) as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                QUERY,
                {
                    "word_text": word_text or None,
                    "example_id": example_id or None,
                    "topik_max": topik_max,
                },
            )
            rows = cursor.fetchall()
    return [dict(row) for row in rows]


def build_packet(args: argparse.Namespace, selected: dict, ledger_path: Path, used_example_ids: set[str]) -> dict:
    answer_word = selected["word_text"]
    sentence = selected["example_text"].strip()
    romanization, romanization_source, romanization_note = resolve_romanization(answer_word, (selected.get("word_romanization") or "").strip())
    english_gloss = (selected.get("english_gloss") or "").strip()
    english_translation = (selected.get("example_translation_text") or "").strip()
    selected_at = utc_now_iso()
    blanked_sentence = blank_sentence(sentence, answer_word)
    was_previously_used = selected["example_id"] in used_example_ids
    reuse_required = was_previously_used

    return {
        "episodeSlug": args.episode_slug,
        "seriesSlug": "malmoelab-hangul-quiz",
        "contentLanguageCode": "ko",
        "learnerLanguageCode": "en",
        "narrationLanguageCode": "ko",
        "selectedAt": selected_at,
        "source": {
            "sourceType": "malmoelab.word_example",
            "languageCode": "ko",
            "baseUrl": args.base_url,
            "wordId": selected["word_id"],
            "senseId": selected["sense_id"],
            "exampleId": selected["example_id"],
            "wordText": answer_word,
            "wordRomanization": romanization,
            "wordRomanizationSource": romanization_source,
            "wordRomanizationNote": romanization_note,
            "wordReadingText": selected.get("reading_text") or "",
            "partOfSpeech": selected.get("part_of_speech") or "",
            "topikLevel": selected.get("topik_level"),
            "difficultyScore": selected.get("difficulty_score"),
            "definition": selected.get("definition") or "",
            "definitionTranslated": selected.get("definition_translated") or "",
            "englishGloss": english_gloss,
            "exampleText": sentence,
            "exampleTranslationText": english_translation,
            "exampleRegisterLabel": selected.get("example_register_label") or "",
            "senseRegisterLabel": selected.get("sense_register_label") or "",
        },
        "quiz": {
            "promptLanguageCode": "en",
            "titleCardTitle": args.title_card_title,
            "titleCardSubtitle": args.title_card_subtitle,
            "questionCaption": args.question_caption,
            "engagementCaption": args.engagement_caption,
            "revealCaption": f"{args.reveal_prefix}: {answer_word}",
            "ctaCaption": args.cta_caption,
            "blankedSentence": blanked_sentence,
            "fullSentence": sentence,
            "blankedSentenceRomanization": romanize_hangul_text(blanked_sentence),
            "fullSentenceRomanization": romanize_hangul_text(sentence),
            "answerWord": answer_word,
            "answerRomanization": romanization,
            "answerGloss": english_gloss,
            "answerTranslation": english_translation,
        },
        "dedupe": {
            "ledgerPath": str(ledger_path),
            "wasPreviouslyUsed": was_previously_used,
            "reuseRequired": reuse_required,
            "selectionStatus": "reused_existing_example" if was_previously_used else "unused_example_selected",
        },
        "ledger": {
            "path": str(ledger_path),
            "reserved": bool(args.reserve),
        },
    }


def main() -> int:
    args = parse_args()
    database_url = args.database_url.strip()
    if not database_url:
        raise SystemExit("Missing MALMOELAB_DATABASE_URL or --database-url")

    output_path = Path(args.output).resolve()
    ledger_path = Path(args.ledger).resolve()
    used_example_ids = load_used_example_ids(ledger_path)

    rows = fetch_rows(
        database_url=database_url,
        word_text=args.word.strip() or None,
        example_id=args.example_id.strip() or None,
        topik_max=args.topik_max,
    )
    selected = select_candidate(rows, used_example_ids, args.allow_reuse)
    packet = build_packet(args, selected, ledger_path, used_example_ids)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.reserve:
        append_ledger_entry(
            ledger_path,
            {
                "episodeSlug": args.episode_slug,
                "wordId": selected["word_id"],
                "senseId": selected["sense_id"],
                "exampleId": selected["example_id"],
                "sentenceText": selected["example_text"],
                "status": "reserved",
                "selectedAt": packet["selectedAt"],
            },
        )

    print(json.dumps(packet, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
